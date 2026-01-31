from logging import getLogger
from pathlib import Path

import numpy as np
import webrtcvad
from scipy.signal import resample_poly, butter, lfilter
import soundfile as sf


class AudioPreprocessor:
    eps: float = 1e-9
    frame_ms: int = 30

    def __init__(self) -> None:
        self.logger = getLogger(self.__class__.__name__)

    def run(self, path: Path, target_sr: int = 16_000, vad_aggressiveness: int = 2) -> np.ndarray:
        """
        Runs complete pipeline to preprocess audio data before giving it to Whisper

        :param path: path to audio file
        :param target_sr:
        :param vad_aggressiveness:
        :return: processed audio file
        """
        return self.apply_vad(
            self.highpass_denoise(self.normalize(self.load_file(path, target_sr=target_sr)), sr=target_sr),
            sr=target_sr,
            aggressiveness=vad_aggressiveness,
        )

    def load_file(self, path: Path, target_sr: int = 16_000) -> np.ndarray:
        """
        Loads audio file, converts it to mono channel and resamples to target SR

        :param path: audio path
        :param target_sr: target SR
        :return: audio data
        """
        audio, sr = sf.read(path.resolve(), always_2d=False)

        if audio.ndim > 1:
            self.logger.debug("Converting to mono channel from %s channels", audio.ndim)
            audio = np.mean(audio, axis=1)

        if sr != target_sr:
            audio = resample_poly(audio, up=target_sr, down=sr)
            self.logger.debug("Resampling from %s to %", sr, target_sr)

        return audio.astype(np.float64)

    def normalize(self, audio: np.ndarray) -> np.ndarray:
        """
        Normalizes audio range by min-max scaling

        :param audio: audio data
        :return: normalized data
        """
        ratio = np.max(np.abs(audio)) + self.eps
        return audio / ratio

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
        return lfilter(b, a, audio)

    def apply_vad(self, audio: np.ndarray, sr: int = 16_000, aggressiveness: int = 2) -> np.ndarray:
        """
        Cuts out silence elements to speed up Whisper processing

        :param audio: audio data
        :param sr:
        :param aggressiveness: VAD mode
        :return: audio with no-speech pieces removed
        """
        vad = webrtcvad.Vad(aggressiveness)

        frame_length = int(sr * self.frame_ms / 1_000)

        audio_int16 = (audio * 32768).astype(np.int16)
        voiced = []
        for i in range(0, len(audio_int16) - frame_length, frame_length):
            frame = audio_int16[i : i + frame_length].tobytes()
            if vad.is_speech(frame, sr):
                # Save original piece of audio file
                voiced.append(audio[i : i + frame_length])

        # Let whisper try it anyway
        if len(voiced) == 0:
            self.logger.warning("Did not manage to extract speeched pieces from audio")
            return audio

        audio_vad = np.concatenate(voiced)
        self.logger.warning("Applied VAD: %s -> %s", audio.shape, audio_vad.shape)
        return audio_vad
