import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from random import choice, randint, seed, uniform
from uuid import uuid4

import pandas as pd


LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "pipeline.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("generate_synthetic_claims")

OUT_DIR = Path("data/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)

seed()

now = datetime.now(timezone.utc)

claim_statuses = ["paid", "rejected", "reversed"]
ndc_codes = [
    "00002-0800-01",
    "00003-0293-20",
    "00004-0802-85",
    "00006-4095-31",
    "00007-4888-13",
]

claims = []

try:
    logger.info("Starting synthetic claims generation")

    for _ in range(100):
        ingredient_cost = round(uniform(10, 500), 2)
        dispensing_fee = round(uniform(1, 15), 2)
        member_copay = round(uniform(0, 50), 2)
        plan_paid = round(max(ingredient_cost + dispensing_fee - member_copay, 0), 2)

        claims.append(
            {
                "claim_id": str(uuid4()),
                "member_id": randint(1, 50),
                "drug_id": randint(1, 25),
                "pharmacy_id": randint(1, 10),
                "plan_id": randint(1, 5),
                "ndc_code": choice(ndc_codes),
                "claim_status": choice(claim_statuses),
                "fill_date": (now - timedelta(days=randint(0, 30))).date().isoformat(),
                "days_supply": choice([30, 60, 90]),
                "quantity": choice([30, 60, 90]),
                "ingredient_cost": ingredient_cost,
                "dispensing_fee": dispensing_fee,
                "member_copay": member_copay,
                "plan_paid": plan_paid,
                "loaded_at": now.isoformat(),
            }
        )

    df = pd.DataFrame(claims)
    output_path = OUT_DIR / "claims.csv"
    df.to_csv(output_path, index=False)

    logger.info(
        "Synthetic claims generation complete | rows=%s | output_path=%s | loaded_at=%s",
        len(df),
        output_path,
        now.isoformat(),
    )

    print(f"Wrote {len(df)} rows to {output_path}")

except Exception:
    logger.exception("Synthetic claims generation failed")
    raise