#!/bin/bash

set -e

cd "$(dirname "$0")/.."

rm -f data/raw/.pipeline_timestamp

python scripts/generate_synthetic_plans.py
python scripts/generate_synthetic_drugs.py
python scripts/generate_synthetic_pharmacies.py
python scripts/generate_synthetic_providers.py
python scripts/generate_synthetic_formulary.py
python scripts/generate_synthetic_members.py
python scripts/generate_synthetic_claims.py
python scripts/load_raw_to_snowflake.py

dbt source freshness
dbt build --target dev
