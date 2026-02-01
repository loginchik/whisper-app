from pathlib import Path
import os
from typing import Literal

from pydantic import BaseModel


class Settings(BaseModel):
    """
    Application constant settings

    Filepaths are either relative to current file location
    (thus it has to be in the root of the application directory)
    or address system directories
    """

    version: str = "0.0.1"
    debug: bool = False

    # In-app directories
    BASE_DIR: Path = Path(__file__).parent.resolve()
    STATIC_DIR: Path = BASE_DIR / "static"

    # System directories
    CACHE_DIR: Path = Path("~/.cache/whisper").expanduser()
    LOGGING_DIR: Path = CACHE_DIR / "logs"


settings = Settings()
