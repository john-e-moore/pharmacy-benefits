from datetime import datetime

from airflow.sdk import TaskGroup, dag, task

from pipeline.config import VENV_PYTHON

VENV_PYTHON_STR = str(VENV_PYTHON)


@dag(
    dag_id="pharmacy_benefits_pipeline",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["pharmacy_benefits"],
    default_args={"retries": 0},
)
def pharmacy_benefits_pipeline():
    @task.external_python(task_id="reset_pipeline_timestamp", python=VENV_PYTHON_STR)
    def reset_pipeline_timestamp():
        from pipeline import tasks as pipeline_tasks

        return pipeline_tasks.reset_pipeline_timestamp_task()

    with TaskGroup(group_id="generate_dimensions") as generate_dimensions:
        @task.external_python(task_id="generate_plans", python=VENV_PYTHON_STR)
        def generate_plans():
            from pipeline import tasks as pipeline_tasks

            return pipeline_tasks.generate_plans_task()

        @task.external_python(task_id="generate_drugs", python=VENV_PYTHON_STR)
        def generate_drugs():
            from pipeline import tasks as pipeline_tasks

            return pipeline_tasks.generate_drugs_task()

        @task.external_python(task_id="generate_pharmacies", python=VENV_PYTHON_STR)
        def generate_pharmacies():
            from pipeline import tasks as pipeline_tasks

            return pipeline_tasks.generate_pharmacies_task()

        @task.external_python(task_id="generate_providers", python=VENV_PYTHON_STR)
        def generate_providers():
            from pipeline import tasks as pipeline_tasks

            return pipeline_tasks.generate_providers_task()

        dim_tasks = [
            generate_plans(),
            generate_drugs(),
            generate_pharmacies(),
            generate_providers(),
        ]

    @task.external_python(task_id="generate_formulary", python=VENV_PYTHON_STR)
    def generate_formulary():
        from pipeline import tasks as pipeline_tasks

        return pipeline_tasks.generate_formulary_task()

    @task.external_python(task_id="generate_members", python=VENV_PYTHON_STR)
    def generate_members():
        from pipeline import tasks as pipeline_tasks

        return pipeline_tasks.generate_members_task()

    @task.external_python(task_id="generate_claims", python=VENV_PYTHON_STR)
    def generate_claims():
        from pipeline import tasks as pipeline_tasks

        return pipeline_tasks.generate_claims_task()

    @task.external_python(task_id="load_raw_to_snowflake", python=VENV_PYTHON_STR)
    def load_raw_to_snowflake():
        from pipeline import tasks as pipeline_tasks

        return pipeline_tasks.load_raw_to_snowflake_task()

    @task.external_python(task_id="check_source_freshness", python=VENV_PYTHON_STR)
    def check_source_freshness():
        from pipeline import tasks as pipeline_tasks

        pipeline_tasks.check_source_freshness_task()

    @task.external_python(task_id="build_staging_models", python=VENV_PYTHON_STR)
    def build_staging_models():
        from pipeline import tasks as pipeline_tasks

        pipeline_tasks.build_staging_models_task()

    @task.external_python(task_id="test_staging_models", python=VENV_PYTHON_STR)
    def test_staging_models():
        from pipeline import tasks as pipeline_tasks

        pipeline_tasks.test_staging_models_task()

    @task.external_python(task_id="build_intermediate_models", python=VENV_PYTHON_STR)
    def build_intermediate_models():
        from pipeline import tasks as pipeline_tasks

        pipeline_tasks.build_intermediate_models_task()

    @task.external_python(task_id="test_intermediate_models", python=VENV_PYTHON_STR)
    def test_intermediate_models():
        from pipeline import tasks as pipeline_tasks

        pipeline_tasks.test_intermediate_models_task()

    @task.external_python(task_id="build_marts", python=VENV_PYTHON_STR)
    def build_marts():
        from pipeline import tasks as pipeline_tasks

        pipeline_tasks.build_marts_task()

    @task.external_python(task_id="test_marts", python=VENV_PYTHON_STR)
    def test_marts():
        from pipeline import tasks as pipeline_tasks

        pipeline_tasks.test_marts_task()

    @task.external_python(task_id="run_business_validations", python=VENV_PYTHON_STR)
    def run_business_validations():
        from pipeline import tasks as pipeline_tasks

        pipeline_tasks.run_business_validations_task()

    reset = reset_pipeline_timestamp()
    formulary = generate_formulary()
    members = generate_members()
    claims = generate_claims()
    load_raw = load_raw_to_snowflake()
    freshness = check_source_freshness()
    build_stg = build_staging_models()
    test_stg = test_staging_models()
    build_int = build_intermediate_models()
    test_int = test_intermediate_models()
    build_marts_task = build_marts()
    test_marts_task = test_marts()
    biz_val = run_business_validations()

    reset >> dim_tasks
    for dim_task in dim_tasks:
        dim_task >> formulary
        dim_task >> members
    formulary >> claims
    members >> claims
    claims >> load_raw >> freshness >> build_stg >> test_stg
    test_stg >> build_int >> test_int >> build_marts_task >> test_marts_task >> biz_val


pharmacy_benefits_pipeline()
