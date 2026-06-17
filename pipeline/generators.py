from datetime import datetime, timedelta
from random import choice, randint, sample, seed, uniform
from uuid import uuid4

import pandas as pd

from pipeline.synthetic.common import (
    pipeline_timestamp,
    read_required_csv,
    setup_logging,
    validate_claims_integrity,
    write_csv,
)
from pipeline.synthetic.constants import (
    CLAIM_COUNT,
    CLAIM_STATUSES,
    DAYS_SUPPLY_OPTIONS,
    DRUG_CATALOG,
    DRUG_COUNT,
    MEMBER_COUNT,
    OUT_OF_NETWORK_PHARMACY_COUNT,
    PHARMACY_COUNT,
    PLAN_COUNT,
    PLAN_NAMES,
    PLAN_TYPES,
    PROVIDER_COUNT,
    RANDOM_SEED,
    SPECIALTIES,
    TERMINATED_MEMBER_COUNT,
    US_STATES,
)

logger = setup_logging("pipeline.generators")


def _write_result(rows: list, filename: str, label: str) -> dict:
    output_path = write_csv(pd.DataFrame(rows), filename)
    logger.info(
        "%s complete | rows=%s | output_path=%s",
        label,
        len(rows),
        output_path,
    )
    return {"rows": len(rows), "output_path": str(output_path)}


def generate_plans() -> dict:
    seed(RANDOM_SEED)
    logger.info("Starting synthetic plans generation")
    now = pipeline_timestamp()
    plans = [
        {
            "plan_id": plan_id,
            "plan_name": PLAN_NAMES[plan_id - 1],
            "plan_type": PLAN_TYPES[plan_id - 1],
            "loaded_at": now.isoformat(),
        }
        for plan_id in range(1, PLAN_COUNT + 1)
    ]
    return _write_result(plans, "plans.csv", "Synthetic plans generation")


def generate_drugs() -> dict:
    seed(RANDOM_SEED)
    logger.info("Starting synthetic drugs generation")
    now = pipeline_timestamp()
    drugs = [
        {
            "drug_id": drug_id,
            "ndc_code": drug["ndc_code"],
            "drug_name": drug["drug_name"],
            "therapeutic_class": drug["therapeutic_class"],
            "brand_generic": drug["brand_generic"],
            "loaded_at": now.isoformat(),
        }
        for drug_id, drug in enumerate(DRUG_CATALOG[:DRUG_COUNT], start=1)
    ]
    return _write_result(drugs, "drugs.csv", "Synthetic drugs generation")


def generate_pharmacies() -> dict:
    seed(RANDOM_SEED)
    logger.info("Starting synthetic pharmacies generation")
    now = pipeline_timestamp()
    out_of_network_ids = set(
        range(PHARMACY_COUNT - OUT_OF_NETWORK_PHARMACY_COUNT + 1, PHARMACY_COUNT + 1)
    )
    pharmacies = []
    for pharmacy_id in range(1, PHARMACY_COUNT + 1):
        network_status = (
            "out_of_network" if pharmacy_id in out_of_network_ids else "in_network"
        )
        pharmacies.append(
            {
                "pharmacy_id": pharmacy_id,
                "pharmacy_name": f"Pharmacy_{pharmacy_id:03d}",
                "ncpdp_id": f"{1000000 + pharmacy_id}",
                "state": choice(US_STATES),
                "network_status": network_status,
                "loaded_at": now.isoformat(),
            }
        )
    return _write_result(pharmacies, "pharmacies.csv", "Synthetic pharmacies generation")


def generate_providers() -> dict:
    seed(RANDOM_SEED)
    logger.info("Starting synthetic providers generation")
    now = pipeline_timestamp()
    providers = [
        {
            "provider_id": provider_id,
            "npi": f"{1000000000 + provider_id}",
            "provider_last_name": f"Provider_{provider_id:03d}",
            "specialty": choice(SPECIALTIES),
            "state": choice(US_STATES),
            "loaded_at": now.isoformat(),
        }
        for provider_id in range(1, PROVIDER_COUNT + 1)
    ]
    return _write_result(providers, "providers.csv", "Synthetic providers generation")


def generate_formulary() -> dict:
    seed(RANDOM_SEED)
    logger.info("Starting synthetic formulary generation")
    drugs_df = read_required_csv("drugs.csv", "generate_drugs")
    read_required_csv("plans.csv", "generate_plans")
    now = pipeline_timestamp()
    formulary = []
    all_drug_ids = list(range(1, DRUG_COUNT + 1))
    brand_drugs = set(drugs_df.loc[drugs_df["brand_generic"] == "brand", "drug_id"])

    for plan_id in range(1, PLAN_COUNT + 1):
        covered_drug_ids = sample(all_drug_ids, randint(18, 22))
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
    return _write_result(formulary, "formulary.csv", "Synthetic formulary generation")


def generate_members() -> dict:
    seed(RANDOM_SEED)
    logger.info("Starting synthetic members generation")
    now = pipeline_timestamp()
    terminated_ids = set(
        range(MEMBER_COUNT - TERMINATED_MEMBER_COUNT + 1, MEMBER_COUNT + 1)
    )
    members = []
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
    return _write_result(members, "members.csv", "Synthetic members generation")


def generate_claims() -> dict:
    seed(RANDOM_SEED)
    logger.info("Starting synthetic claims generation")
    members_df = read_required_csv("members.csv", "generate_members")
    drugs_df = read_required_csv("drugs.csv", "generate_drugs")
    pharmacies_df = read_required_csv("pharmacies.csv", "generate_pharmacies")
    formulary_df = read_required_csv("formulary.csv", "generate_formulary")

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

        eligibility_start = datetime.fromisoformat(
            str(member["eligibility_start_date"])
        ).date()
        eligibility_end = datetime.fromisoformat(
            str(member["eligibility_end_date"])
        ).date()
        recent_window_start = max(eligibility_start, (now - timedelta(days=30)).date())
        fill_window_days = max((eligibility_end - recent_window_start).days, 0)
        fill_date = min(
            recent_window_start + timedelta(days=randint(0, fill_window_days)),
            now.date(),
        )

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
    return {"rows": len(df), "output_path": str(output_path)}
