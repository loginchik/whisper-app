from logging import getLogger
from pathlib import Path
from typing import Literal, Tuple

import numpy as np
from scipy.signal import resample_poly, butter, lfilter
import soundfile as sf


class AudioPreprocessor:
    eps: float = 1e-9
    frame_ms: int = 30

    def __init__(self) -> None:
        self.logger = getLogger(self.__class__.__name__)

    def run(
        self,
        path: Path,
        preset: Literal["universal", "studio", "phone_call", "dictophone", "outdoors", "music"],
        target_sr: int = 16_000,
    ) -> Tuple[np.ndarray, bool]:
        """
        Runs complete pipeline to preprocess audio data before giving it to Whisper

        Changes processing pipeline and stages parameters depending on user defined preset

        :param path: path to audio file
        :param preset: preset name
        :param target_sr:
        :return: processed audio file, whether VAD was used
        """
        normalized_audio = self.normalize(self.load_file(path, target_sr))
        if preset == "universal":
            return normalized_audio, False

        if preset == "studio":
            return self.apply_vad(normalized_audio, sr=target_sr, threshold=0.006, pad_ms=200), True

        if preset == "phone_call":
            return self.apply_vad(
                self.highpass_denoise(normalized_audio, target_sr, 150), target_sr, threshold=0.02, pad_ms=300
            ), True

        if preset == "dictophone":
            return self.apply_vad(
                self.highpass_denoise(normalized_audio, target_sr, 80), target_sr, threshold=0.012, pad_ms=250
            ), True

        if preset == "outdoors":
            return self.apply_vad(
                self.highpass_denoise(normalized_audio, target_sr, 200), target_sr, threshold=0.04, pad_ms=350
            ), True

        if preset == "music":
            return self.apply_vad(
                self.highpass_denoise(normalized_audio, target_sr, 120), target_sr, threshold=0.06, pad_ms=400
            ), True

        raise ValueError("Unable to process preset %s" % preset)

    def load_file(self, path: Path, target_sr: int = 16_000) -> np.ndarray:
        """
        Loads audio file, converts it to mono channel and resamples to target SR

        :param path: audio path
        :param target_sr: target SR
        :return: audio data
        """
        audio, sr = sf.read(path.resolve(), always_2d=False, dtype="float32")

        if audio.ndim > 1:
            self.logger.debug("Converting to mono channel from %s channels", audio.ndim)
            audio = np.mean(audio, axis=1)

        if sr != target_sr:
            audio = resample_poly(audio, up=target_sr, down=sr)
            self.logger.debug("Resampling from %s to %s", sr, target_sr)

        return audio.astype(np.float32)

    def normalize(self, audio: np.ndarray) -> np.ndarray:
        """
        Normalizes audio range by min-max scaling

        :param audio: audio data
        :return: normalized data
        """
        ratio = np.max(np.abs(audio)) + self.eps
        return (audio / ratio).astype(np.float32)

    @staticmethod
    def highpass_denoise(audio: np.ndarray, sr: int = 16_000, cutoff: int = 80) -> np.ndarray:
        """
        Applies high-pass denoise to (normalized) data

        :param audio: normalized audio data
        :param sr:
        :param cutoff:
        :return: denoised audio data
        """
        b, a = butter(2, cutoff / (sr / 2), btype="highpass")
        return lfilter(b, a, audio).astype(np.float32)

    def apply_vad(self, audio: np.ndarray, sr: int = 16_000, threshold: float = 0.1, pad_ms: int = 200) -> np.ndarray:
        """
        Cuts out silence elements to speed up Whisper processing

        :param audio: audio data
        :param sr:
        :param threshold:
        :param pad_ms:
        :return: audio with no-speech pieces removed
        """
        frame_len = int(sr * self.frame_ms / 1_000)
        # Get energy per frame
        frames = audio[: len(audio) // frame_len * frame_len]
        frames = frames.reshape(-1, frame_len)
        energy = np.mean(frames**2, axis=1)

        # Create mask that seems to be speeched
        mask = energy > threshold
        # Widen mask not to cut off beginnings and endings of words
        pad = int(pad_ms / self.frame_ms)
        for i in range(1, pad + 1):
            mask[:-i] |= mask[i:]
            mask[i:] |= mask[:-i]

        # Get voiced pieces
        voiced = frames[mask]

        if len(voiced) == 0:
            return audio  # Let whisper process the original file

        voiced = voiced.reshape(-1)
        self.logger.debug("Applied VAD: %s -> %s", audio.shape, voiced.shape)
        return voiced.astype(np.float32)
