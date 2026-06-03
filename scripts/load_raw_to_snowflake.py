import logging
import os
from pathlib import Path

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from snowflake.connector.pandas_tools import write_pandas


LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("load_raw_to_snowflake")

load_dotenv()

RAW_DIR = Path("data/raw")
CLAIMS_CSV = RAW_DIR / "claims.csv"

REQUIRED_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
]

expected_columns = [
    "claim_id",
    "member_id",
    "drug_id",
    "pharmacy_id",
    "plan_id",
    "ndc_code",
    "claim_status",
    "fill_date",
    "days_supply",
    "quantity",
    "ingredient_cost",
    "dispensing_fee",
    "member_copay",
    "plan_paid",
    "loaded_at",
]

conn = None

try:
    logger.info("Starting raw claims load to Snowflake")

    missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing_vars:
        raise RuntimeError(f"Missing required environment variables: {missing_vars}")

    if not CLAIMS_CSV.exists():
        raise FileNotFoundError(
            f"{CLAIMS_CSV} does not exist. Run scripts/generate_synthetic_claims.py first."
        )

    role = os.getenv("SNOWFLAKE_ROLE", "DBT_DEV_ROLE")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "DBT_DEV_WH")
    database = "PHARMACY_BENEFITS_RAW"
    schema = "CLAIMS"
    table_name = "RAW_CLAIMS"

    logger.info(
        "Connecting to Snowflake | account=%s | user=%s | role=%s | warehouse=%s | database=%s | schema=%s",
        os.environ["SNOWFLAKE_ACCOUNT"],
        os.environ["SNOWFLAKE_USER"],
        role,
        warehouse,
        database,
        schema,
    )

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=role,
        warehouse=warehouse,
        database=database,
        schema=schema,
    )

    logger.info("Snowflake connection established")

    with conn.cursor() as cur:
        cur.execute(f"USE DATABASE {database}")
        cur.execute(f"USE SCHEMA {schema}")

        logger.info("Creating table if not exists | table=%s.%s.%s", database, schema, table_name)

        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                claim_id STRING,
                member_id NUMBER,
                drug_id NUMBER,
                pharmacy_id NUMBER,
                plan_id NUMBER,
                ndc_code STRING,
                claim_status STRING,
                fill_date DATE,
                days_supply NUMBER,
                quantity NUMBER,
                ingredient_cost NUMBER(10, 2),
                dispensing_fee NUMBER(10, 2),
                member_copay NUMBER(10, 2),
                plan_paid NUMBER(10, 2),
                loaded_at TIMESTAMP_TZ
            )
            """
        )

    logger.info("Reading CSV | path=%s", CLAIMS_CSV)

    df = pd.read_csv(CLAIMS_CSV)

    missing_columns = sorted(set(expected_columns) - set(df.columns))
    if missing_columns:
        raise RuntimeError(f"CSV is missing expected columns: {missing_columns}")

    df = df[expected_columns]
    df.columns = [col.upper() for col in df.columns]

    logger.info("Loading rows to Snowflake | rows=%s | table=%s.%s.%s", len(df), database, schema, table_name)

    success, nchunks, nrows, output = write_pandas(
        conn=conn,
        df=df,
        table_name=table_name,
        database=database,
        schema=schema,
        quote_identifiers=False,
    )

    if not success:
        raise RuntimeError(f"Snowflake load failed: {output}")

    logger.info(
        "Raw claims load complete | rows_loaded=%s | chunks=%s | table=%s.%s.%s",
        nrows,
        nchunks,
        database,
        schema,
        table_name,
    )

    print(f"Loaded {nrows} rows into {database}.{schema}.{table_name}")

except Exception:
    logger.exception("Raw claims load failed")
    raise

finally:
    if conn is not None:
        conn.close()
        logger.info("Snowflake connection closed")