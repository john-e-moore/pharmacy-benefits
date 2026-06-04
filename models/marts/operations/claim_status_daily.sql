with claims as (
    select * from {{ ref('fct_claims') }}
),

aggregated as (
    select
        fill_date,
        count(*) as total_claims,
        sum(is_claim_paid) as paid_claims,
        count_if(claim_status = 'rejected') as rejected_claims,
        count_if(claim_status = 'reversed') as reversed_claims,
        sum(is_claim_paid) / nullif(count(*), 0) as paid_claim_rate,
        count_if(claim_status = 'reversed') / nullif(count(*), 0) as reversal_rate
    from claims
    group by 1
)

select * from aggregated
