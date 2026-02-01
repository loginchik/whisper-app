from typing import Self, Tuple

from PyQt6.QtGui import QIcon, QPixmap
import PyQt6.QtWidgets as QtW
from PyQt6.QtCore import QSize, QByteArray

from src.transcriber.schemas import WhisperModel


class ModelsSelector(QtW.QComboBox):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # TODO: create icons
        self.loaded_icon = self.create_dummy_icon("green", 16)
        self.not_loaded_icon = self.create_dummy_icon("red", 16)

    def fill(self, models: Tuple[WhisperModel, ...]) -> Self:
        """
        Sets items and icons depending on model being available locally

        :param models: available models
        :return: self
        """
        self.clear()

        for i, model in enumerate(models):
            self.addItem(model.name)
            self.setItemIcon(i, self.loaded_icon if model.is_loaded else self.not_loaded_icon)
        self.setIconSize(QSize(16, 16))

        return self

    @staticmethod
    def create_dummy_icon(color: str, size: int) -> QIcon:
        svg_content = f"""
        <svg width="{size}" height="{size}" xmlns="http://www.w3.org">
          <rect width="{size}" height="{size}" fill="{color}"/>
        </svg>
        """.encode("utf-8")

        pixmap = QPixmap(QSize(size, size))
        pixmap.loadFromData(QByteArray(svg_content), "SVG")
        return QIcon(pixmap)
