select
    claim_id,
    is_claim_paid,
    allowed_amount
from {{ ref('fct_claims') }}
where is_claim_paid = 1
  and allowed_amount <= 0
