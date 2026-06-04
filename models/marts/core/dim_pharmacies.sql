select
    pharmacy_id,
    pharmacy_name,
    ncpdp_id,
    state,
    network_status,
    loaded_at
from {{ ref('stg_pharmacies') }}
