import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

OUT_DIR = Path("data/raw")
LOG_DIR = Path("logs")
TIMESTAMP_FILE = OUT_DIR / ".pipeline_timestamp"

OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logging(name: str) -> logging.Logger:
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            filename=LOG_DIR / "pipeline.log",
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        )
    return logging.getLogger(name)


def pipeline_timestamp() -> datetime:
    if TIMESTAMP_FILE.exists():
        return datetime.fromisoformat(TIMESTAMP_FILE.read_text().strip())
    now = datetime.now(timezone.utc)
    TIMESTAMP_FILE.write_text(now.isoformat())
    return now


def reset_pipeline_timestamp() -> datetime:
    if TIMESTAMP_FILE.exists():
        TIMESTAMP_FILE.unlink()
    return pipeline_timestamp()


def write_csv(df: pd.DataFrame, filename: str) -> Path:
    output_path = OUT_DIR / filename
    df.to_csv(output_path, index=False)
    return output_path


def read_required_csv(filename: str, generator_hint: str) -> pd.DataFrame:
    path = OUT_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"{path} does not exist. Run {generator_hint} first."
        )
    return pd.read_csv(path)


def validate_claims_integrity(claims_df: pd.DataFrame, members_df: pd.DataFrame,
                              drugs_df: pd.DataFrame, pharmacies_df: pd.DataFrame,
                              formulary_df: pd.DataFrame) -> None:
    member_ids = set(members_df["member_id"])
    drug_ids = set(drugs_df["drug_id"])
    pharmacy_ids = set(pharmacies_df["pharmacy_id"])
    ndc_by_drug = dict(zip(drugs_df["drug_id"], drugs_df["ndc_code"]))
    member_plan = dict(zip(members_df["member_id"], members_df["plan_id"]))
    formulary_pairs = set(zip(formulary_df["plan_id"], formulary_df["drug_id"]))

    for _, row in claims_df.iterrows():
        if row["member_id"] not in member_ids:
            raise ValueError(f"Orphan member_id: {row['member_id']}")
        if row["drug_id"] not in drug_ids:
            raise ValueError(f"Orphan drug_id: {row['drug_id']}")
        if row["pharmacy_id"] not in pharmacy_ids:
            raise ValueError(f"Orphan pharmacy_id: {row['pharmacy_id']}")
        if row["ndc_code"] != ndc_by_drug[row["drug_id"]]:
            raise ValueError(
                f"NDC mismatch for drug_id {row['drug_id']}: "
                f"{row['ndc_code']} != {ndc_by_drug[row['drug_id']]}"
            )
        if row["plan_id"] != member_plan[row["member_id"]]:
            raise ValueError(
                f"plan_id {row['plan_id']} does not match member {row['member_id']} plan"
            )
        if (row["plan_id"], row["drug_id"]) not in formulary_pairs:
            raise ValueError(
                f"Drug {row['drug_id']} not on formulary for plan {row['plan_id']}"
            )
        if row["claim_status"] == "rejected" and (row["plan_paid"] != 0 or row["member_copay"] != 0):
            raise ValueError(f"Rejected claim {row['claim_id']} has non-zero payment amounts")


def ensure_scripts_importable() -> None:
    scripts_dir = Path(__file__).resolve().parent.parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
