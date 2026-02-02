from typing import Self, Tuple

from PyQt6.QtGui import QIcon
import PyQt6.QtWidgets as QtW
from PyQt6.QtCore import QSize

from src.settings import settings
from src.transcriber.schemas import WhisperModel


class ModelsSelector(QtW.QComboBox):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.not_loaded_icon = QIcon(str(settings.STATIC_DIR / "download.png"))

    def fill(self, models: Tuple[WhisperModel, ...]) -> Self:
        """
        Sets items and icons depending on model being available locally

        :param models: available models
        :return: self
        """
        self.clear()

        for i, model in enumerate(models):
            self.addItem(model.name)
            if not model.is_loaded:
                self.setItemIcon(i, self.not_loaded_icon)
                self.setIconSize(QSize(12, 12))

        return self
