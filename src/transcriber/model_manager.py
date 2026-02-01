from logging import getLogger
from typing import Iterable, Optional, Tuple

import whisper
from yaml import safe_load

from src.settings import settings
from .schemas import WhisperModel


class ModelManager:
    MODELS_FILE = settings.STATIC_DIR / "models.yaml"

    def __init__(self) -> None:
        self.logger = getLogger(self.__class__.__name__)

        self._model: Optional[whisper.Whisper] = None
        self._model_description: Optional[WhisperModel] = None
        self._available_models: Optional[Tuple[WhisperModel, ...]] = None

    @property
    def model(self) -> whisper.Whisper:
        """
        Returns assigned whisper model, if any

        :return: whisper
        :raise AttributeError: model not set
        """
        if self._model is None:
            raise AttributeError("Whisper model has not been assigned yet")
        return self._model

    @model.setter
    def model(self, v: whisper.Whisper) -> None:
        """
        Sets provided whisper model as a target model to use in the object

        :param v: new whisper model
        :raise TypeError: invalid model type
        """
        if not isinstance(v, whisper.Whisper):
            raise TypeError(f"Cannot assign {type(v)} to model")

        if self._model is not None:
            self.logger.warning("Reassigning whisper model")
        self._model = v
        self.logger.debug("Assigned whisper model")

    @property
    def default_model(self) -> WhisperModel:
        """
        Returns first model marked as default out of available models,
        if any is marked, or just the first model

        :return: default model to use
        """
        try:
            return next(model for model in self.available_models if model.is_default)
        except StopIteration:
            return self.available_models[0]

    @property
    def available_models(self) -> Tuple[WhisperModel, ...]:
        """
        Available models metadata information

        :return: list of available Whisper models
        """
        if self._available_models is None:
            self.available_models = self.load_available_models()
        return self._available_models

    @available_models.setter
    def available_models(self, v: Iterable[WhisperModel]) -> None:
        """
        Sets available models

        Prohibits to reassign property to an existent object of a class
        and validates input models to be of a WhisperModel class

        :param v: new value
        :raise AttributeError: attempt to reassign value
        :raise TypeError: none of the values in the list is a valid model
        :raise ValueError: models are duplicated
        """
        if self._available_models is not None:
            raise AttributeError("Cannot reassign models in existing manager")

        valid_models = tuple(filter(lambda x: isinstance(x, WhisperModel), v))
        if len(valid_models) == 0:
            raise TypeError("None of the provided values is a valid WhisperModel object")
        if len({model.name for model in v}) < len(valid_models):
            raise ValueError("Models are duplicated by name")

        self._available_models = valid_models
        self.logger.debug("Available models loaded from yaml file: %s", self.MODELS_FILE)

    @classmethod
    def load_available_models(cls) -> Tuple[WhisperModel, ...]:
        """
        Loads available models information from a static YAML file

        :return: available models information
        """
        with open(cls.MODELS_FILE) as file:
            data = safe_load(file.read())["available"]
        return tuple(map(lambda x: WhisperModel(**x), data))

    @staticmethod
    def load_model(model: WhisperModel) -> whisper.Whisper:
        """
        Loads model via `whisper` methods

        :param model: model description
        :returns: whisper
        """
        return whisper.load_model(name=model.name, download_root=settings.CACHE_DIR)
