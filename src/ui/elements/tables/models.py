from gettext import gettext as _
from typing import Tuple, Self

import PyQt6.QtWidgets as QtW

from src.transcriber.schemas import WhisperModel


class ModelsTableWidget(QtW.QTableWidget):
    COLUMNS: Tuple[str, ...] = ("parameters", "required_ram", "relative_speed", "disk_space", "is_loaded")

    def fill(self, models: Tuple[WhisperModel, ...]) -> Self:
        """
        Re-renders table data - draws new models information

        :param models: models to display
        """
        self.clear()

        # Configure columns
        self.setColumnCount(len(self.COLUMNS))
        self.setHorizontalHeaderLabels(self.column_labels)
        # Configure rows
        self.setRowCount(len(models))
        self.setVerticalHeaderLabels(list(map(lambda m: m.name, models)))

        # Fill data cell by cell
        for i, model in enumerate(models):
            for j, column in enumerate(self.COLUMNS):
                self.setItem(i, j, QtW.QTableWidgetItem(getattr(model, f"displayed_{column}")))

        return self

    @property
    def column_labels(self) -> Tuple[str, ...]:
        """
        Generates human-readable column names for the table

        :return: column labels
        """
        return tuple(map(lambda col: _(col), self.COLUMNS))
