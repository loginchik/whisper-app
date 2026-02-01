from PyQt6 import QtWidgets as QtW
from PyQt6.QtCore import Qt


class InformationLabel(QtW.QWidget):
    def __init__(self, title: str, **kwargs) -> None:
        super().__init__(**kwargs)

        self.layout_ = QtW.QVBoxLayout()
        self.layout_.setContentsMargins(*([0] * 4))

        heading = QtW.QLabel("<b>" + title + "</b>")
        heading.setTextFormat(Qt.TextFormat.RichText)
        self.layout_.addWidget(heading)
        self.setLayout(self.layout_)

    def add_paragraph(self, text: str) -> None:
        """
        Inserts label widget at the end of current layout

        :param text: label text
        """
        information = QtW.QLabel()
        information.setWordWrap(True)
        information.setTextFormat(Qt.TextFormat.RichText)
        information.setText(text)
        information.setOpenExternalLinks(True)
        self.layout_.addWidget(information)
        self.setLayout(self.layout_)
