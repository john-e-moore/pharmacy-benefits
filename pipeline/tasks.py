from pipeline import generators
from pipeline.dbt_runner import run_dbt
from pipeline.loader import load_all_raw_tables
from pipeline.synthetic.common import reset_pipeline_timestamp


def reset_pipeline_timestamp_task() -> str:
    ts = reset_pipeline_timestamp()
    return ts.isoformat()


def generate_plans_task() -> dict:
    return generators.generate_plans()


def generate_drugs_task() -> dict:
    return generators.generate_drugs()


def generate_pharmacies_task() -> dict:
    return generators.generate_pharmacies()


def generate_providers_task() -> dict:
    return generators.generate_providers()


def generate_formulary_task() -> dict:
    return generators.generate_formulary()


def generate_members_task() -> dict:
    return generators.generate_members()


def generate_claims_task() -> dict:
    return generators.generate_claims()


def load_raw_to_snowflake_task() -> dict:
    return load_all_raw_tables()


def check_source_freshness_task() -> None:
    run_dbt("source", "freshness")


def build_staging_models_task() -> None:
    run_dbt("run", select="path:models/staging")


def test_staging_models_task() -> None:
    run_dbt("test", select="path:models/staging")


def build_intermediate_models_task() -> None:
    run_dbt("run", select="path:models/intermediate")


def test_intermediate_models_task() -> None:
    run_dbt("test", select="path:models/intermediate")


def build_marts_task() -> None:
    run_dbt("run", select="path:models/marts")


def test_marts_task() -> None:
    run_dbt("test", select="path:models/marts")


def run_business_validations_task() -> None:
    run_dbt("test", select="path:tests")
