import os
from pathlib import Path
from dotenv import load_dotenv

# Project root is one level up from src/
_project_root = Path(__file__).resolve().parent.parent

_ALL_KEYS = {
    "govocal": ("GOVOCAL_BASE_URL", "GOVOCAL_CLIENT_ID", "GOVOCAL_CLIENT_SECRET"),
    "typeform": ("TYPEFORM_TOKEN",),
}


def _load():
    """(Re-)load .env and refresh module-level credential variables."""
    global GOVOCAL_BASE_URL, GOVOCAL_CLIENT_ID, GOVOCAL_CLIENT_SECRET, TYPEFORM_TOKEN

    load_dotenv(_project_root / ".env", override=True)

    GOVOCAL_BASE_URL = os.environ.get("GOVOCAL_BASE_URL", "").rstrip("/")
    GOVOCAL_CLIENT_ID = os.environ.get("GOVOCAL_CLIENT_ID", "")
    GOVOCAL_CLIENT_SECRET = os.environ.get("GOVOCAL_CLIENT_SECRET", "")
    TYPEFORM_TOKEN = os.environ.get("TYPEFORM_TOKEN", "")


# Load on first import
_load()


def validate(services=None):
    """Check that required env vars are set. Raises ValueError if any are missing.

    Re-reads the .env file each time so changes are picked up without
    restarting the kernel.

    Args:
        services: Optional list of service names to validate ("govocal", "typeform").
                  If None, validates all.
    """
    _load()  # refresh from .env

    if services is None:
        keys_to_check = [k for group in _ALL_KEYS.values() for k in group]
    else:
        keys_to_check = []
        for svc in services:
            keys_to_check.extend(_ALL_KEYS.get(svc.lower(), ()))

    missing = [k for k in keys_to_check if not os.environ.get(k)]
    if missing:
        raise ValueError(
            f"Missing environment variables: {', '.join(missing)}. "
            "Copy .example.env to .env and fill in your credentials."
        )
