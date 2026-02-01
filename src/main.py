import logging
from logging.handlers import RotatingFileHandler
import multiprocessing
import sys

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator

from src.ui.app import MainWindow
from src.settings import settings


formatter = logging.Formatter(
    datefmt="%Y-%m-%d %H:%M:%S", fmt="%(asctime)s %(name)s %(module)s:%(funcName)s [%(levelname)s]: %(message)s"
)
if settings.debug:
    handler = logging.StreamHandler()
else:
    settings.LOGGING_DIR.mkdir(exist_ok=True)
    handler = RotatingFileHandler(
        filename=settings.LOGGING_DIR / "logs.log", maxBytes=(1024**2) * 3, backupCount=3, encoding="utf-8"
    )
handler.setFormatter(formatter)

root = logging.getLogger()
root.setLevel(logging.DEBUG if settings.debug else logging.INFO)
root.handlers.clear()
root.addHandler(handler)
logging.getLogger("numba").setLevel("WARNING")


def main() -> None:
    app = QApplication(sys.argv)
    translator = QTranslator()
    translator.load(str(settings.BASE_DIR / "locales" / f"app.qm"))
    app.installTranslator(translator)

    window = MainWindow()
    app.aboutToQuit.connect(window.on_quit)

    root.info("Starting app")
    window.show()
    app.exec()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
