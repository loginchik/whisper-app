from gettext import gettext as _
from typing import Tuple

import PyQt6.QtWidgets as QtW

from src.transcriber.schemas import WhisperModel
from src.ui.elements.tables import ModelsTableWidget
from src.ui.elements.labels import InformationLabel


class ModelsWindow(QtW.QWidget):
    def __init__(self, models: Tuple[WhisperModel, ...], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.table = ModelsTableWidget().fill(models)
        self.table.resizeColumnsToContents()
        self.table.setContentsMargins(0, 10, 0, 0)

        layout = QtW.QVBoxLayout()
        layout.addWidget(self.get_text_element())
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.setWindowTitle(_("About models"))

        self.setMinimumSize(400, 400)
        self.setMaximumSize(650, 650)
        self.adjustSize()

    @staticmethod
    def get_text_element() -> QtW.QWidget:
        """
        Creates static text elements with models short description

        :return: widget
        """
        information = InformationLabel(title=_("Available models"))

        paragraphs = [
            _(
                "Below are the names of the available models and their approximate memory requirements "
                "and inference speed relative to the large model. Besides number of parameters, "
                "Whisper's performance highly depends on the language"
            ),
            _("Source")
            + ': <a href="https://github.com/openai/whisper/blob/main/README.md#available-models-and-languages">OpenAI</a>',
        ]
        for par in paragraphs:
            information.add_paragraph(par)

        return information
