from __future__ import annotations

from pathlib import Path
import os
import platform


APPLICATION_DIRECTORY_NAME = "Health Model Research OS"
DATA_DIRECTORY_ENVIRONMENT_VARIABLE = "HEALTH_MODEL_DATA_DIR"


def application_data_directory() -> Path:
    """Return a persistent user-data location outside the replaceable source tree."""
    configured = os.environ.get(DATA_DIRECTORY_ENVIRONMENT_VARIABLE)
    if configured:
        return Path(configured).expanduser().resolve()

    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / APPLICATION_DIRECTORY_NAME
    if system == "Windows":
        base = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
        return base / APPLICATION_DIRECTORY_NAME
    base = Path(os.environ.get("XDG_DATA_HOME") or (Path.home() / ".local" / "share"))
    return base / "health-model-research-os"

