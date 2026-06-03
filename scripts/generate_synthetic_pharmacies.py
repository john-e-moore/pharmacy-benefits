import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from random import choice, seed

from synthetic.common import pipeline_timestamp, setup_logging, write_csv
from synthetic.constants import (
    OUT_OF_NETWORK_PHARMACY_COUNT,
    PHARMACY_COUNT,
    RANDOM_SEED,
    US_STATES,
)

logger = setup_logging("generate_synthetic_pharmacies")

try:
    seed(RANDOM_SEED)
    logger.info("Starting synthetic pharmacies generation")

    now = pipeline_timestamp()
    pharmacies = []
    out_of_network_ids = set(range(PHARMACY_COUNT - OUT_OF_NETWORK_PHARMACY_COUNT + 1, PHARMACY_COUNT + 1))

    for pharmacy_id in range(1, PHARMACY_COUNT + 1):
        network_status = "out_of_network" if pharmacy_id in out_of_network_ids else "in_network"
        pharmacies.append(
            {
                "pharmacy_id": pharmacy_id,
                "pharmacy_name": f"Pharmacy_{pharmacy_id:03d}",
                "ncpdp_id": f"{1000000 + pharmacy_id}",
                "state": choice(US_STATES),
                "network_status": network_status,
                "loaded_at": now.isoformat(),
            }
        )

    output_path = write_csv(pd.DataFrame(pharmacies), "pharmacies.csv")

    logger.info(
        "Synthetic pharmacies generation complete | rows=%s | output_path=%s",
        len(pharmacies),
        output_path,
    )
    print(f"Wrote {len(pharmacies)} rows to {output_path}")

except Exception:
    logger.exception("Synthetic pharmacies generation failed")
    raise
