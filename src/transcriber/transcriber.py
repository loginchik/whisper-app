from dataclasses import dataclass
from datetime import datetime
from gettext import gettext as _
from pathlib import Path
import re
from typing import Dict, List, Any, Tuple

import numpy as np
import polars as pl
import xlsxwriter
from yaml import safe_load

from src.settings import settings
from .model_manager import ModelManager
from .schemas import ModelSettings


class Transcriber(ModelManager):
    @dataclass(frozen=True)
    class Transcription:
        text: str
        segments: List[Any]
        language: str = None

    def __init__(self) -> None:
        super().__init__()

    def transcribe(self, audio: np.ndarray, preset: ModelSettings, path: Path) -> Tuple[Transcription, Path, ModelSettings]:
        """
        Runs transcription with parameters specified in preset

        :param audio: numpy audio data
        :param preset: transcription settings
        :param path: filepath
        :return: transcribed data, filepath, preset
        """
        result = self.model.transcribe(
            audio=audio, **preset.model_dump(mode="python", exclude_none=True, by_alias=False, exclude={"name"})
        )
        return self.Transcription(**result), path, preset

    def store_transcription(self, transcription: Transcription, target_dir: Path, filename: str, vad: bool) -> Path:
        """
        Creates export directory in target and stores transcription files

        :param transcription: transcription to store
        :param target_dir: target directory
        :param filename: original filename without extension
        :param vad: whether VAD was used
        :return: path to export directory
        """
        filename_clear = re.sub(r"\W", "", filename)
        export_dir = self.get_export_dir(target_dir, filename_clear)
        export_dir.mkdir()
        self.logger.debug("Created export directory: %s -> %s", filename, export_dir)

        filename_clear = filename_clear[:50]
        with open(export_dir / (filename_clear + " - Full Text.txt"), mode="w", encoding="utf-8") as file:
            file.write(transcription.text)
        self.logger.debug("Saved full text: %s", filename)

        with open(export_dir / (filename_clear + " - Meta.txt"), mode="w", encoding="utf-8") as file:
            file.writelines(
                [
                    _("Source") + f": {filename}\n",
                    _("Language") + f": {transcription.language}\n",
                    _("Created") + f": {datetime.now().strftime('%d %b %Y, %H:%M')}\n",
                ]
                + (
                    [_("Segments timings can mismatch audio timings, as voice detection was used to remove silence gaps")]
                    if vad
                    else []
                )
            )
        self.logger.debug("Saved meta file: %s", filename)

        if len(transcription.segments) > 0:
            segments_df = pl.DataFrame(transcription.segments, orient="row")
            with xlsxwriter.Workbook(export_dir / (filename_clear + " - Segments.xlsx")) as wb:
                segments_df.write_excel(wb, worksheet="segments")
            self.logger.debug("Saved segments file: %s", filename)

        return export_dir

    @staticmethod
    def get_export_dir(target_dir: Path, filename: str) -> Path:
        """
        Generates export dir from target directory and filename
        and adds number id, until the resulting directory name does not exist

        :param target_dir: parent directory to make export in
        :param filename: original filename (without extension) to name export directory after
        :return: export directory path
        """
        export_dir = target_dir.joinpath(filename)
        if not export_dir.exists():
            return export_dir

        i = 1
        while export_dir.exists():
            export_dir = target_dir.joinpath(f"{filename}_{i}")
            i += 1
        return export_dir

    @staticmethod
    def load_available_languages() -> Dict[str, str]:
        """
        Loads languages that are supported by whisper transcription model

        :return: languages (code - name)
        """
        with open(settings.STATIC_DIR / "transcriber.yaml", mode="r", encoding="utf-8") as file:
            data = safe_load(file.read())
        return data["languages"]
