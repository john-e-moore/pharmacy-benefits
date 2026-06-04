select
    plan_id,
    plan_name,
    plan_type,
    loaded_at
from {{ ref('stg_plans') }}
