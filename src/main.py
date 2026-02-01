from logging import basicConfig, getLogger
import multiprocessing
import sys

from PyQt6.QtWidgets import QApplication

from src.ui.app import MainWindow
from src.settings import settings


basicConfig(
    level="DEBUG" if settings.debug else "INFO",
    format="%(asctime)s %(name)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
getLogger("numba").setLevel("WARNING")


def main() -> None:
    app = QApplication(sys.argv)

    window = MainWindow()
    app.aboutToQuit.connect(window.on_quit)

    window.show()
    app.exec()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
