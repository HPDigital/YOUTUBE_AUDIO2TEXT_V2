from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import List, Optional

from pydub import AudioSegment
from pydub.silence import split_on_silence


def ensure_wav(input_path: str | os.PathLike, out_dir: str | os.PathLike | None = None, sample_rate: int = 16000) -> Path:
    """
    Asegura que un archivo de audio esté en formato WAV con un sample rate deseado.

    Si el archivo ya es WAV, intenta normalizar el sample rate si es distinto.

    Returns la ruta del archivo WAV resultante.
    """
    input_path = Path(input_path)
    out_dir = Path(out_dir) if out_dir else input_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    target = out_dir / (input_path.stem + ".wav")

    # Cargar con pydub (requiere FFmpeg)
    audio = AudioSegment.from_file(input_path)
    if audio.frame_rate != sample_rate:
        audio = audio.set_frame_rate(sample_rate)
    audio = audio.set_channels(1)  # mono para reconocimiento
    audio.export(target, format="wav")
    return target


def split_wav_on_silence(
    wav_path: str | os.PathLike,
    min_silence_len: int = 700,
    silence_thresh: Optional[int] = None,
    keep_silence: int = 300,
    max_chunk_ms: int = 60_000,
) -> List[Path]:
    """
    Divide un WAV en fragmentos usando silencios y un tamaño máximo.

    - `silence_thresh` en dBFS; si None, calcula relativo al audio.
    - Limita cada fragmento a `max_chunk_ms` para evitar límites del servicio.
    """
    wav_path = Path(wav_path)
    audio = AudioSegment.from_wav(wav_path)

    # Calcular umbral de silencio relativo si no se provee
    if silence_thresh is None:
        silence_thresh = int(audio.dBFS - 16)

    raw_chunks = split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence,
    )

    # Forzar límite de duración por chunk
    def _slice_to_max(seg: AudioSegment, max_ms: int) -> List[AudioSegment]:
        if len(seg) <= max_ms:
            return [seg]
        return [seg[i : i + max_ms] for i in range(0, len(seg), max_ms)]

    chunks: List[AudioSegment] = []
    for seg in (raw_chunks if raw_chunks else [audio]):
        chunks.extend(_slice_to_max(seg, max_chunk_ms))

    out_dir = Path(tempfile.mkdtemp(prefix="chunks_"))
    out_paths: List[Path] = []
    for idx, seg in enumerate(chunks, start=1):
        out_file = out_dir / f"chunk_{idx:03d}.wav"
        seg.export(out_file, format="wav")
        out_paths.append(out_file)
    return out_paths

