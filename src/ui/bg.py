from concurrent.futures import ProcessPoolExecutor, Future
from logging import getLogger
from pathlib import Path
from typing import Literal, Dict

from PyQt6.QtCore import QObject, pyqtSignal

from src.transcriber import Transcriber, AudioPreprocessor
from src.transcriber.schemas import WhisperModel


STAGES = ("prepare", "transcribe", "clear")


def on_task_complete(stage: Literal["prepare", "transcribe", "clear"]):
    """
    Starts next stage, if current stage has no more pending tasks

    :param stage: current stage
    """
    if stage not in STAGES:
        raise ValueError("Unknown stage: %s", stage)

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self.decrease_pending()

            if self.pending == 0 and stage != "clear":
                self.logger.debug("Ready to start next stage")
                self.run_next_stage(STAGES[STAGES.index(stage) + 1])
            return result

        return wrapper

    return decorator


class ProcessManager(QObject):
    signal_task_completed = pyqtSignal(bool)
    signal_model_loaded = pyqtSignal(bool)
    signal_file_prepared = pyqtSignal(int)
    signal_file_transcribed = pyqtSignal(Path)

    def __init__(self, transcriber: Transcriber, workers: int = 4, **kwargs) -> None:
        super().__init__(**kwargs)
        self.logger = getLogger(self.__class__.__name__)
        self.pool = ProcessPoolExecutor(workers)
        self.logger.debug("Created pool with %s workers", workers)

        self.transcriber = transcriber
        self.__prepared_files = []
        self.__pending_tasks_count = 0

    @property
    def pending(self) -> int:
        """
        Pending tasks count
        """
        return self.__pending_tasks_count

    @pending.setter
    def pending(self, v: int) -> None:
        """
        Checks value type and assigns it to internal property,
        only if current pending count equals 0

        :param v: new pending tasks count
        :raise TypeError: invalid value type
        :raise AttributeError: attempt to reassign pending value != 0
        """
        if not isinstance(v, int):
            raise TypeError(f"Cannot use type {type(v)} as int")

        if self.__pending_tasks_count != 0:
            raise AttributeError("Cannot reassign pending value, when current value != 0")

        self.__pending_tasks_count = v
        self.logger.debug("Set pending tasks count: %s", self.__pending_tasks_count)

    def decrease_pending(self) -> None:
        """
        The only method to decrease pending tasks count
        """
        self.__pending_tasks_count -= 1

    def submit_load_model(self, model: WhisperModel) -> None:
        """
        Creates task to load model via whisper methods

        :param model: model description to load
        """
        self.transcriber._model_description = model
        future = self.pool.submit(Transcriber.load_model, model)
        future.add_done_callback(self.on_model_loaded)

    def submit_prepare_files(self, files: Dict) -> None:
        """
        Creates tasks to prepare audio files via audio processor

        :param files: files to process from file selector
        """
        processor = AudioPreprocessor()
        for file, file_data in files.items():
            future = self.pool.submit(processor, file, file_data.preset)
            future.add_done_callback(self.on_file_prepared)

    def submit_transcribe_files(self, files) -> None:
        for path, audio, preset in files:
            future = self.pool.submit(self.transcriber.transcribe, audio, preset, path)
            future.add_done_callback(self.on_file_transcribed)

    def run_next_stage(self, stage: Literal["transcribe", "clear"]) -> None:
        """
        Starts next stage from internal manager data, if pending tasks count equals 0

        :param stage: stage to start
        """
        if self.pending > 0:
            raise RuntimeError("Cannot start next stage having pending tasks")

        self.logger.info("Stating stage %s", stage)
        if stage == "transcribe":
            self.pending = len(self.__prepared_files)
            self.submit_transcribe_files(self.__prepared_files)

        elif stage == "clear":
            self.logger.info("Tasks complete")
            self.signal_task_completed.emit(True)

    @on_task_complete("prepare")
    def on_model_loaded(self, future: Future) -> None:
        """
        Sets loaded model to transcriber

        :param future: future that was loading model
        """
        model = future.result()
        self.transcriber.model = model

        self.signal_model_loaded.emit(True)
        self.logger.info("Model loaded")

    @on_task_complete("prepare")
    def on_file_prepared(self, future: Future) -> None:
        """
        Processes audio file that is prepared for transcription

        :param future: completed future
        """
        result = future.result()
        self.__prepared_files.append(result)

        self.signal_file_prepared.emit(1)
        self.logger.info("Prepared file: %s - %s - %s", result[0].name, result[2], len(result[1]))

    @on_task_complete("transcribe")
    def on_file_transcribed(self, future: Future) -> None:
        """
        Stores transcribed file in sync mode

        :param future: completed future
        """
        transcription, path, preset = future.result()
        self.logger.info("Transcribed file: %s - %s", path.name, preset)
        export_dir_path = self.transcriber.store_transcription(
            transcription, Path("~/Downloads").expanduser(), path.stem, preset.name != "universal"
        )
        self.signal_file_transcribed.emit(export_dir_path)
        self.logger.info("Saved transcription: %s -> %s", path.name, export_dir_path)
