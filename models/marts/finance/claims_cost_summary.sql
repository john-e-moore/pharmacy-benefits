with claims as (
    select * from {{ ref('fct_claims') }}
),

plans as (
    select * from {{ ref('dim_plans') }}
),

aggregated as (
    select
        date_trunc('month', fill_date) as fill_month,
        claims.plan_id,
        plans.plan_name,
        plans.plan_type,
        count(*) as total_claims,
        sum(is_claim_paid) as paid_claims,
        count_if(claim_status = 'rejected') as rejected_claims,
        count_if(claim_status = 'reversed') as reversed_claims,
        sum(gross_claim_cost) as total_gross_claim_cost,
        sum(ingredient_cost) as total_ingredient_cost,
        sum(dispensing_fee) as total_dispensing_fee,
        sum(member_copay) as total_member_copay,
        sum(plan_paid) as total_plan_paid,
        avg(case when is_claim_paid = 1 then gross_claim_cost end) as avg_gross_claim_cost
    from claims
    left join plans on claims.plan_id = plans.plan_id
    group by 1, 2, 3, 4
)

select * from aggregated
