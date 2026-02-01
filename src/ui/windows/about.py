import PyQt6.QtWidgets as QtW

from src.settings import settings
from src.ui.elements.labels import InformationLabel


class AboutWindow(QtW.QDialog):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setWindowTitle(self.tr("About"))
        self.setModal(True)

        information = InformationLabel(self.tr("App name"))
        information.add_paragraph(
            self.tr(
                "Whisper is a general-purpose speech recognition model. It is trained on a large dataset of diverse "
                "audio and is a multitasking model"
            )
        )
        information.add_paragraph(
            self.tr(
                "This application employs its multilingual speech recognition and language "
                "detection features, supporting 50+ world languages"
            )
        )
        information.add_paragraph('OpenAI Whisper: <a href="https://github.com/openai/whisper/tree/v20250625">Github</a>')
        information.add_paragraph('Application: <a href="https://github.com/loginchik/whisper-app">Github</a>')

        layout = QtW.QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(information)
        layout.addStretch(1)
        layout.addWidget(QtW.QLabel("v" + settings.version))
        layout.setContentsMargins(*([20] * 4))
        self.setLayout(layout)

        self.setMinimumSize(350, 100)
        self.adjustSize()
