from logging import getLogger
from pathlib import Path
import subprocess
from sys import platform

import PyQt6.QtWidgets as QtW
from PyQt6.QtCore import Qt


class FileList(QtW.QListWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logger = getLogger(self.__class__.__name__)

        self.itemDoubleClicked.connect(self.handle_item_double_click)
        self.setMinimumHeight(250)

    def add_list_item(self, path: Path) -> None:
        """
        Add new item with data to open it in file manager

        :param path: new path
        """
        item = QtW.QListWidgetItem(str(path.name))
        item.setData(Qt.ItemDataRole.UserRole + 1, path)
        self.addItem(item)

    def handle_item_double_click(self, item) -> None:
        """
        When user double clicks list item, determines target directory path
        and opens it in system file manager

        :param item: clicked item
        """
        path_to_open = item.data(Qt.ItemDataRole.UserRole + 1)
        if path_to_open is None:
            self.logger.warning("Path not defined in clicked item")
            return

        try:
            subprocess.Popen([self.open_directory_command, path_to_open])
        except ValueError as e:
            self.logger.warning("Unable to open directory: %s", e)

    @property
    def open_directory_command(self) -> str:
        """
        Depending on user platform, determines subprocess command to open directory
        in file manager

        :return: command
        """
        if platform == "darwin":
            return "open"
        elif platform == "win32":
            return "explorer"
        elif platform.startswith("linux"):
            return "xdg-open"
        raise ValueError("Platform is not supported: %s" % platform)
