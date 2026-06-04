with stg_claims as (
    select
        nullif(trim(claim_id::varchar), '') as claim_id,
        member_id::number as member_id,
        drug_id::number as drug_id,
        pharmacy_id::number as pharmacy_id,
        plan_id::number as plan_id,
        nullif(trim(ndc_code::varchar), '') as ndc_code,
        nullif(trim(claim_status::varchar), '') as claim_status,
        fill_date::date as fill_date,
        days_supply::number as days_supply,
        quantity::number as quantity,
        ingredient_cost::number as ingredient_cost,
        dispensing_fee::number as dispensing_fee,
        member_copay::number as member_copay,
        plan_paid::number as plan_paid,
        loaded_at::timestamp_tz as loaded_at
    from {{ source('claims', 'raw_claims') }}
)

select * from stg_claims
