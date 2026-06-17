import logging
import subprocess

from pipeline.config import DBT_TARGET, PROJECT_ROOT, dbt_env
from pipeline.synthetic.common import setup_logging

logger = setup_logging("pipeline.dbt_runner")


def run_dbt(*command_parts: str, select: str | None = None) -> None:
    args = list(command_parts)
    if select:
        args.extend(["--select", select])
    args.extend([
        "--target", DBT_TARGET,
        "--project-dir", str(PROJECT_ROOT),
    ])

    profiles_path = PROJECT_ROOT / "profiles.yml"
    if profiles_path.exists():
        args.extend(["--profiles-dir", str(PROJECT_ROOT)])

    logger.info("Running dbt command | args=%s", " ".join(args))
    result = subprocess.run(
        ["dbt", *args],
        cwd=PROJECT_ROOT,
        env=dbt_env(),
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        logger.info("dbt stdout:\n%s", result.stdout)
    if result.stderr:
        logger.info("dbt stderr:\n%s", result.stderr)
