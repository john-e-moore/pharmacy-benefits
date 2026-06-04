# dbt + Snowflake Interview Roadmap: Pharmacy Benefits Claims Project

## Goal

Use your pharmacy benefits claims project to build hands-on fluency in dbt, Snowflake, Git-based deployment workflows, data quality, observability, lineage, and healthcare-domain analytics.

The aim is not to make the most complex project possible. The aim is to be able to explain, confidently and concretely:

- how raw claims data lands in Snowflake
- how dbt turns raw data into reliable analytics models
- how tests, docs, lineage, and freshness checks create trust
- how dev/prod environments and Git workflows support deployment
- how Snowflake performance, cost, and security concerns show up in real work

---

## Current Starting Point

You already have:

- Snowflake databases for raw, dev, and prod
- dbt dev/prod profiles planned
- Python scripts to generate synthetic claims data
- Python loader to append raw data into Snowflake
- logging to `logs/pipeline.log`
- a realistic domain: pharmacy benefits / PBM claims analytics

Your next phase is manual dbt buildout.

---

## Suggested Repo Shape

```text
pharmacy-benefits/
  dbt_project.yml
  packages.yml
  README.md
  .gitignore

  analyses/
  macros/
  models/
    staging/
      claims/
      members/
      drugs/
      pharmacies/
      plans/
    intermediate/
    marts/
      core/
      finance/
      operations/
  seeds/
  snapshots/
  tests/

  scripts/
    generate_synthetic_claims.py
    load_raw_to_snowflake.py
    run_pipeline.sh

  snowflake/
    setup_dev.sql
    setup_prod.sql
    setup_raw.sql

  data/
    raw/

  docs/
    interview_notes.md
    domain_notes.md
    data_model_notes.md
```

Keep generated files out of Git:

```gitignore
.env
logs/
target/
dbt_packages/
data/raw/*.csv
profiles.yml
```

---

## Phase 1: Prove the End-to-End Loop

### Objective

Make sure you can generate data, load raw Snowflake tables, run dbt, and verify outputs.

### Tasks

- [x] Run `python scripts/generate_synthetic_claims.py`
- [x] Run `python scripts/load_raw_to_snowflake.py`
- [x] Confirm raw table exists in Snowflake:

```sql
select count(*)
from PHARMACY_BENEFITS_RAW.CLAIMS.RAW_CLAIMS;
```

- [x] Run:

```bash
dbt debug --target dev
dbt debug --target prod
dbt parse
```

- [x] Create one smoke-test model manually:

```sql
-- models/smoke_test.sql
select
    1 as test_id,
    current_timestamp as loaded_at
```

- [x] Run:

```bash
dbt run --select smoke_test --target dev
dbt run --select smoke_test --target prod
```

- [x] Drop the smoke-test model after verifying it appears in Snowflake.

### Interview Talking Point

“I set up a raw/dev/prod Snowflake layout and validated that dbt could connect, compile, and write to both dev and prod targets before building actual models.”

---

## Phase 2: Define Sources and Freshness

### Objective

Teach dbt where raw data lives and how fresh it should be.

### Tasks

- [x] Create a source YAML file:

```text
models/staging/claims/_src_claims.yml
```

- [x] Define source for `PHARMACY_BENEFITS_RAW.CLAIMS.RAW_CLAIMS`
- [x] Add `loaded_at_field: loaded_at`
- [x] Add freshness thresholds:

```yaml
warn_after:
  count: 3
  period: hour
error_after:
  count: 6
  period: hour
```

- [x] Run:

```bash
dbt source freshness --target dev
```

- [x] Intentionally wait or change freshness thresholds to observe pass/warn/error behavior.

### Manual Practice Rule

Write the source YAML by hand first. After that, try `dbt-codegen` to generate source YAML and compare it to your manual version.

### Interview Talking Point

“Source freshness lets dbt check whether upstream raw data is arriving within an expected SLA. In a real pipeline, I would run freshness before downstream models so stale source data does not silently flow into reporting.”

---

## Phase 3: Build Staging Models

### Objective

