select
    fill_date,
    count(*) as row_count
from {{ ref('claim_status_daily') }}
group by 1
having count(*) > 1
