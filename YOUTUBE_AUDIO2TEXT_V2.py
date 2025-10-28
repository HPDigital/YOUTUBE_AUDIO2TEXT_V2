#!/usr/bin/env python
# coding: utf-8

"""
YOUTUBE_AUDIO2TEXT_V2 (refactorizado)

Este script ahora actúa como un pequeño CLI y punto de entrada
para lanzar la interfaz gráfica.

Comandos:
  - python YOUTUBE_AUDIO2TEXT_V2.py --gui
  - python YOUTUBE_AUDIO2TEXT_V2.py --url <YouTubeURL> [--lang es-ES]
  - python YOUTUBE_AUDIO2TEXT_V2.py --file <ruta_audio_o_video> [--lang es-ES]
"""

import argparse
from pathlib import Path

from yt_audio2text.downloader import download_youtube_audio
from yt_audio2text.audio_utils import ensure_wav, split_wav_on_silence
from yt_audio2text.transcriber import Transcriber
from yt_audio2text.gui import run as run_gui


def transcribe_youtube(url: str, lang: str) -> Path:
    downloads = Path("downloads")
    outputs = Path("outputs")
    downloads.mkdir(exist_ok=True)
    outputs.mkdir(exist_ok=True)

    audio = download_youtube_audio(url, downloads, fmt="wav", sample_rate=16000)
    wav = ensure_wav(audio, out_dir=outputs, sample_rate=16000)
    chunks = split_wav_on_silence(wav, max_chunk_ms=60_000)
    tr = Transcriber(language=lang)
    if len(chunks) <= 1:
        text = tr.transcribe_wav(wav)
    else:
        text = tr.transcribe_chunks(chunks)
    out = outputs / f"transcripcion_{wav.stem}.txt"
    out.write_text(text, encoding="utf-8")
    return out


def transcribe_file(path: Path, lang: str) -> Path:
    outputs = Path("outputs")
    outputs.mkdir(exist_ok=True)
    wav = ensure_wav(path, out_dir=outputs, sample_rate=16000)
    chunks = split_wav_on_silence(wav, max_chunk_ms=60_000)
    tr = Transcriber(language=lang)
    if len(chunks) <= 1:
        text = tr.transcribe_wav(wav)
    else:
        text = tr.transcribe_chunks(chunks)
    out = outputs / f"transcripcion_{wav.stem}.txt"
    out.write_text(text, encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="YouTube/Audio -> Texto")
    parser.add_argument("--gui", action="store_true", help="Lanza la interfaz gráfica")
    parser.add_argument("--url", type=str, help="URL de YouTube")
    parser.add_argument("--file", type=str, help="Ruta de archivo local (audio/video)")
    parser.add_argument("--lang", type=str, default="es-ES", help="Idioma, ej. es-ES, en-US")
    args = parser.parse_args()

    if args.gui or (not args.url and not args.file):
        run_gui()
        return

    if args.url:
        out = transcribe_youtube(args.url, args.lang)
        print(f"Transcripción guardada en: {out}")
        return

    if args.file:
        out = transcribe_file(Path(args.file), args.lang)
        print(f"Transcripción guardada en: {out}")
        return


if __name__ == "__main__":
    main()