Create clean, renamed, lightly typed models from raw sources.

### Suggested Staging Models

```text
models/staging/claims/stg_claims.sql
models/staging/members/stg_members.sql
models/staging/drugs/stg_drugs.sql
models/staging/pharmacies/stg_pharmacies.sql
models/staging/plans/stg_plans.sql
```

Start with `stg_claims.sql` because you currently have claims data.

### Staging Model Checklist

For each staging model:

- [x] Pull from `source()` only
- [x] Rename columns into consistent snake_case
- [x] Cast dates/timestamps explicitly
- [x] Standardize status values
- [x] Avoid business aggregation logic
- [x] Add a primary key-like field
- [x] Add `loaded_at`

Example logic to practice manually:

```sql
select
    claim_id,
    member_id,
    drug_id,
    pharmacy_id,
    plan_id,
    lower(claim_status) as claim_status,
    fill_date::date as fill_date,
    days_supply,
    quantity,
    ingredient_cost,
    dispensing_fee,
    member_copay,
    plan_paid,
    loaded_at::timestamp_tz as loaded_at
from {{ source('claims_raw', 'raw_claims') }}
```

### Tests to Add

- [x] `not_null` on `claim_id`
- [x] `unique` on `claim_id`
- [x] `accepted_values` on `claim_status`
- [x] `not_null` on `loaded_at`
- [ ] relationship tests later once dimension tables exist

### Interview Talking Point

“I use staging models to clean and standardize raw source data without burying business logic there. Staging creates a stable interface for downstream models.”

---

## Phase 4: Add dbt Packages Carefully

### Objective

Practice using packages without outsourcing your understanding.

### Recommended Packages

Add `dbt-codegen` for generating boilerplate YAML and model scaffolding. Use it after writing at least one source and model manually.

Example `packages.yml`:

```yaml
packages:
  - package: dbt-labs/codegen
    version: [">=0.13.0", "<1.0.0"]
```

Then run:

```bash
dbt deps
```

Useful commands to practice:

```bash
dbt run-operation generate_source --args '{schema_name: CLAIMS, database_name: PHARMACY_BENEFITS_RAW}'
```

```bash
dbt run-operation generate_model_yaml --args '{model_names: [stg_claims]}'
```

### Manual Practice Rule

Use packages to accelerate after you understand the output. Do not use generated YAML blindly. Edit descriptions, tests, and names yourself.

### Interview Talking Point

“I used dbt-codegen to speed up repetitive YAML scaffolding, but I manually reviewed and edited descriptions, tests, and model semantics.”

---

## Phase 5: Build Intermediate Models

### Objective

Create reusable business logic models that prepare facts/dimensions.

### Suggested Intermediate Models

```text
models/intermediate/int_claims_enriched.sql
models/intermediate/int_claim_cost_components.sql
models/intermediate/int_claims_by_member_day.sql
```

### Practice Logic

- [x] Compute total claim cost:

```sql
ingredient_cost + dispensing_fee as gross_claim_cost
```

- [x] Compute payer/member split:

```sql
plan_paid + member_copay as allowed_amount
```

- [x] Add claim status flags:

```sql
case when claim_status = 'paid' then 1 else 0 end as is_paid_claim
```

- [ ] Join to member, plan, pharmacy, and drug tables once available
- [x] Deduplicate if needed using `row_number()`

### Interview Talking Point

“Intermediate models are where I put reusable business logic that should not be repeated across marts.”

---

## Phase 6: Build Marts and Metrics-Oriented Models

### Objective

Create fact and dimension models suitable for analytics and reporting.

### Suggested Core Models

```text
models/marts/core/fct_claims.sql
models/marts/core/dim_members.sql
models/marts/core/dim_drugs.sql
models/marts/core/dim_pharmacies.sql
models/marts/core/dim_plans.sql
```

### Suggested Analytical Marts

```text
models/marts/finance/claims_cost_summary.sql
models/marts/operations/claim_status_daily.sql
models/marts/operations/pharmacy_claim_volume.sql
models/marts/finance/plan_paid_by_month.sql
```

