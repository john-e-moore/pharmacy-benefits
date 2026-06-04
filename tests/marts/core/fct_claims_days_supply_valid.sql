select
    claim_id,
    days_supply
from {{ ref('fct_claims') }}
where days_supply not in (30, 60, 90)
