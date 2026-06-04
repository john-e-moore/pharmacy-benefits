with stg_providers as (
    select
        provider_id::number as provider_id,
        nullif(trim(npi::varchar), '') as npi,
        nullif(trim(provider_last_name::varchar), '') as provider_last_name,
        nullif(trim(specialty::varchar), '') as specialty,
        nullif(trim(state::varchar), '') as state,
        loaded_at::timestamp_tz as loaded_at
    from {{ source('providers', 'raw_providers') }}
)

select * from stg_providers
