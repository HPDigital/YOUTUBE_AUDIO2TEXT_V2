from __future__ import annotations

import threading
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk

from .downloader import download_youtube_audio
from .audio_utils import ensure_wav, split_wav_on_silence
from .transcriber import Transcriber


DEFAULT_OUTPUTS_DIR = Path("outputs")
DEFAULT_DOWNLOADS_DIR = Path("downloads")


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("YouTube Audio -> Texto")
        self.root.geometry("840x640")

        self.language = tk.StringVar(value="es-ES")
        self.youtube_url = tk.StringVar()
        self.local_file = tk.StringVar()

        self._build_ui()

        self.transcriber = Transcriber(language=self.language.get())
        DEFAULT_OUTPUTS_DIR.mkdir(exist_ok=True)
        DEFAULT_DOWNLOADS_DIR.mkdir(exist_ok=True)

    def _build_ui(self) -> None:
        nb = ttk.Notebook(self.root)
        frame_url = ttk.Frame(nb)
        frame_local = ttk.Frame(nb)
        nb.add(frame_url, text="YouTube URL")
        nb.add(frame_local, text="Archivo Local")
        nb.pack(fill="both", expand=True)

        # URL Tab
        ttk.Label(frame_url, text="URL de YouTube:").pack(anchor="w", padx=10, pady=(10, 2))
        url_entry = ttk.Entry(frame_url, textvariable=self.youtube_url)
        url_entry.pack(fill="x", padx=10)

        self.btn_dl_transcribe = ttk.Button(
            frame_url, text="Descargar y Transcribir", command=self.on_download_and_transcribe
        )
        self.btn_dl_transcribe.pack(padx=10, pady=8)

        # Local tab
        file_row = ttk.Frame(frame_local)
        file_row.pack(fill="x", padx=10, pady=(10, 2))
        ttk.Entry(file_row, textvariable=self.local_file).pack(side="left", fill="x", expand=True)
        ttk.Button(file_row, text="Seleccionar...", command=self.on_pick_file).pack(side="left", padx=6)

        self.btn_transcribe_local = ttk.Button(frame_local, text="Transcribir Archivo", command=self.on_transcribe_local)
        self.btn_transcribe_local.pack(padx=10, pady=8)

        # Common controls
        opts_row = ttk.Frame(self.root)
        opts_row.pack(fill="x", padx=10, pady=(6, 2))
        ttk.Label(opts_row, text="Idioma:").pack(side="left")
        lang_combo = ttk.Combobox(
            opts_row,
            textvariable=self.language,
            values=["es-ES", "en-US", "pt-BR", "fr-FR"],
            width=10,
            state="readonly",
        )
        lang_combo.pack(side="left", padx=(4, 12))
        lang_combo.bind("<<ComboboxSelected>>", lambda e: self._update_language())

        self.progress = ttk.Progressbar(opts_row, mode="determinate")
        self.progress.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.btn_save = ttk.Button(opts_row, text="Guardar Texto", command=self.on_save, state=tk.DISABLED)
        self.btn_save.pack(side="left")

        # Output
        self.txt = tk.Text(self.root, wrap="word")
        self.txt.pack(fill="both", expand=True, padx=10, pady=10)

    def _update_language(self) -> None:
        self.transcriber.language = self.language.get()

    def log(self, msg: str) -> None:
        self.txt.configure(state=tk.NORMAL)
        self.txt.insert(tk.END, msg + "\n")
        self.txt.see(tk.END)
        self.txt.configure(state=tk.DISABLED)

    def set_running(self, running: bool) -> None:
        state = tk.DISABLED if running else tk.NORMAL
        self.btn_dl_transcribe.configure(state=state)
        self.btn_transcribe_local.configure(state=state)

    def set_progress(self, message: str, frac: float) -> None:
        self.progress.configure(value=max(0, min(100, int(frac * 100))))
        if message:
            self.log(message)

    # Actions
    def on_download_and_transcribe(self) -> None:
        url = self.youtube_url.get().strip()
        if not url:
            self.log("Ingresa una URL válida de YouTube.")
            return
        threading.Thread(target=self._task_download_and_transcribe, args=(url,), daemon=True).start()

    def on_pick_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Selecciona un archivo de audio o video",
            filetypes=[
                ("Audio/Video", "*.wav;*.mp3;*.m4a;*.mp4;*.mov;*.mkv"),
                ("Todos", "*.*"),
            ],
        )
        if path:
            self.local_file.set(path)

    def on_transcribe_local(self) -> None:
        path = self.local_file.get().strip()
        if not path or not Path(path).exists():
            self.log("Selecciona un archivo válido.")
            return
        threading.Thread(target=self._task_transcribe_local, args=(Path(path),), daemon=True).start()

    def on_save(self) -> None:
        content = self.txt.get("1.0", tk.END).strip()
        if not content:
            return
        target = filedialog.asksaveasfilename(
            title="Guardar transcripción",
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt")],
        )
        if target:
            Path(target).write_text(content, encoding="utf-8")
            self.log(f"Guardado: {target}")

    # Worker tasks
    def _task_download_and_transcribe(self, url: str) -> None:
        self.set_running(True)
        self.txt.configure(state=tk.NORMAL)
        self.txt.delete("1.0", tk.END)
        self.txt.configure(state=tk.DISABLED)
        self.progress.configure(value=0)
        try:
            self.set_progress("Descargando audio de YouTube...", 0.01)
            audio_path = download_youtube_audio(url, DEFAULT_DOWNLOADS_DIR, fmt="wav", sample_rate=16000)
            self.set_progress(f"Descarga completa: {audio_path.name}", 0.15)

            self._transcribe_common(Path(audio_path))
        except Exception as e:
            self.log("ERROR: " + str(e))
            self.log(traceback.format_exc())
        finally:
            self.set_running(False)

    def _task_transcribe_local(self, path: Path) -> None:
        self.set_running(True)
        self.txt.configure(state=tk.NORMAL)
        self.txt.delete("1.0", tk.END)
        self.txt.configure(state=tk.DISABLED)
        self.progress.configure(value=0)
        try:
            self.set_progress("Normalizando/Convirtiendo a WAV...", 0.05)
            wav = ensure_wav(path, out_dir=DEFAULT_OUTPUTS_DIR, sample_rate=16000)
            self.set_progress(f"Listo WAV: {wav.name}", 0.15)

            self._transcribe_common(wav)
        except Exception as e:
            self.log("ERROR: " + str(e))
            self.log(traceback.format_exc())
        finally:
            self.set_running(False)

    def _transcribe_common(self, wav_path: Path) -> None:
        self.set_progress("Dividiendo en fragmentos por silencios...", 0.2)
        chunks = split_wav_on_silence(wav_path, max_chunk_ms=60_000)
        total = len(chunks)
        if total <= 1:
            self.set_progress("Transcribiendo audio...", 0.25)
            text = self.transcriber.transcribe_wav(wav_path, progress_cb=self.set_progress)
        else:
            self.set_progress(f"{total} fragmentos generados. Transcribiendo...", 0.25)
            text = self.transcriber.transcribe_chunks(chunks, progress_cb=self.set_progress)

        out_file = DEFAULT_OUTPUTS_DIR / f"transcripcion_{wav_path.stem}.txt"
        out_file.write_text(text, encoding="utf-8")
        self.log("\n=== TRANSCRIPCIÓN ===\n")
        self.log(text)
        self.log(f"\nGuardado en: {out_file}")
        self.btn_save.configure(state=tk.NORMAL)


def run() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()

