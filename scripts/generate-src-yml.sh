#!/bin/bash

set -e

dbt run-operation generate_source --args '{"schema_name": "claims", "database_name": "pharmacy_benefits_raw", "generate_columns": true}'
dbt run-operation generate_source --args '{"schema_name": "drugs", "database_name": "pharmacy_benefits_raw", "generate_columns": true}'
dbt run-operation generate_source --args '{"schema_name": "members", "database_name": "pharmacy_benefits_raw", "generate_columns": true}'
dbt run-operation generate_source --args '{"schema_name": "pharmacies", "database_name": "pharmacy_benefits_raw", "generate_columns": true}'
dbt run-operation generate_source --args '{"schema_name": "plans", "database_name": "pharmacy_benefits_raw", "generate_columns": true}'
dbt run-operation generate_source --args '{"schema_name": "providers", "database_name": "pharmacy_benefits_raw", "generate_columns": true}'
