from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from yt_dlp import YoutubeDL


def download_youtube_audio(
    url: str,
    out_dir: str | os.PathLike,
    filename: Optional[str] = None,
    fmt: str = "wav",
    sample_rate: int = 16000,
) -> Path:
    """
    Descarga el audio de un video de YouTube y lo extrae a un archivo de audio.

    - Usa yt-dlp con postprocesadores de FFmpeg para extraer audio directamente.
    - Requiere ffmpeg instalado y disponible en PATH.

    Args:
        url: URL del video de YouTube.
        out_dir: Carpeta de salida.
        filename: Nombre base del archivo de salida (sin extensión). Si None, usa el título del video.
        fmt: Formato de salida (p.ej., "wav", "mp3").
        sample_rate: Frecuencia de muestreo para el archivo final (Hz).

    Returns:
        Ruta al archivo de audio generado.
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    # Plantilla de nombre de salida
    # yt-dlp añadirá la extensión adecuada luego de post-proceso
    outtmpl = str(Path(out_dir) / (filename or "%(title)s_%(id)s")) + ".%(ext)s"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": fmt,
                "preferredquality": "192",
            },
            {
                "key": "FFmpegMetadata",
            },
        ],
        # Re-muestrear si es WAV
        "postprocessor_args": (
            ["-ar", str(sample_rate)] if fmt.lower() == "wav" else []
        ),
        "quiet": True,
        "noprogress": True,
        "no_warnings": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    # Construir ruta final
    # Si filename fue None, yt-dlp utilizó el título/ID.
    base_name = filename or f"{info.get('title','video')}_{info.get('id','')}".strip("_")
    audio_path = Path(out_dir) / f"{base_name}.{fmt}"

    # Manejo defensivo: si no coincide, buscar por patrón
    if not audio_path.exists():
        candidates = list(Path(out_dir).glob(f"*{info.get('id','')}*.{fmt}"))
        if candidates:
            return candidates[0]

    return audio_path
