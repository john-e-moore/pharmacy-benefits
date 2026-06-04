select
    drug_id,
    ndc_code,
    drug_name,
    therapeutic_class,
    brand_generic,
    loaded_at
from {{ ref('stg_drugs') }}