### Metrics to Compute

- [ ] Total claims
- [ ] Paid claims
- [ ] Rejected claims
- [ ] Reversal rate
- [ ] Total ingredient cost
- [ ] Total dispensing fees
- [ ] Total member copay
- [ ] Total plan paid
- [ ] Average cost per claim
- [ ] Claims per member
- [ ] Top drugs by plan paid
- [ ] Top pharmacies by claim volume
- [ ] Monthly paid amount trend

### Interview Talking Point

“I modeled claims as the central fact table, with member, plan, drug, and pharmacy dimensions. Then I built reporting marts around cost, utilization, and claim status.”

---

## Phase 7: Tests, Data Quality, and Observability

### Objective

Show that you know how to build trust into pipelines.

### dbt Generic Tests

- [ ] `not_null`
- [ ] `unique`
- [ ] `accepted_values`
- [ ] `relationships`

### Custom Data Tests

Create custom SQL tests for rules like:

- [ ] `plan_paid >= 0`
- [ ] `member_copay >= 0`
- [ ] `ingredient_cost >= 0`
- [ ] paid claims should have positive allowed amount
- [ ] rejected claims should not have plan paid, if that matches your business rule
- [ ] `fill_date <= current_date`
- [ ] `days_supply in (30, 60, 90)`

### Observability Concepts to Practice

- [ ] Freshness: did source data arrive?
- [ ] Volume: did row counts unexpectedly spike/drop?
- [ ] Schema drift: did columns change?
- [ ] Validity: are values within expected ranges?
- [ ] Uniqueness: are keys duplicated?
- [ ] Referential integrity: do foreign keys match dimensions?

### Add Simple Audit Models

```text
models/marts/operations/audit_claim_loads.sql
models/marts/operations/audit_claim_volume_by_loaded_at.sql
```

### Interview Talking Point

“Data quality is not just testing for nulls. I think in terms of freshness, volume, validity, uniqueness, referential integrity, and business-rule checks.”

---

## Phase 8: Docs and Lineage

### Objective

Generate documentation and explain lineage clearly.

### Tasks

- [ ] Add model descriptions
- [ ] Add column descriptions
- [ ] Add source descriptions
- [ ] Add tests in YAML
- [ ] Run:

```bash
dbt docs generate
dbt docs serve
```

- [ ] Inspect lineage graph
- [ ] Be able to trace:

```text
RAW_CLAIMS -> stg_claims -> int_claims_enriched -> fct_claims -> claims_cost_summary
```

### Interview Talking Point

“dbt lineage shows transformation dependencies inside the warehouse. Airflow would orchestrate the broader pipeline around extraction, loading, dbt runs, retries, and alerting.”

---

## Phase 9: Dev, Prod, Git, and Deployment Practice

### Objective

Practice the workflow a real team would use.

### Branch Workflow

- [ ] Create a feature branch:

```bash
git checkout -b feature/staging-claims
```

- [ ] Add source YAML and staging model
- [ ] Run locally:

```bash
dbt build --target dev --select stg_claims+
```

- [ ] Commit changes:

```bash
git add .
git commit -m "Add claims source and staging model"
```

- [ ] Merge to main after tests pass

### Deployment Simulation

Practice these commands:

```bash
dbt build --target dev
```

```bash
dbt build --target prod
```

### CI/CD Concepts to Understand

- Pull request opens
- CI installs dependencies with `dbt deps`
- CI validates parse/compile
- CI builds modified models in a dev or CI schema
- Merge to main triggers prod deployment
- Prod deployment runs with prod role, prod warehouse, prod database

### Interview Talking Point

“In dev, I build into my personal schema. In prod, dbt builds controlled schemas such as staging, intermediate, marts, and snapshots. Git and CI/CD control promotion from dev work to production.”

---

## Phase 10: Incremental Models and Snapshots

### Objective

Learn dbt patterns for non-static data.

### Incremental Model Practice

Create an incremental version of `fct_claims`.

Practice:

