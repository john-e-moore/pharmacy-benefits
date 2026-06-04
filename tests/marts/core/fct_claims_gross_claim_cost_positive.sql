select
    claim_id,
    gross_claim_cost
from {{ ref('fct_claims') }}
where gross_claim_cost < 0
