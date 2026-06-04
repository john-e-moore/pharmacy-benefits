with stg_pharmacies as (
    select
        pharmacy_id::number as pharmacy_id,
        nullif(trim(pharmacy_name::varchar), '') as pharmacy_name,
        nullif(trim(ncpdp_id::varchar), '') as ncpdp_id,
        nullif(trim(state::varchar), '') as state,
        nullif(trim(network_status::varchar), '') as network_status,
        loaded_at::timestamp_tz as loaded_at
    from {{ source('pharmacies', 'raw_pharmacies') }}
)

select * from stg_pharmacies