- [ ] `materialized='incremental'`
- [ ] `unique_key='claim_id'`
- [ ] `is_incremental()`
- [ ] filtering on `loaded_at`
- [ ] merge/upsert behavior

Questions to answer:

- What happens when a claim is corrected?
- What happens when a claim is reversed?
- Should the model append, merge, or snapshot?

### Snapshot Practice

Use snapshots for slowly changing dimensions or historical state tracking:

```text
snapshots/member_plan_snapshot.sql
```

Good candidates:

- member eligibility
- plan assignment
- pharmacy network status
- drug formulary tier

### Interview Talking Point

“Incremental models help with large fact tables where rebuilding everything is expensive. Snapshots are useful when I need history of changing source records, such as eligibility or plan membership.”

---

## Phase 11: Snowflake Data Modeling

### Objective

Explain how data lands and becomes analytical.

### Concepts to Practice

- [ ] Raw tables preserve source-like records
- [ ] Staging models clean and standardize
- [ ] Intermediate models apply reusable business logic
- [ ] Facts store business events
- [ ] Dimensions describe entities
- [ ] Marts aggregate for reporting

### Claims Domain Model

Central fact:

```text
fct_claims
```

Dimensions:

```text
dim_members
dim_plans
dim_drugs
dim_pharmacies
dim_providers
```

Common grains:

- one row per claim
- one row per member per eligibility period
- one row per drug
- one row per pharmacy
- one row per plan
- one row per claim status per day

### Interview Talking Point

“The first thing I identify is the grain. For claims, the core fact table grain is one row per claim or claim transaction, depending on whether reversals and adjustments are represented separately.”

---

## Phase 12: Snowflake Performance and Cost

### Objective

Be able to speak practically about performance without over-engineering.

### Topics to Practice

- [ ] Warehouse size controls compute resources
- [ ] Auto-suspend controls idle cost
- [ ] Auto-resume improves usability
- [ ] Separate warehouses isolate workloads
- [ ] Result cache can make repeated queries faster
- [ ] Warehouse cache can help queries that reuse recently accessed data
- [ ] Clustering can help very large tables with common filters
- [ ] Query profile helps identify scan volume, joins, spills, and bottlenecks

### Practical Exercises

- [ ] Run a model on `XSMALL`
- [ ] Inspect query profile
- [ ] Re-run the same query and observe caching behavior
- [ ] Filter a large claims table by `fill_date`
- [ ] Think about whether clustering by `fill_date` would help once data is large

### Interview Talking Point

“I would not jump to clustering immediately. I’d first look at query profile, data volume, filter patterns, warehouse sizing, and whether caching or model design solves the problem.”

---

## Phase 13: PII, PHI, and HIPAA Awareness

### Objective

Show healthcare data maturity without pretending to be a compliance expert.

### Concepts to Know

- PHI includes individually identifiable health information
- Claims, eligibility, member IDs, DOB, addresses, diagnoses, and prescriptions can be sensitive
- Use least-privilege access
- Avoid committing real data to Git
- Avoid logging secrets or sensitive values
- Mask, tokenize, or de-identify sensitive fields when possible
- Separate raw sensitive data from analytics-ready data
- Be careful with exports, local files, and screenshots
- Production healthcare systems need appropriate governance, auditing, access controls, and agreements such as BAAs where applicable

### Project Practice

- [ ] Use synthetic data only
- [ ] Do not generate realistic SSNs, DOBs tied to names, or real patient data
- [ ] Keep `.env` out of Git
- [ ] Keep raw CSV outputs out of Git
- [ ] Do not log passwords or sensitive row-level data
- [ ] Add a README note: “This project uses synthetic data only.”

### Interview Talking Point

“I treated the project as if claims data could be PHI: least privilege, no secrets in Git, synthetic data only, and careful separation of raw from modeled outputs.”

---

## Phase 14: Pharmacy Benefits / Claims Domain Notes

### Key Entities

- Member: covered person receiving benefits
- Plan: benefit design or coverage arrangement
- Claim: request/payment record for a prescription fill
- Pharmacy: dispensing location
- Drug: medication, usually identified by NDC
- Provider/prescriber: clinician associated with prescription
- Formulary: covered drug list and tiers
- Eligibility: whether a member has coverage during a period

