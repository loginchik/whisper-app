from logging import getLogger
from pathlib import Path

import PyQt6.QtWidgets as QtW
from PyQt6.QtCore import Qt

from src.ui.elements.tables import FileList
from src.ui.elements.labels import ProcessLabel, ProgressBarLabel


class TranscribedFilesList(QtW.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logger = getLogger(self.__class__.__name__)

        self.list = FileList()
        self.label = ProgressBarLabel(self.tr("Files transcription"))

        layout = QtW.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.list)
        layout.setContentsMargins(*([0] * 4))
        self.setLayout(layout)

    def add_list_item(self, path: Path) -> None:
        """
        Add new item with data to open it in file manager

        :param path: new path
        """
        self.list.add_list_item(path)
        self.label.increase_counter()


class TaskWindow(QtW.QDialog):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logger = getLogger(self.__class__.__name__)
        self.__files_count = 0

        self.setWindowTitle(self.tr("Running task"))

        self.model_label = ProcessLabel(self.tr("Model preparation"), self.tr("Loading"))
        self.prepared_files_counter = ProgressBarLabel(self.tr("Files preparation"))
        self.transcribed_files_list = TranscribedFilesList()

        self.task_complete_label = QtW.QLabel(self.tr("Task complete"))
        self.task_complete_label.setVisible(False)

        layout = QtW.QVBoxLayout()
        layout.addWidget(self.model_label)
        layout.addStretch(1)
        layout.addWidget(self.prepared_files_counter)
        layout.addWidget(self.transcribed_files_list)
        layout.addStretch(1)
        layout.addWidget(self.transcribed_files_list)
        layout.addWidget(self.task_complete_label)

        self.setLayout(layout)
        self.setMinimumSize(200, 200)
        self.resize(350, 350)

    @property
    def files_count(self) -> int:
        return self.__files_count

    @files_count.setter
    def files_count(self, v: int) -> None:
        """
        Updates files count value

        :param v: new files count
        """
        if not isinstance(v, int):
            raise TypeError(f"Cannot use type {type(v)} as int")
        self.__files_count = v

        self.transcribed_files_list.label.set_max_value(v)
        self.prepared_files_counter.set_max_value(v)
        self.logger.debug("Updated files count: %s", v)

    def handle_model_ready(self, signal: bool) -> None:
        """
        Updates model status label depending on incoming signal

        :param signal: user signal
        """
        new_label = self.tr("Ready") if signal else self.tr("Loading")
        self.model_label.update_label(new_label)

    def handle_file_prepared(self, signal: int) -> None:
        """
        Increases prepared files counter

        :param signal: incoming signal
        """
        self.prepared_files_counter.increase_counter()

    def handle_file_transcribed(self, signal: Path) -> None:
        """
        Updates transcribed file elements with new processed path

        :param signal: new path
        """
        self.transcribed_files_list.add_list_item(signal)

    def handle_task_complete(self, signal: bool) -> None:
        """
        Shows/hides task complete label depending on new signal

        :param signal: incoming signal
        """
        if signal:
            self.task_complete_label.setVisible(True)

    def closeEvent(self, event) -> None:
        """
        Prevent modal window from closure, if task is still pending

        :param event: close event
        """
        if not self.task_complete_label.isVisible():
            event.ignore()
            self.setWindowState(Qt.WindowState.WindowMinimized)
            self.logger.warning("Prevent running task from closing")
            return
