import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
LOG_DIR = PROJECT_ROOT / "logs"
VENV_PYTHON = PROJECT_ROOT / ".venv" / "bin" / "python"
TIMESTAMP_FILE = RAW_DIR / ".pipeline_timestamp"
DBT_TARGET = "dev"


def load_project_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def dbt_env() -> dict[str, str]:
    load_project_env()
    env = os.environ.copy()
    venv_bin = str(PROJECT_ROOT / ".venv" / "bin")
    env["PATH"] = f"{venv_bin}:{env.get('PATH', '')}"
    return env