### Useful Claims Concepts

- paid claim
- rejected claim
- reversed claim
- ingredient cost
- dispensing fee
- member copay
- plan paid
- allowed amount
- days supply
- quantity dispensed
- NDC
- formulary tier
- prior authorization
- network pharmacy

### Questions to Practice Answering

- What is the grain of a claims fact table?
- How would you handle reversed claims?
- How would you model member eligibility over time?
- How would you calculate plan paid per month?
- How would you find top drugs by total cost?
- How would you identify stale source data?
- How would you validate claim financial fields?

---

## Phase 15: Build-It-Again Without AI Drill

### Objective

Prepare for the interview by forcing recall.

Do this once from scratch using notes only, not generated code.

### Drill

- [ ] Create a new branch:

```bash
git checkout -b practice/rebuild-core-dbt
```

- [ ] Temporarily move or delete generated model files
- [ ] Recreate by hand:
  - [ ] source YAML
  - [ ] `stg_claims.sql`
  - [ ] model YAML with tests
  - [ ] one intermediate model
  - [ ] `fct_claims.sql`
  - [ ] one reporting mart
- [ ] Run:

```bash
dbt parse
dbt source freshness
dbt build --target dev
```

- [ ] Fix errors without asking AI first
- [ ] Write down what broke and how you fixed it

### Interview Talking Point

“I intentionally rebuilt the project from scratch to make sure I understood the dbt workflow rather than just copying generated files.”

---

## Two-Day Interview Sprint

### Day 1: Build Core dbt Project

- [ ] Validate Snowflake connection
- [ ] Load fresh raw claims data
- [ ] Define source YAML and freshness
- [ ] Build `stg_claims`
- [ ] Add tests and descriptions
- [ ] Build `int_claims_enriched`
- [ ] Build `fct_claims`
- [ ] Build one mart: `claims_cost_summary`
- [ ] Run `dbt docs generate`
- [ ] Inspect lineage

### Day 2: Make It Interview-Ready

- [ ] Add one incremental model
- [ ] Add 2-3 custom data tests
- [ ] Practice dev/prod runs
- [ ] Write README architecture summary
- [ ] Review Snowflake performance notes
- [ ] Review PHI/HIPAA talking points
- [ ] Practice explaining the whole pipeline in 2 minutes
- [ ] Practice answering: “Where does Airflow fit?”

---

## 2-Minute Project Explanation Script

“I built a small pharmacy benefits analytics project using synthetic claims data. A Python script generates raw claims data with a `loaded_at` timestamp, and a loader appends it to Snowflake raw tables. dbt defines those raw tables as sources, checks freshness, then transforms the data through staging, intermediate, and mart layers. The core fact table is claims, with dimensions for members, drugs, pharmacies, and plans. I added dbt tests for uniqueness, nulls, accepted values, and business rules like non-negative costs. I also generated docs and used dbt lineage to trace raw claims into reporting marts. The Snowflake setup separates raw, dev, and prod databases, with dev building into my personal schema and prod building into controlled schemas. For deployment, I would use Git branches, CI checks, and a production dbt job. Airflow would sit around this process to orchestrate extract/load, freshness checks, dbt builds, retries, and alerts.”

---

## Final Success Criteria

You are ready when you can do these without looking much up:

- [ ] Explain raw/dev/prod Snowflake separation
- [ ] Explain dbt source, ref, model, test, doc, and lineage concepts
- [ ] Build a staging model from a raw source
- [ ] Add source freshness
- [ ] Add generic and custom tests
- [ ] Build a fact table and a summary mart
- [ ] Explain incremental models and snapshots
- [ ] Explain where Airflow fits
- [ ] Explain Snowflake warehouse sizing/caching/clustering at a practical level
- [ ] Explain basic PHI/HIPAA-aware engineering habits
- [ ] Discuss claims, members, plans, drugs, pharmacies, and claim statuses
