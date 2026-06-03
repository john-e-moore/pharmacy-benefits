import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from random import seed

from synthetic.common import pipeline_timestamp, setup_logging, write_csv
from synthetic.constants import PLAN_COUNT, PLAN_NAMES, PLAN_TYPES, RANDOM_SEED

logger = setup_logging("generate_synthetic_plans")

try:
    seed(RANDOM_SEED)
    logger.info("Starting synthetic plans generation")

    now = pipeline_timestamp()
    plans = []

    for plan_id in range(1, PLAN_COUNT + 1):
        plans.append(
            {
                "plan_id": plan_id,
                "plan_name": PLAN_NAMES[plan_id - 1],
                "plan_type": PLAN_TYPES[plan_id - 1],
                "loaded_at": now.isoformat(),
            }
        )

    output_path = write_csv(pd.DataFrame(plans), "plans.csv")

    logger.info(
        "Synthetic plans generation complete | rows=%s | output_path=%s",
        len(plans),
        output_path,
    )
    print(f"Wrote {len(plans)} rows to {output_path}")

except Exception:
    logger.exception("Synthetic plans generation failed")
    raise
