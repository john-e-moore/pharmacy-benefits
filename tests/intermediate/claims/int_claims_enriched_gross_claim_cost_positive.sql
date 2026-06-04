with negative_values as (
    select
        gross_claim_cost
    from {{ ref('int_claims_enriched') }}
    where gross_claim_cost < 0
)
select * from negative_values
