with stg_members as (
    select
        member_id::number as member_id,
        plan_id::number as plan_id,
        nullif(trim(member_status::varchar), '') as member_status,
        nullif(trim(state::varchar), '') as state,
        eligibility_start_date::date as eligibility_start_date,
        eligibility_end_date::date as eligibility_end_date,
        loaded_at::timestamp_tz as loaded_at
    from {{ source('members', 'raw_members') }}
)

select * from stg_members
