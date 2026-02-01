from logging import getLogger
from typing import Tuple

import PyQt6.QtWidgets as QtW
from PyQt6.QtGui import QAction

from src.transcriber import Transcriber
from src.transcriber.schemas import WhisperModel
from .elements.tables import AudioFilesTable
from .elements.selectors import ModelsSelector
from .elements.labels import InformationLabel
from .windows import TaskWindow, ModelsWindow, AboutWindow
from .bg import ProcessManager


class MainWindowHeading(QtW.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        information = InformationLabel(self.tr("App name"))
        information.add_paragraph(
            self.tr(
                "Note, that the application just wraps OpenAI model. Besides model downloading, <b>all processes run "
                "locally</b>, so the performance highly depends on your machine resources"
            )
        )

        layout = QtW.QVBoxLayout()
        layout.addWidget(information)
        layout.setContentsMargins(*([0] * 4))
        self.setLayout(layout)


class ModelsSelectionLayout(QtW.QWidget):
    def __init__(self, available_models: Tuple[WhisperModel, ...], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.model_selector: ModelsSelector = ModelsSelector().fill(available_models)

        about_window = ModelsWindow(available_models)
        about_button = QtW.QPushButton(self.tr("About models"))
        about_button.clicked.connect(lambda _: about_window.show())

        row_layout = QtW.QHBoxLayout()
        row_layout.addWidget(self.model_selector)
        row_layout.addStretch(1)
        row_layout.addWidget(about_button)
        row_layout.setContentsMargins(*([0] * 4))
        row = QtW.QWidget()
        row.setLayout(row_layout)

        layout = QtW.QVBoxLayout()
        layout.addWidget(QtW.QLabel("<b>" + self.tr("Choose model") + "</b>"))
        layout.addWidget(row)
        layout.setContentsMargins(0, 10, 0, 0)
        self.setLayout(layout)

    @property
    def current_model(self) -> str:
        """
        Returns current selected value

        :return: name of a model
        """
        return self.model_selector.currentText()

    def freeze(self) -> None:
        self.model_selector.setEnabled(False)

    def unfreeze(self) -> None:
        self.model_selector.setEnabled(True)


class MainWindow(QtW.QMainWindow):
    """
    Main application window

    Runs all business logic of the application, including process management
    and child windows creation and closure
    """

    def __init__(self) -> None:
        super().__init__()
        self.logger = getLogger(self.__class__.__name__)
        self.transcriber: Transcriber = Transcriber()
        self.process_manager: ProcessManager = ProcessManager(transcriber=self.transcriber)
        self.process_manager.signal_task_completed.connect(self.unfreeze)

        self.model_selection_block = ModelsSelectionLayout(self.transcriber.available_models, parent=self)
        self.file_selector_table: AudioFilesTable = AudioFilesTable(languages=self.transcriber.load_available_languages())

        self.running_task_window: TaskWindow = TaskWindow(parent=self)
        self.process_manager.signal_model_loaded.connect(self.running_task_window.handle_model_ready)
        self.process_manager.signal_file_prepared.connect(self.running_task_window.handle_file_prepared)
        self.process_manager.signal_file_transcribed.connect(self.running_task_window.handle_file_transcribed)
        self.process_manager.signal_task_completed.connect(self.running_task_window.handle_task_complete)

        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(self.file_selector_table.open_file_action)
        file_menu.addAction(self.file_selector_table.delete_files_action)

        about_menu = menu.addMenu("&Help")
        about_action = QAction(self.tr("About"), self)
        about_action.triggered.connect(self.show_about_window)
        about_menu.addAction(about_action)

        self.start_button = QtW.QPushButton(self.tr("Start"))
        self.start_button.clicked.connect(self.run_task)
        self.start_button.setEnabled(False)
        self.file_selector_table.has_files_changed.connect(lambda changed: self.start_button.setEnabled(changed))

        layout = QtW.QVBoxLayout()
        layout.addWidget(MainWindowHeading())
        layout.addWidget(self.model_selection_block)
        layout.addWidget(self.file_selector_table)
        layout.addWidget(self.start_button)

        widget = QtW.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.set_window_size()
        self.setWindowTitle(self.tr("App name"))

    def on_quit(self) -> None:
        """
        Stops running background tasks before application quit
        """
        self.process_manager.pool.shutdown(cancel_futures=True, wait=False)
        self.logger.info("Process pool shutdown")
        self.logger.info("App quit")

    def run_task(self) -> None:
        """
        Freezes application and starts background tasks to process
        current specified parameters
        """
        self.logger.info("Starting task")
        self.freeze()

        files_count = len(self.file_selector_table.files)
        self.running_task_window.files_count = files_count
        self.running_task_window.show()

        # Prepare for task start
        self.process_manager.pending = files_count + 1

        model_desc = next(
            model for model in self.transcriber.available_models if model.name == self.model_selection_block.current_model
        )
        self.process_manager.submit_load_model(model_desc)
        self.process_manager.submit_prepare_files(self.file_selector_table.files)

    def freeze(self) -> None:
        """
        Block all elements that must not be touched during transcription
        """
        self.model_selection_block.freeze()
        self.file_selector_table.setEnabled(False)
        self.start_button.setEnabled(False)
        self.logger.info("Freeze application")

    def unfreeze(self) -> None:
        """
        Unblock previously blocked elements
        """
        self.model_selection_block.unfreeze()
        self.file_selector_table.clear_files()
        self.file_selector_table.setEnabled(True)
        self.logger.info("Unfreeze application")

    def set_window_size(self) -> None:
        """
        Updates size boundaries for the window element
        """
        self.setMinimumSize(400, 400)
        self.adjustSize()

    def show_about_window(self) -> None:
        AboutWindow(self).exec()
