with 
    claims as (
        select * from {{ ref('stg_claims') }}
    ),
    ranked as (
        select
            *,
            row_number() over (
                partition by claim_id
                order by loaded_at desc
            ) as row_num
        from claims
    ),
    /* keep most recent */
    deduped as (
        select *
        from ranked
        where row_num = 1
    ),
    int_claims_enriched as (
        select
            *,
            ingredient_cost + dispensing_fee as gross_claim_cost,
            case
                when plan_paid > 0 then round(member_copay / (member_copay + plan_paid), 3)
                else null
            end as pct_total_member_copay,
            case 
                when claim_status = 'paid' then 1 else 0 
            end as is_claim_paid
        from deduped
    )
select * from int_claims_enriched