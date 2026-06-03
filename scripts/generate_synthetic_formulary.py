import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from random import randint, sample, seed

from synthetic.common import pipeline_timestamp, read_required_csv, setup_logging, write_csv
from synthetic.constants import DRUG_COUNT, PLAN_COUNT, RANDOM_SEED

logger = setup_logging("generate_synthetic_formulary")

try:
    seed(RANDOM_SEED)
    logger.info("Starting synthetic formulary generation")

    drugs_df = read_required_csv("drugs.csv", "scripts/generate_synthetic_drugs.py")
    read_required_csv("plans.csv", "scripts/generate_synthetic_plans.py")

    now = pipeline_timestamp()
    formulary = []
    all_drug_ids = list(range(1, DRUG_COUNT + 1))
    brand_drugs = set(drugs_df.loc[drugs_df["brand_generic"] == "brand", "drug_id"])

    for plan_id in range(1, PLAN_COUNT + 1):
        covered_count = randint(18, 22)
        covered_drug_ids = sample(all_drug_ids, covered_count)

        for drug_id in covered_drug_ids:
            tier = randint(1, 4)
            is_brand = drug_id in brand_drugs
            prior_auth_required = tier == 4 or (is_brand and randint(1, 100) <= 25)

            formulary.append(
                {
                    "plan_id": plan_id,
                    "drug_id": drug_id,
                    "formulary_tier": tier,
                    "prior_auth_required": prior_auth_required,
                    "loaded_at": now.isoformat(),
                }
            )

    output_path = write_csv(pd.DataFrame(formulary), "formulary.csv")

    logger.info(
        "Synthetic formulary generation complete | rows=%s | output_path=%s",
        len(formulary),
        output_path,
    )
    print(f"Wrote {len(formulary)} rows to {output_path}")

except Exception:
    logger.exception("Synthetic formulary generation failed")
    raise
