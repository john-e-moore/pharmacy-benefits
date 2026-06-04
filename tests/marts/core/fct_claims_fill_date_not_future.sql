select
    claim_id,
    fill_date
from {{ ref('fct_claims') }}
where fill_date > current_date()
