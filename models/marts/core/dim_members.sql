select
    member_id,
    plan_id,
    member_status,
    state,
    eligibility_start_date,
    eligibility_end_date,
    loaded_at
from {{ ref('stg_members') }}
