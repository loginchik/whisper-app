from typing import List

import PyQt6.QtWidgets as QtW

from src.transcriber.schemas import ModelSettings


class PresetSelector(QtW.QComboBox):
    def __init__(self, presets: List[ModelSettings], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        for preset in presets:
            self.addItem(self.tr(preset.name))
