import sys
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from random import choice, randint, seed, uniform

from synthetic.common import (
    pipeline_timestamp,
    read_required_csv,
    setup_logging,
    validate_claims_integrity,
    write_csv,
)
from synthetic.constants import CLAIM_COUNT, CLAIM_STATUSES, DAYS_SUPPLY_OPTIONS, RANDOM_SEED

logger = setup_logging("generate_synthetic_claims")

try:
    seed(RANDOM_SEED)
    logger.info("Starting synthetic claims generation")

    members_df = read_required_csv("members.csv", "scripts/generate_synthetic_members.py")
    drugs_df = read_required_csv("drugs.csv", "scripts/generate_synthetic_drugs.py")
    pharmacies_df = read_required_csv("pharmacies.csv", "scripts/generate_synthetic_pharmacies.py")
    formulary_df = read_required_csv("formulary.csv", "scripts/generate_synthetic_formulary.py")

    now = pipeline_timestamp()
    active_members = members_df[members_df["member_status"] == "active"]
    pharmacy_ids = pharmacies_df["pharmacy_id"].tolist()
    ndc_by_drug = dict(zip(drugs_df["drug_id"], drugs_df["ndc_code"]))

    drugs_by_plan = {}
    for plan_id, group in formulary_df.groupby("plan_id"):
        drugs_by_plan[int(plan_id)] = group["drug_id"].tolist()

    claims = []

    for _ in range(CLAIM_COUNT):
        member = active_members.iloc[choice(range(len(active_members)))]
        member_id = int(member["member_id"])
        plan_id = int(member["plan_id"])
        drug_id = int(choice(drugs_by_plan[plan_id]))
        pharmacy_id = int(choice(pharmacy_ids))
        claim_status = choice(CLAIM_STATUSES)

        eligibility_start = datetime.fromisoformat(str(member["eligibility_start_date"])).date()
        eligibility_end = datetime.fromisoformat(str(member["eligibility_end_date"])).date()
        recent_window_start = max(eligibility_start, (now - timedelta(days=30)).date())
        fill_window_days = max((eligibility_end - recent_window_start).days, 0)
        fill_date = recent_window_start + timedelta(days=randint(0, fill_window_days))

        ingredient_cost = round(uniform(10, 500), 2)
        dispensing_fee = round(uniform(1, 15), 2)

        if claim_status == "rejected":
            member_copay = 0.0
            plan_paid = 0.0
        else:
            member_copay = round(uniform(0, 50), 2)
            plan_paid = round(max(ingredient_cost + dispensing_fee - member_copay, 0), 2)

        claims.append(
            {
                "claim_id": str(uuid4()),
                "member_id": member_id,
                "drug_id": drug_id,
                "pharmacy_id": pharmacy_id,
                "plan_id": plan_id,
                "ndc_code": ndc_by_drug[drug_id],
                "claim_status": claim_status,
                "fill_date": fill_date.isoformat(),
                "days_supply": choice(DAYS_SUPPLY_OPTIONS),
                "quantity": choice(DAYS_SUPPLY_OPTIONS),
                "ingredient_cost": ingredient_cost,
                "dispensing_fee": dispensing_fee,
                "member_copay": member_copay,
                "plan_paid": plan_paid,
                "loaded_at": now.isoformat(),
            }
        )

    df = pd.DataFrame(claims)
    validate_claims_integrity(df, members_df, drugs_df, pharmacies_df, formulary_df)
    output_path = write_csv(df, "claims.csv")

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
