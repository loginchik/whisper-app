import PyQt6.QtWidgets as QtW


class ProcessLabel(QtW.QWidget):
    def __init__(self, label: str, default: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.label = QtW.QLabel(default)

        layout = QtW.QHBoxLayout()
        layout.addWidget(QtW.QLabel(label))
        layout.addStretch(1)
        layout.addWidget(self.label)
        layout.setContentsMargins(*([0] * 4))
        self.setLayout(layout)

    def update_label(self, new: str) -> None:
        """
        Updates label text as provided

        :param new: new label text
        """
        self.label.setText(new)

    def increase_counter(self) -> None:
        """
        Assuming that label stores integer, increases its value by 1
        """
        current_value = int(self.label.text())
        self.update_label(str(current_value + 1))
