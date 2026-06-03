import sys
from datetime import timedelta
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from random import choice, seed

from synthetic.common import pipeline_timestamp, setup_logging, write_csv
from synthetic.constants import (
    MEMBER_COUNT,
    PLAN_COUNT,
    RANDOM_SEED,
    TERMINATED_MEMBER_COUNT,
    US_STATES,
)

logger = setup_logging("generate_synthetic_members")

try:
    seed(RANDOM_SEED)
    logger.info("Starting synthetic members generation")

    now = pipeline_timestamp()
    members = []
    terminated_ids = set(range(MEMBER_COUNT - TERMINATED_MEMBER_COUNT + 1, MEMBER_COUNT + 1))

    for member_id in range(1, MEMBER_COUNT + 1):
        plan_id = ((member_id - 1) % PLAN_COUNT) + 1
        is_terminated = member_id in terminated_ids
        eligibility_start = (now - timedelta(days=90)).date()
        eligibility_end = (
            (now - timedelta(days=10)).date().isoformat()
            if is_terminated
            else "2099-12-31"
        )

        members.append(
            {
                "member_id": member_id,
                "plan_id": plan_id,
                "member_status": "terminated" if is_terminated else "active",
                "state": choice(US_STATES),
                "eligibility_start_date": eligibility_start.isoformat(),
                "eligibility_end_date": eligibility_end,
                "loaded_at": now.isoformat(),
            }
        )

    output_path = write_csv(pd.DataFrame(members), "members.csv")

    logger.info(
        "Synthetic members generation complete | rows=%s | output_path=%s",
        len(members),
        output_path,
    )
    print(f"Wrote {len(members)} rows to {output_path}")

except Exception:
    logger.exception("Synthetic members generation failed")
    raise
