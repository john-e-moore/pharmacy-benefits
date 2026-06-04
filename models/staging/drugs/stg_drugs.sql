with stg_drugs as (
    select
        drug_id::number as drug_id,
        nullif(trim(ndc_code::varchar), '') as ndc_code,
        nullif(trim(drug_name::varchar), '') as drug_name,
        nullif(trim(therapeutic_class::varchar), '') as therapeutic_class,
        nullif(trim(brand_generic::varchar), '') as brand_generic,
        loaded_at::timestamp_tz as loaded_at
    from {{ source('drugs', 'raw_drugs') }}
)

select * from stg_drugs
