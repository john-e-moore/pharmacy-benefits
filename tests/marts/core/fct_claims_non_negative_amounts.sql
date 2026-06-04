select
    claim_id,
    ingredient_cost,
    dispensing_fee,
    member_copay,
    plan_paid,
    gross_claim_cost
from {{ ref('fct_claims') }}
where ingredient_cost < 0
   or dispensing_fee < 0
   or member_copay < 0
   or plan_paid < 0
   or gross_claim_cost < 0
