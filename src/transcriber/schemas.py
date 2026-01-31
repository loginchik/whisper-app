from gettext import gettext as _
from pathlib import Path
from typing import Literal, List, Optional

from pydantic import BaseModel, Field, AliasChoices

from src.settings import settings


class WhisperModel(BaseModel):
    """
    Single Whisper model metadata and description
    """

    name: Literal["tiny", "small", "base", "medium", "large"]
    required_ram: int = Field(serialization_alias="Необходимо VRAM")
    relative_speed: int = Field(serialization_alias="Относительная скорость")
    disk_space: int = Field(serialization_alias="Пространство на диске")
    is_default: bool = Field(
        validation_alias=AliasChoices("default", "is_default"), default=False, serialization_alias="Доступна локально"
    )

    @property
    def displayed_required_ram(self) -> str:
        """
        Adds decorations to required RAM value

        :return: decorated required RAM value
        """
        return f"~{self.required_ram}GB"

    @property
    def displayed_relative_speed(self) -> str:
        """
        Adds decorations to relative speed value

        :return: decorated relative speed value
        """
        return f"~{self.relative_speed}x"

    @property
    def displayed_disk_space(self) -> str:
        """
        Adds decorations to required disk space value

        If value is bigger than 1GB, converts it into GB.
        Otherwise, returns value with "MB" label

        :return: decorated disk space
        """
        if self.disk_space < 1024:
            return f"~{self.disk_space}MB"
        return f"~{round(self.disk_space / 1024, 2)}GB"

    @property
    def filepath(self, store_dir: Path = settings.CACHE_DIR) -> Path:
        """
        Generates filepath where model can be stored

        :param store_dir: application directory in the filesystem
        :return: model filepath
        """
        return store_dir.joinpath(f"{self.name}.pt")

    @property
    def is_loaded(self) -> bool:
        """
        Checks if model file exists in the filesystem,
        meaning that model had been loaded before and can be reused

        :return: whether models is stored in filesystem
        """
        return self.filepath.exists() and self.filepath.is_file(follow_symlinks=False)

    @property
    def displayed_is_loaded(self) -> str:
        """
        Converts `is_loaded` to a human-readable value

        :return: `is_loaded` description
        """
        return _("is loaded") if self.is_loaded else _("not loaded")


class ModelSettings(BaseModel):
    """
    Settings for whisper to transcribe audio file
    """

    name: str  #: Preset name
    temperature: List[float]
    word_timestamps: bool = Field(default=False)
    fp16: bool = Field(default=False)
    condition_on_previous_text: bool = Field(default=False)

    language: Optional[str] = Field(default=None)
    initial_prompt: Optional[str] = Field(default=None)
    beam_size: Optional[int] = Field(default=None)
    best_of: Optional[int] = Field(default=None)
    no_speech_threshold: Optional[float] = Field(default=None)
    logprob_threshold: Optional[float] = Field(default=None)
    compression_ratio_threshold: Optional[float] = Field(default=None)
