#!/bin/bash

set -e

python scripts/generate_synthetic_claims.py
python scripts/load_raw_to_snowflake.py

dbt source freshness
dbt build --target dev