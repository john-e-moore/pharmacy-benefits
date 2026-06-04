with daily_counts as (

    select
        cast(loaded_at as date) as load_date,
        count(*) as row_count

    from {{ ref('fct_claims') }}
    group by 1

)

select *
from daily_counts
where row_count < 50
   or row_count > 10000