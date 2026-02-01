from collections import defaultdict
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from typing import Dict, List, Optional, Literal, Union

from frozendict import frozendict
from more_itertools.more import last
from PyQt6 import QtWidgets as QtW
from PyQt6.QtCore import Qt, pyqtSignal, QCoreApplication
from PyQt6.QtGui import QKeySequence, QAction
from yaml import safe_load

from src.settings import settings
from src.transcriber.schemas import ModelSettings
from src.ui.elements.selectors import LanguageSelector, PresetSelector


@dataclass(eq=False, repr=False, frozen=False, order=False)
class FileData:
    """
    Imported file properties for transcription
    """

    priority: int = 0
    preset: Optional[ModelSettings] = None
    language: str = None
    fp16: bool = False
    condition_on_previous_text: bool = False
    word_timestamps: bool = False


class AudioFilesTable(QtW.QWidget):
    COLUMNS = (
        QCoreApplication.tr("File"),
        QCoreApplication.tr("Language"),
        QCoreApplication.tr("Preset"),
        QCoreApplication.tr("Word timestamps"),
        QCoreApplication.tr("Condition on previous text"),
        QCoreApplication.tr("FP16"),
    )
    has_files_changed = pyqtSignal(bool)

    def __init__(self, languages: Dict[str, str], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logger = getLogger(self.__class__.__name__)
        self.languages = frozendict(languages)

        self._files: Dict[Path, FileData] = defaultdict(FileData)
        self.model_settings_presets: List[ModelSettings] = self.load_model_settings_presets()

        self.table: QtW.QTableWidget = self.get_table()
        self.add_button: QtW.QPushButton = QtW.QPushButton(self.tr("Add"))
        self.remove_button: QtW.QPushButton = QtW.QPushButton(self.tr("Remove"))

        self.open_file_action = QAction(self.tr("Add audio"), self)
        self.open_file_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_file_action.triggered.connect(self.handle_add_button_click)

        self.delete_files_action = QAction(self.tr("Remove selected audio files"), self.table)
        self.delete_files_action.setShortcuts(QKeySequence.StandardKey.Delete)
        self.delete_files_action.triggered.connect(self.handle_remove_button_click)
        self.delete_files_action.setEnabled(False)

        self.setLayout(self.get_layout())

    @property
    def files(self) -> Dict[Path, FileData]:
        """
        Files loaded by user to process

        :return: collection of files with their properties
        """
        return self._files

    @property
    def ordered_files(self) -> Dict[Path, FileData]:
        """
        Files ordered by priority

        :return:
        """
        return dict(sorted(self.files.items(), key=lambda x: x[1].priority))

    @files.setter
    def files(self, v: Dict[Path, FileData]) -> None:
        """
        Sets files collection and updates table contents and visibility

        :param v: new collection
        """
        self._files = v
        self.has_files_changed.emit(len(self._files) > 0)
        self.table = self.get_table(self.table)

    def get_layout(self) -> QtW.QVBoxLayout:
        """
        Creates layout for file selection: top label, table with files and action buttons

        :return: layout
        """
        buttons = self.get_buttons()

        layout = QtW.QVBoxLayout()
        layout.addWidget(QtW.QLabel("<b>" + self.tr("Add files") + "</b>"))
        layout.addWidget(self.table)
        layout.addWidget(buttons)

        layout.setContentsMargins(0, 10, 0, 0)
        return layout

    def get_table(self, table: Optional[QtW.QTableWidget] = None) -> QtW.QTableWidget:
        """
        Creates table to configure files and their languages

        :param table: existing table to update
        :return: configured table
        """
        if table is None:
            table = QtW.QTableWidget()
            table.setMinimumHeight(200)
        else:
            table.clear()

        table.setColumnCount(len(self.COLUMNS))
        table.setHorizontalHeaderLabels(self.COLUMNS)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setRowCount(len(self.files))

        for i, (file, file_data) in enumerate(self.ordered_files.items()):
            language_selector = LanguageSelector(languages=self.languages)
            # Set selected language as default
            language_selector_text = (
                self.languages[file_data.language].capitalize() if file_data.language else self.tr("Undefined")
            )
            language_selector.setCurrentText(language_selector_text)
            # Connect input handler
            language_selector.currentTextChanged.connect(
                lambda changed: self.handle_file_property_change("language", changed, file)
            )

            preset_selector = PresetSelector(presets=self.model_settings_presets)
            # Set selected preset as default
            preset_selector.setCurrentText(file_data.preset.name)
            # Connect input handler
            preset_selector.currentTextChanged.connect(
                lambda changed: self.handle_file_property_change("preset", changed, file)
            )

            table.setCellWidget(i, 0, QtW.QLabel(str(file.name)))
            table.setCellWidget(i, 1, language_selector)
            table.setCellWidget(i, 2, preset_selector)

            for j, checkbox_field in enumerate(("word_timestamps", "condition_on_previous_text", "fp16")):
                checkbox = QtW.QCheckBox()
                checkbox.setChecked(getattr(file_data, checkbox_field))
                checkbox.checkStateChanged.connect(
                    lambda changed, field=checkbox_field, file_=file: self.handle_file_property_change(
                        field, changed.value > 0, file_
                    )
                )
                table.setCellWidget(i, j + 3, checkbox)

        table.setSelectionMode(QtW.QAbstractItemView.SelectionMode.MultiSelection)
        table.setSelectionBehavior(QtW.QAbstractItemView.SelectionBehavior.SelectRows)
        table.resizeColumnsToContents()

        table.clearSelection()
        table.itemSelectionChanged.connect(self.switch_remove_button_enabled)

        return table

    def get_buttons(self) -> QtW.QWidget:
        """
        Configures add and remove buttons and creates layout for them

        :return: buttons horizontal layout
        """
        # Connect signals
        self.add_button.clicked.connect(self.handle_add_button_click)
        self.remove_button.clicked.connect(self.handle_remove_button_click)
        self.switch_remove_button_enabled()

        w = QtW.QWidget()
        layout = QtW.QHBoxLayout(w)
        layout.addWidget(self.add_button)
        layout.addStretch(1)
        layout.addWidget(self.remove_button)
        layout.setContentsMargins(*([0] * 4))

        return w

    def handle_add_button_click(self) -> None:
        """
        Creates file dialog for user to select audio files to add.
        Only saves new user input adding them at the end of the current list

        If any file is already loaded, uses last loaded file directory
        as a directory for file dialog
        """
        dialog = QtW.QFileDialog()
        dialog.setNameFilters(["*.mp3"])

        # Open last used directory by default
        if (last_file := last(self.ordered_files, None)) is not None:
            dialog.setDirectory(str(last_file.parent))

        if dialog.exec() == 1:
            selected = list(map(Path, dialog.selectedFiles()))
            new_ = list(filter(lambda x: x not in self.files, selected))
            self.logger.info("Selected new files (%s): %s", len(new_), new_)

            priority = len(self.files)
            universal_preset = next(preset for preset in self.model_settings_presets if preset.name == "universal")
            self.files = {
                **self.files,
                **{file: FileData(priority=priority + i, preset=universal_preset) for i, file in enumerate(new_)},
            }

    def handle_remove_button_click(self) -> None:
        """
        Selected files to delete depending on selected table rows
        and removes them from files. Updates remaining priorities,
        so that they remain continuous
        """
        selected_indices = set(map(lambda x: x.row(), self.table.selectedIndexes()))
        self.logger.debug("Selected indices to remove: %s", selected_indices)
        if len(selected_indices) == 0:
            return

        # Delete items
        target_files = set(map(lambda x: x[0], (filter(lambda x: x[1].priority in selected_indices, self.files.items()))))
        for file in target_files:
            del self.files[file]
        self.logger.info("Removed files from queue: %s", set(map(lambda f: f.name, target_files)))

        # Update files priorities
        ordered_remaining_files = dict(sorted(self.files.items(), key=lambda x: x[1].priority))
        for i, file in enumerate(ordered_remaining_files):
            ordered_remaining_files[file].priority = i
        self.files = ordered_remaining_files  # it also updates table

    def handle_file_property_change(
        self,
        name: Literal["language", "preset", "word_timestamps", "condition_on_previous_text", "fp16"],
        value: Union[str, bool],
        file: Path,
    ) -> None:
        """
        Updates internal files settings according to new user input

        Preset inherits values from separate selectors. Once preset changes,
        outer values (language, fp16, etc.) are set automatically

        :param name: property name
        :param value: language name
        :param file: file to update
        """
        if file not in self.files:
            self.logger.warning("File not found in files: %s", file)
            return

        if name == "language":
            language_code = next((code for code, v in self.languages.items() if v.lower() == value.lower()), None)
            self.files[file].language = language_code
            self.files[file].preset.language = language_code
            self.logger.debug("Updated file language: %s <- %s", language_code, file.name)
        elif name in ["word_timestamps", "condition_on_previous_text", "fp16"]:
            setattr(self.files[file], name, value)
            setattr(self.files[file].preset, name, value)
            self.logger.debug("Updated file %s: %s <- %s", name, value, file.name)
        elif name == "preset":
            preset = next(preset for preset in self.model_settings_presets if preset.name == value)
            # Inherit properties from separate fields
            for prop in ["language", "fp16", "word_timestamps", "condition_on_previous_text"]:
                setattr(preset, prop, getattr(self.files[file], prop))
            self.files[file].preset = preset
            self.logger.debug("Updated file preset: %s <- %s", preset, file.name)
        else:
            self.logger.warning("Unable to update %s", name)

    def switch_remove_button_enabled(self, *args, **kwargs) -> None:
        """
        Changes remove files button depending on current table contents and its selection range
        """
        status = self.table.rowCount() > 0 and len(self.table.selectedIndexes()) > 0
        if not self.remove_button.isEnabled() is status:
            self.remove_button.setEnabled(status)
            self.delete_files_action.setEnabled(status)
            self.logger.debug("Switched remove button enabled status: %s", status)

    def clear_files(self) -> None:
        """
        Resets internal files collection
        """
        self.files = defaultdict(FileData)
        self.logger.info("Removed all files")

    @staticmethod
    def load_model_settings_presets() -> List[ModelSettings]:
        """
        Loads model settings presets from YAML file

        :return: model settings presets
        """
        with open(settings.STATIC_DIR / "presets.yaml", mode="r", encoding="utf-8") as file:
            data = safe_load(file.read())
        return list(map(lambda x: ModelSettings(**x), data["presets"]))
