# Start airflow standalone (restart if already running so env vars take effect)
export AIRFLOW__CORE__DAGS_FOLDER=/home/john/pharmacy-benefits/dags
export AIRFLOW__CORE__LOAD_EXAMPLES=False
export PYTHONPATH=/home/john/pharmacy-benefits
uvx apache-airflow standalone

# Open local UI
# http://localhost:8080
#
# Verify:
#   airflow dags details pharmacy_benefits_pipeline
#   airflow tasks list pharmacy_benefits_pipeline
# Trigger manually from the UI (DAG is unscheduled).
