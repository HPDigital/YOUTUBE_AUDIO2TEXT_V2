# YOUTUBE_AUDIO2TEXT_V2

Convierte audio de YouTube o archivos locales a texto usando SpeechRecognition (Google Web Speech) con una interfaz gráfica en Tkinter.

## Características
- Descarga audio de YouTube y lo convierte a WAV.
- Transcribe audios locales (wav, mp3, mp4, m4a, etc.).
- Segmentación automática por silencios para audios largos.
- Interfaz gráfica sencilla (Tkinter) y CLI opcional.

## Requisitos
1) Python 3.9+
2) FFmpeg instalado y disponible en PATH (requerido por `pydub` y conversiones)
3) Dependencias Python
```bash
pip install -r requirements.txt
```

> Nota: La transcripción usa el servicio de Google de `SpeechRecognition`, por lo que requiere conexión a internet en tiempo de ejecución.

## Uso (GUI)
```bash
python app.py
# o
python YOUTUBE_AUDIO2TEXT_V2.py --gui
```

## Uso (CLI)
- Transcribir desde YouTube:
```bash
python YOUTUBE_AUDIO2TEXT_V2.py --url "https://www.youtube.com/watch?v=XXXX" --lang es-ES
```

- Transcribir archivo local:
```bash
python YOUTUBE_AUDIO2TEXT_V2.py --file ruta/al/archivo.mp3 --lang es-ES
```

Los resultados se guardan en la carpeta `outputs/` como archivos `.txt`.

## Estructura del Proyecto
```
YOUTUBE_AUDIO2TEXT_V2/
├─ app.py                 # Entrada para la GUI
├─ YOUTUBE_AUDIO2TEXT_V2.py   # CLI y lanzador de GUI
├─ yt_audio2text/
│  ├─ __init__.py
│  ├─ downloader.py       # Descarga y extracción de audio (yt-dlp)
│  ├─ audio_utils.py      # Conversión a WAV y segmentación
│  └─ transcriber.py      # Lógica de transcripción
│  └─ gui.py              # Interfaz Tkinter
├─ requirements.txt
├─ README.md
└─ .gitignore
```

## Notas
- Asegúrate de tener `ffmpeg` instalado.
- yt-dlp se utiliza para descargar el audio de YouTube.
- La carpeta `downloads/` contiene los audios descargados; `outputs/` las transcripciones.

## Licencia
MIT

