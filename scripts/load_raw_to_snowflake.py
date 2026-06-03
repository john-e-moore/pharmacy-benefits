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
DATABASE = "PHARMACY_BENEFITS_RAW"

REQUIRED_ENV_VARS = [
    "SNOWFLAKE_ACCOUNT",
    "SNOWFLAKE_USER",
    "SNOWFLAKE_PASSWORD",
]

RAW_TABLES = [
    {
        "csv": "plans.csv",
        "schema": "PLANS",
        "table": "RAW_PLANS",
        "generator": "scripts/generate_synthetic_plans.py",
        "columns": ["plan_id", "plan_name", "plan_type", "loaded_at"],
        "ddl": """
            CREATE TABLE IF NOT EXISTS RAW_PLANS (
                plan_id NUMBER,
                plan_name STRING,
                plan_type STRING,
                loaded_at TIMESTAMP_TZ
            )
        """,
    },
    {
        "csv": "drugs.csv",
        "schema": "DRUGS",
        "table": "RAW_DRUGS",
        "generator": "scripts/generate_synthetic_drugs.py",
        "columns": [
            "drug_id", "ndc_code", "drug_name", "therapeutic_class",
            "brand_generic", "loaded_at",
        ],
        "ddl": """
            CREATE TABLE IF NOT EXISTS RAW_DRUGS (
                drug_id NUMBER,
                ndc_code STRING,
                drug_name STRING,
                therapeutic_class STRING,
                brand_generic STRING,
                loaded_at TIMESTAMP_TZ
            )
        """,
    },
    {
        "csv": "pharmacies.csv",
        "schema": "PHARMACIES",
        "table": "RAW_PHARMACIES",
        "generator": "scripts/generate_synthetic_pharmacies.py",
        "columns": [
            "pharmacy_id", "pharmacy_name", "ncpdp_id", "state",
            "network_status", "loaded_at",
        ],
        "ddl": """
            CREATE TABLE IF NOT EXISTS RAW_PHARMACIES (
                pharmacy_id NUMBER,
                pharmacy_name STRING,
                ncpdp_id STRING,
                state STRING,
                network_status STRING,
                loaded_at TIMESTAMP_TZ
            )
        """,
    },
    {
        "csv": "members.csv",
        "schema": "MEMBERS",
        "table": "RAW_MEMBERS",
        "generator": "scripts/generate_synthetic_members.py",
        "columns": [
            "member_id", "plan_id", "member_status", "state",
            "eligibility_start_date", "eligibility_end_date", "loaded_at",
        ],
        "ddl": """
            CREATE TABLE IF NOT EXISTS RAW_MEMBERS (
                member_id NUMBER,
                plan_id NUMBER,
                member_status STRING,
                state STRING,
                eligibility_start_date DATE,
                eligibility_end_date DATE,
                loaded_at TIMESTAMP_TZ
            )
        """,
    },
    {
        "csv": "providers.csv",
        "schema": "PROVIDERS",
        "table": "RAW_PROVIDERS",
        "generator": "scripts/generate_synthetic_providers.py",
        "columns": [
            "provider_id", "npi", "provider_last_name", "specialty", "state", "loaded_at",
        ],
        "ddl": """
            CREATE TABLE IF NOT EXISTS RAW_PROVIDERS (
                provider_id NUMBER,
                npi STRING,
                provider_last_name STRING,
                specialty STRING,
                state STRING,
                loaded_at TIMESTAMP_TZ
            )
        """,
    },
    {
        "csv": "formulary.csv",
        "schema": "REFERENCE",
        "table": "RAW_FORMULARY",
        "generator": "scripts/generate_synthetic_formulary.py",
        "columns": [
            "plan_id", "drug_id", "formulary_tier", "prior_auth_required", "loaded_at",
        ],
        "ddl": """
            CREATE TABLE IF NOT EXISTS RAW_FORMULARY (
                plan_id NUMBER,
                drug_id NUMBER,
                formulary_tier NUMBER,
                prior_auth_required BOOLEAN,
                loaded_at TIMESTAMP_TZ
            )
        """,
    },
    {
        "csv": "claims.csv",
        "schema": "CLAIMS",
        "table": "RAW_CLAIMS",
        "generator": "scripts/generate_synthetic_claims.py",
        "columns": [
            "claim_id", "member_id", "drug_id", "pharmacy_id", "plan_id", "ndc_code",
            "claim_status", "fill_date", "days_supply", "quantity", "ingredient_cost",
            "dispensing_fee", "member_copay", "plan_paid", "loaded_at",
        ],
        "ddl": """
            CREATE TABLE IF NOT EXISTS RAW_CLAIMS (
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
        """,
    },
]


def load_table(conn, table_config: dict) -> int:
    csv_path = RAW_DIR / table_config["csv"]
    schema = table_config["schema"]
    table_name = table_config["table"]
    expected_columns = table_config["columns"]

    if not csv_path.exists():
        raise FileNotFoundError(
            f"{csv_path} does not exist. Run {table_config['generator']} first."
        )

    with conn.cursor() as cur:
        cur.execute(f"USE SCHEMA {schema}")
        logger.info(
            "Creating table if not exists | table=%s.%s.%s",
            DATABASE, schema, table_name,
        )
        cur.execute(table_config["ddl"])
        cur.execute(f"TRUNCATE TABLE {table_name}")

    logger.info("Reading CSV | path=%s", csv_path)
    df = pd.read_csv(csv_path)

    missing_columns = sorted(set(expected_columns) - set(df.columns))
    if missing_columns:
        raise RuntimeError(f"{csv_path} is missing expected columns: {missing_columns}")

    df = df[expected_columns]
    df.columns = [col.upper() for col in df.columns]

    logger.info(
        "Loading rows to Snowflake | rows=%s | table=%s.%s.%s",
        len(df), DATABASE, schema, table_name,
    )

    success, nchunks, nrows, output = write_pandas(
        conn=conn,
        df=df,
        table_name=table_name,
        database=DATABASE,
        schema=schema,
        quote_identifiers=False,
    )

    if not success:
        raise RuntimeError(f"Snowflake load failed for {table_name}: {output}")

    logger.info(
        "Raw load complete | rows_loaded=%s | chunks=%s | table=%s.%s.%s",
        nrows, nchunks, DATABASE, schema, table_name,
    )
    print(f"Loaded {nrows} rows into {DATABASE}.{schema}.{table_name}")
    return nrows


conn = None

try:
    logger.info("Starting raw data load to Snowflake")

    missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing_vars:
        raise RuntimeError(f"Missing required environment variables: {missing_vars}")

    role = os.getenv("SNOWFLAKE_ROLE", "DBT_DEV_ROLE")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "DBT_DEV_WH")

    logger.info(
        "Connecting to Snowflake | account=%s | user=%s | role=%s | warehouse=%s | database=%s",
        os.environ["SNOWFLAKE_ACCOUNT"],
        os.environ["SNOWFLAKE_USER"],
        role,
        warehouse,
        DATABASE,
    )

    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=role,
        warehouse=warehouse,
        database=DATABASE,
    )

    logger.info("Snowflake connection established")

    with conn.cursor() as cur:
        cur.execute(f"USE DATABASE {DATABASE}")

    for table_config in RAW_TABLES:
        load_table(conn, table_config)

    logger.info("All raw tables loaded successfully")

except Exception:
    logger.exception("Raw data load failed")
    raise

finally:
    if conn is not None:
        conn.close()
        logger.info("Snowflake connection closed")
