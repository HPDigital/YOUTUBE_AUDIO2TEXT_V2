"""
yt_audio2text: Descarga audio de YouTube o procesa archivos locales
y convierte el contenido a texto usando SpeechRecognition (Google Web Speech).

Requiere FFmpeg instalado y disponible en PATH para conversiones de audio.
"""

__all__ = [
    "download_youtube_audio",
    "ensure_wav",
    "split_wav_on_silence",
    "Transcriber",
]
