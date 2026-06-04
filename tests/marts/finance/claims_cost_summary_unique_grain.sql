select
    fill_month,
    plan_id,
    count(*) as row_count
from {{ ref('claims_cost_summary') }}
group by 1, 2
having count(*) > 1
