from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Iterable, Optional

import speech_recognition as sr


ProgressCb = Optional[Callable[[str, float], None]]  # (message, progress 0..1)


class Transcriber:
    def __init__(self, language: str = "es-ES") -> None:
        self.language = language
        self.recognizer = sr.Recognizer()

    def _emit(self, cb: ProgressCb, message: str, progress: float) -> None:
        if cb:
            cb(message, progress)

    def transcribe_wav(self, wav_path: str | os.PathLike, progress_cb: ProgressCb = None) -> str:
        wav_path = Path(wav_path)
        with sr.AudioFile(str(wav_path)) as source:
            self._emit(progress_cb, "Ajustando ruido ambiente...", 0.05)
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.record(source)

        self._emit(progress_cb, "Enviando a servicio de reconocimiento...", 0.2)
        text = self.recognize_google(audio, progress_cb)
        return text

    def transcribe_chunks(self, chunk_paths: Iterable[str | os.PathLike], progress_cb: ProgressCb = None) -> str:
        chunk_paths = list(map(Path, chunk_paths))
        total = len(chunk_paths)
        texts: list[str] = []
        for idx, path in enumerate(chunk_paths, start=1):
            with sr.AudioFile(str(path)) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = self.recognizer.record(source)
            piece = self.recognize_google(audio, progress_cb)
            texts.append(piece)
            self._emit(progress_cb, f"Chunk {idx}/{total} transcrito", 0.2 + 0.8 * (idx / max(total, 1)))
        return "\n".join(texts)

    def recognize_google(self, audio: sr.AudioData, progress_cb: ProgressCb = None) -> str:
        try:
            text = self.recognizer.recognize_google(audio, language=self.language)
            return text
        except sr.UnknownValueError:
            self._emit(progress_cb, "No se entendió el audio (silencio/ruido)", 0.2)
            return ""
        except sr.RequestError as e:
            # Error del servicio de Google (requiere internet)
            raise RuntimeError(f"Error del servicio de reconocimiento: {e}")

