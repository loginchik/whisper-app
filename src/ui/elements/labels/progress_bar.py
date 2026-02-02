from logging import getLogger

import PyQt6.QtWidgets as QtW

from .process_label import ProcessLabel


class ProgressBarLabel(ProcessLabel):
    def __init__(self, label: str, **kwargs) -> None:
        super().__init__(label=label, default="0", **kwargs)
        self.logger = getLogger(self.__class__.__name__)
        self.layout.removeWidget(self.label)

        self.bar = QtW.QProgressBar()
        self.bar.setMinimum(0)
        self.bar.setMaximum(0)
        self.bar.setValue(0)

        self.layout.addWidget(self.bar)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def increase_counter(self) -> None:
        """
        Adds progress bar value
        """
        new_value = self.bar.value() + 1
        self.bar.setValue(new_value)
        self.update_label(str(round(new_value / self.bar.maximum() * 100)) + "%")
        self.logger.debug("Update progress bar value: %s", new_value)

    def set_max_value(self, v: int) -> None:
        """
        Updates max possible value in bar

        :param v: new value
        """
        self.bar.setMaximum(v)
