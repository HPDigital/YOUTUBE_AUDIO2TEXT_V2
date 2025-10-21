"""
YOUTUBE_AUDIO2TEXT_V2
"""

#!/usr/bin/env python
# coding: utf-8

# In[3]:


import youtube_dl
import speech_recognition as sr
from pydub import AudioSegment

def yt_audio_to_text(url):
  """
  Extrae el audio de un video de YouTube y lo convierte a texto.

  Args:
    url: URL del video de YouTube.

  Returns:
    Texto del audio del video.
  """

  # Descarga el video
  with youtube_dl.YoutubeDL() as ydl:
    ydl.download([url])

  # Extrae el audio del video
  audio_file = f"{ydl.get_filename(url)}.mp3"
  sound = AudioSegment.from_mp3(audio_file)

  # Convierte el audio a formato WAV
  wav_file = audio_file.export("audio.wav", format="wav")

  # Usa SpeechRecognition para convertir el audio a texto
  r = sr.Recognizer()
  with sr.AudioFile(wav_file) as source:
    audio = r.record(source)

  # Elimina archivos temporales
  import os
  os.remove(audio_file)
  os.remove(wav_file)

  # Regresa el texto
  return r.recognize_google(audio)

# Ejemplo de uso
url = "https://www.youtube.com/watch?v=6pM0Rmj57Vk"
text = yt_audio_to_text(url)

print(text)


# In[5]:


import speech_recognition as sr
from moviepy.editor import AudioFileClip
import os

def convertir_archivo_local_a_texto(archivo_audio):
    """
    Convierte un archivo de audio local a texto
    Formatos soportados: .wav, .mp3, .mp4, .m4a, etc.
    """
    try:
        # Si no es WAV, convertir primero
        if not archivo_audio.lower().endswith('.wav'):
            print("Convirtiendo archivo a WAV...")
            audio_clip = AudioFileClip(archivo_audio)
            wav_filename = "temp_audio.wav"
            audio_clip.write_audiofile(wav_filename)
            audio_clip.close()
            archivo_a_procesar = wav_filename
        else:
            archivo_a_procesar = archivo_audio

        # Reconocimiento de voz
        r = sr.Recognizer()

        with sr.AudioFile(archivo_a_procesar) as source:
            print("Ajustando para ruido ambiente...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("Grabando audio...")
            audio_data = r.record(source)

            print("Convirtiendo a texto...")
            try:
                # Cambiar idioma según necesites: 'es-ES', 'en-US', etc.
                text = r.recognize_google(audio_data, language='es-ES')
                print(f"Texto extraído: {text}")
                return text
            except sr.UnknownValueError:
                print("No se pudo entender el audio")
                return None
            except sr.RequestError as e:
                print(f"Error del servicio de Google: {e}")
                return None

    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return None
    finally:
        # Limpiar archivo temporal si se creó
        if 'wav_filename' in locals() and os.path.exists(wav_filename):
            os.remove(wav_filename)

if __name__ == "__main__":
    print("=== CONVERTIDOR DE AUDIO LOCAL ===")
    print("Coloca tu archivo de audio en la misma carpeta que este script")
    print("Formatos soportados: .wav, .mp3, .mp4, .m4a, etc.")

    # Cambia esto por el nombre de tu archivo
    archivo = input("Nombre del archivo de audio: ")

    if os.path.exists(archivo):
        texto = convertir_archivo_local_a_texto(archivo)
        if texto:
            print(f"\n=== RESULTADO ===")
            print(texto)

            # Guardar resultado en archivo de texto
            with open("transcripcion.txt", "w", encoding="utf-8") as f:
                f.write(texto)
            print("\nTexto guardado en 'transcripcion.txt'")
        else:
            print("No se pudo extraer texto")
    else:
        print(f"El archivo '{archivo}' no existe")


# In[ ]:




