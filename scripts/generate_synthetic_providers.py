import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from random import choice, seed

from synthetic.common import pipeline_timestamp, setup_logging, write_csv
from synthetic.constants import PROVIDER_COUNT, RANDOM_SEED, SPECIALTIES, US_STATES

logger = setup_logging("generate_synthetic_providers")

try:
    seed(RANDOM_SEED)
    logger.info("Starting synthetic providers generation")

    now = pipeline_timestamp()
    providers = []

    for provider_id in range(1, PROVIDER_COUNT + 1):
        providers.append(
            {
                "provider_id": provider_id,
                "npi": f"{1000000000 + provider_id}",
                "provider_last_name": f"Provider_{provider_id:03d}",
                "specialty": choice(SPECIALTIES),
                "state": choice(US_STATES),
                "loaded_at": now.isoformat(),
            }
        )

    output_path = write_csv(pd.DataFrame(providers), "providers.csv")

    logger.info(
        "Synthetic providers generation complete | rows=%s | output_path=%s",
        len(providers),
        output_path,
    )
    print(f"Wrote {len(providers)} rows to {output_path}")

except Exception:
    logger.exception("Synthetic providers generation failed")
    raise
