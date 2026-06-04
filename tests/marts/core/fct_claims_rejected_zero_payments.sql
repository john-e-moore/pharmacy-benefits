select
    claim_id,
    claim_status,
    plan_paid,
    member_copay
from {{ ref('fct_claims') }}
where claim_status = 'rejected'
  and (plan_paid != 0 or member_copay != 0)
