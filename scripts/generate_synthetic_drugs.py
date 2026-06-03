import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from random import seed

from synthetic.common import pipeline_timestamp, setup_logging, write_csv
from synthetic.constants import DRUG_CATALOG, DRUG_COUNT, RANDOM_SEED

logger = setup_logging("generate_synthetic_drugs")

try:
    seed(RANDOM_SEED)
    logger.info("Starting synthetic drugs generation")

    now = pipeline_timestamp()
    drugs = []

    for drug_id, drug in enumerate(DRUG_CATALOG[:DRUG_COUNT], start=1):
        drugs.append(
            {
                "drug_id": drug_id,
                "ndc_code": drug["ndc_code"],
                "drug_name": drug["drug_name"],
                "therapeutic_class": drug["therapeutic_class"],
                "brand_generic": drug["brand_generic"],
                "loaded_at": now.isoformat(),
            }
        )

    output_path = write_csv(pd.DataFrame(drugs), "drugs.csv")

    logger.info(
        "Synthetic drugs generation complete | rows=%s | output_path=%s",
        len(drugs),
        output_path,
    )
    print(f"Wrote {len(drugs)} rows to {output_path}")

except Exception:
    logger.exception("Synthetic drugs generation failed")
    raise
