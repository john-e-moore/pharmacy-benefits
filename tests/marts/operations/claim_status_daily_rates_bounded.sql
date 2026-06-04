select
    fill_date,
    paid_claim_rate,
    reversal_rate
from {{ ref('claim_status_daily') }}
where (paid_claim_rate is not null and (paid_claim_rate < 0 or paid_claim_rate > 1))
   or (reversal_rate is not null and (reversal_rate < 0 or reversal_rate > 1))
