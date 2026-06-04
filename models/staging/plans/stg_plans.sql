with stg_plans as (
    select
        plan_id::number as plan_id,
        nullif(trim(plan_name::varchar), '') as plan_name,
        nullif(trim(plan_type::varchar), '') as plan_type,
        loaded_at::timestamp_tz as loaded_at
    from {{ source('plans', 'raw_plans') }}
)

select * from stg_plans
