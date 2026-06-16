#!/usr/bin/env python3
"""
Transcritor de Vídeo para Texto
Usando OpenAI Whisper para transcrição em Português
"""

import os
import sys
import threading
import subprocess
import json
import tempfile
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────
# Verifica dependências antes de tudo
# ─────────────────────────────────────────────
def check_and_install_deps():
    deps = {
        "whisper": "openai-whisper",
        "tkinter": None,  # built-in
    }
    missing = []
    try:
        import whisper  # noqa
    except ImportError:
        missing.append("openai-whisper")

    if missing:
        print(f"Instalando dependências: {', '.join(missing)}")
        for pkg in missing:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--break-system-packages", "-q"])
        print("Dependências instaladas! Reiniciando...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

check_and_install_deps()

# ─────────────────────────────────────────────
# Imports após deps garantidas
# ─────────────────────────────────────────────
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import whisper


# ─────────────────────────────────────────────
# Paleta de cores / tema
# ─────────────────────────────────────────────
COLORS = {
    "bg":        "#0D0F14",
    "surface":   "#161920",
    "card":      "#1C2030",
    "border":    "#2A3050",
    "accent":    "#5B7FFF",
    "accent2":   "#7C5BFF",
    "success":   "#3DD68C",
    "warning":   "#FFB547",
    "text":      "#E8EAF6",
    "muted":     "#6B7399",
    "highlight": "#252A40",
}

MODELOS = {
    "Tiny  – rápido, menos preciso":    "tiny",
    "Base  – equilibrado (recomendado)": "base",
    "Small – mais preciso, mais lento":  "small",
    "Medium – alta precisão":            "medium",
    "Large – máxima precisão":           "large",
}

FORMATOS_VIDEO = [
    ("Vídeos", "*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.m4v *.mpeg *.mpg"),
    ("Áudios", "*.mp3 *.wav *.ogg *.flac *.aac *.m4a"),
    ("Todos os arquivos", "*.*"),
]


# ─────────────────────────────────────────────
# App principal
# ─────────────────────────────────────────────
class TranscriptorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.video_path = tk.StringVar()
        self.modelo_key = tk.StringVar(value=list(MODELOS.keys())[1])
        self.status_var = tk.StringVar(value="Pronto para transcrever")
        self.progress_var = tk.DoubleVar(value=0)
        self.is_running = False
        self._whisper_model = None

        self._setup_window()
        self._build_ui()

    # ── janela ─────────────────────────────────
    def _setup_window(self):
        self.root.title("Transcritor de Vídeo 🎬")
        self.root.geometry("820x680")
        self.root.minsize(700, 560)
        self.root.configure(bg=COLORS["bg"])
        # Centraliza
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth()  - 820) // 2
        y = (self.root.winfo_screenheight() - 680) // 2
        self.root.geometry(f"+{x}+{y}")

    # ── UI ─────────────────────────────────────
    def _build_ui(self):
        # ---- Header ----
        header = tk.Frame(self.root, bg=COLORS["bg"])
        header.pack(fill="x", padx=32, pady=(28, 0))

        tk.Label(
            header, text="🎬 Transcritor de Vídeo",
            font=("Helvetica", 22, "bold"),
            bg=COLORS["bg"], fg=COLORS["text"]
        ).pack(side="left")

        tk.Label(
            header, text="powered by Whisper AI",
            font=("Helvetica", 10),
            bg=COLORS["bg"], fg=COLORS["muted"]
        ).pack(side="left", padx=(12, 0), pady=(8, 0))

        # Separador
        sep = tk.Frame(self.root, bg=COLORS["border"], height=1)
        sep.pack(fill="x", padx=32, pady=16)

        # ---- Área principal ----
        main = tk.Frame(self.root, bg=COLORS["bg"])
        main.pack(fill="both", expand=True, padx=32)

        # Card: Selecionar Vídeo
        self._card_video(main)

        # Card: Configurações
        self._card_config(main)

        # Botão Transcrever
        self._btn_transcrever(main)

        # Barra de progresso + status
        self._progress_area(main)

        # Card: Resultado
        self._card_resultado(main)

        # Rodapé
        self._footer()

    def _card(self, parent, title: str) -> tk.Frame:
        wrapper = tk.Frame(parent, bg=COLORS["card"],
                           highlightthickness=1,
                           highlightbackground=COLORS["border"])
        wrapper.pack(fill="x", pady=(0, 12))

        tk.Label(wrapper, text=title,
                 font=("Helvetica", 11, "bold"),
                 bg=COLORS["card"], fg=COLORS["accent"]
                 ).pack(anchor="w", padx=16, pady=(12, 6))

        inner = tk.Frame(wrapper, bg=COLORS["card"])
        inner.pack(fill="x", padx=16, pady=(0, 12))
        return inner

    def _card_video(self, parent):
        inner = self._card(parent, "📂  Arquivo de Vídeo / Áudio")

        entry_frame = tk.Frame(inner, bg=COLORS["highlight"],
                               highlightthickness=1,
                               highlightbackground=COLORS["border"])
        entry_frame.pack(fill="x", side="left", expand=True)

        self.entry_path = tk.Entry(
            entry_frame,
            textvariable=self.video_path,
            font=("Helvetica", 10),
            bg=COLORS["highlight"], fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat", bd=8,
        )
        self.entry_path.pack(fill="x")

        btn = tk.Button(
            inner, text="  Selecionar  ",
            font=("Helvetica", 10, "bold"),
            bg=COLORS["accent"], fg="white",
            activebackground=COLORS["accent2"],
            relief="flat", cursor="hand2",
            command=self._selecionar_arquivo,
            padx=10, pady=6,
        )
        btn.pack(side="left", padx=(10, 0))

    def _card_config(self, parent):
        inner = self._card(parent, "⚙️  Configurações")

        # Modelo
        tk.Label(inner, text="Modelo Whisper:",
                 font=("Helvetica", 10),
                 bg=COLORS["card"], fg=COLORS["muted"]
                 ).grid(row=0, column=0, sticky="w", padx=(0, 12), pady=4)

        combo_style = ttk.Style()
        combo_style.theme_use("clam")
        combo_style.configure("Dark.TCombobox",
                               fieldbackground=COLORS["highlight"],
                               background=COLORS["highlight"],
                               foreground=COLORS["text"],
                               selectbackground=COLORS["accent"],
                               bordercolor=COLORS["border"],
                               arrowcolor=COLORS["accent"])

        self.combo = ttk.Combobox(
            inner,
            textvariable=self.modelo_key,
            values=list(MODELOS.keys()),
            state="readonly",
            style="Dark.TCombobox",
            width=38,
        )
        self.combo.grid(row=0, column=1, sticky="w")

        # Dica
        tk.Label(
            inner,
            text="💡  'Base' é ideal para a maioria dos casos. 'Large' é mais lento mas muito mais preciso.",
            font=("Helvetica", 9),
            bg=COLORS["card"], fg=COLORS["muted"], wraplength=600, justify="left"
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

    def _btn_transcrever(self, parent):
        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill="x", pady=(4, 8))

        self.btn_transcrever = tk.Button(
            frame,
            text="▶  Iniciar Transcrição",
            font=("Helvetica", 13, "bold"),
            bg=COLORS["accent"], fg="white",
            activebackground=COLORS["accent2"],
            relief="flat", cursor="hand2",
            padx=24, pady=10,
            command=self._iniciar_transcricao,
        )
        self.btn_transcrever.pack(side="left")

        self.btn_salvar = tk.Button(
            frame,
            text="💾  Salvar Texto",
            font=("Helvetica", 11),
            bg=COLORS["surface"], fg=COLORS["text"],
            activebackground=COLORS["highlight"],
            relief="flat", cursor="hand2",
            padx=16, pady=10,
            command=self._salvar_texto,
            state="disabled",
        )
        self.btn_salvar.pack(side="left", padx=(10, 0))

        self.btn_limpar = tk.Button(
            frame,
            text="🗑  Limpar",
            font=("Helvetica", 11),
            bg=COLORS["surface"], fg=COLORS["muted"],
            activebackground=COLORS["highlight"],
            relief="flat", cursor="hand2",
            padx=16, pady=10,
            command=self._limpar,
        )
        self.btn_limpar.pack(side="left", padx=(10, 0))

    def _progress_area(self, parent):
        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill="x", pady=(0, 8))

        self.lbl_status = tk.Label(
            frame, textvariable=self.status_var,
            font=("Helvetica", 10),
            bg=COLORS["bg"], fg=COLORS["muted"],
        )
        self.lbl_status.pack(anchor="w")

        bar_style = ttk.Style()
        bar_style.configure("Accent.Horizontal.TProgressbar",
                             troughcolor=COLORS["surface"],
                             background=COLORS["accent"],
                             bordercolor=COLORS["bg"],
                             lightcolor=COLORS["accent"],
                             darkcolor=COLORS["accent"])

        self.progress = ttk.Progressbar(
            frame, variable=self.progress_var,
            style="Accent.Horizontal.TProgressbar",
            mode="indeterminate", length=400,
        )
        self.progress.pack(fill="x", pady=(4, 0))

    def _card_resultado(self, parent):
        wrapper = tk.Frame(parent, bg=COLORS["card"],
                           highlightthickness=1,
                           highlightbackground=COLORS["border"])
        wrapper.pack(fill="both", expand=True, pady=(0, 4))

        header = tk.Frame(wrapper, bg=COLORS["card"])
        header.pack(fill="x", padx=16, pady=(12, 6))

        tk.Label(header, text="📝  Transcrição",
                 font=("Helvetica", 11, "bold"),
                 bg=COLORS["card"], fg=COLORS["accent"]
                 ).pack(side="left")

        self.lbl_palavras = tk.Label(
            header, text="",
            font=("Helvetica", 9),
            bg=COLORS["card"], fg=COLORS["muted"]
        )
        self.lbl_palavras.pack(side="right")

        text_frame = tk.Frame(wrapper, bg=COLORS["card"])
        text_frame.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        self.text_resultado = tk.Text(
            text_frame,
            font=("Helvetica", 11),
            bg=COLORS["highlight"], fg=COLORS["text"],
            insertbackground=COLORS["text"],
            selectbackground=COLORS["accent"],
            relief="flat", bd=0,
            wrap="word",
            padx=12, pady=10,
        )
        self.text_resultado.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame, command=self.text_resultado.yview,
                                  bg=COLORS["surface"], troughcolor=COLORS["surface"],
                                  activebackground=COLORS["accent"])
        scrollbar.pack(side="right", fill="y")
        self.text_resultado.config(yscrollcommand=scrollbar.set)

        self.text_resultado.insert("1.0", "O texto transcrito aparecerá aqui...")
        self.text_resultado.config(state="disabled", fg=COLORS["muted"])

    def _footer(self):
        footer = tk.Frame(self.root, bg=COLORS["bg"])
        footer.pack(fill="x", padx=32, pady=(4, 16))
        tk.Label(
            footer,
            text="Transcrição em Português Brasileiro · OpenAI Whisper · Funciona 100% offline",
            font=("Helvetica", 8),
            bg=COLORS["bg"], fg=COLORS["muted"]
        ).pack(side="left")

    # ── Ações ───────────────────────────────────
    def _selecionar_arquivo(self):
        path = filedialog.askopenfilename(
            title="Selecionar vídeo ou áudio",
            filetypes=FORMATOS_VIDEO,
        )
        if path:
            self.video_path.set(path)
            nome = Path(path).name
            self.status_var.set(f"Arquivo selecionado: {nome}")

    def _iniciar_transcricao(self):
        path = self.video_path.get().strip()
        if not path:
            messagebox.showwarning("Atenção", "Selecione um arquivo de vídeo ou áudio primeiro.")
            return
        if not os.path.exists(path):
            messagebox.showerror("Erro", "Arquivo não encontrado.")
            return
        if self.is_running:
            return

        self.is_running = True
        self.btn_transcrever.config(state="disabled", text="⏳  Transcrevendo...")
        self.btn_salvar.config(state="disabled")
        self._set_resultado("", muted=False)
        self.progress.config(mode="indeterminate")
        self.progress.start(12)

        thread = threading.Thread(target=self._transcrever_thread, args=(path,), daemon=True)
        thread.start()

    def _transcrever_thread(self, path: str):
        try:
            modelo_nome = MODELOS[self.modelo_key.get()]
            self._update_status(f"⏳ Carregando modelo '{modelo_nome}'...")

            if self._whisper_model is None or getattr(self._whisper_model, "_nome", None) != modelo_nome:
                self._whisper_model = whisper.load_model(modelo_nome)
                self._whisper_model._nome = modelo_nome

            self._update_status("🔊 Transcrevendo... (pode levar alguns minutos)")

            result = self._whisper_model.transcribe(
                path,
                language="pt",
                task="transcribe",
                verbose=False,
            )

            texto = result["text"].strip()
            self.root.after(0, self._transcricao_concluida, texto)

        except Exception as e:
            self.root.after(0, self._transcricao_erro, str(e))

    def _transcricao_concluida(self, texto: str):
        self.progress.stop()
        self.progress_var.set(100)
        self.is_running = False

        palavras = len(texto.split())
        self._update_status(f"✅ Transcrição concluída! {palavras} palavras")
        self._set_resultado(texto, muted=False)
        self.lbl_palavras.config(text=f"{palavras} palavras")
        self.btn_transcrever.config(state="normal", text="▶  Iniciar Transcrição")
        self.btn_salvar.config(state="normal")

    def _transcricao_erro(self, erro: str):
        self.progress.stop()
        self.is_running = False
        self._update_status(f"❌ Erro: {erro}")
        self.btn_transcrever.config(state="normal", text="▶  Iniciar Transcrição")
        messagebox.showerror("Erro na Transcrição", f"Ocorreu um erro:\n\n{erro}")

    def _salvar_texto(self):
        texto = self.text_resultado.get("1.0", "end").strip()
        if not texto:
            return

        video = self.video_path.get()
        sugestao = Path(video).stem + "_transcricao.txt" if video else "transcricao.txt"

        path = filedialog.asksaveasfilename(
            title="Salvar transcrição",
            defaultextension=".txt",
            initialfile=sugestao,
            filetypes=[("Texto", "*.txt"), ("Markdown", "*.md"), ("Todos", "*.*")],
        )
        if not path:
            return

        with open(path, "w", encoding="utf-8") as f:
            f.write(f"Transcrição gerada em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"Arquivo: {self.video_path.get()}\n")
            f.write(f"Modelo: {MODELOS[self.modelo_key.get()]}\n")
            f.write("─" * 60 + "\n\n")
            f.write(texto)

        self._update_status(f"💾 Arquivo salvo em: {path}")
        messagebox.showinfo("Salvo!", f"Transcrição salva em:\n{path}")

    def _limpar(self):
        self.video_path.set("")
        self._set_resultado("", muted=True)
        self.lbl_palavras.config(text="")
        self.progress_var.set(0)
        self.status_var.set("Pronto para transcrever")
        self.btn_salvar.config(state="disabled")

    # ── Helpers ─────────────────────────────────
    def _update_status(self, msg: str):
        self.root.after(0, self.status_var.set, msg)

    def _set_resultado(self, texto: str, muted: bool = False):
        self.text_resultado.config(state="normal")
        self.text_resultado.delete("1.0", "end")
        if texto:
            self.text_resultado.insert("1.0", texto)
            self.text_resultado.config(fg=COLORS["text"] if not muted else COLORS["muted"])
        else:
            self.text_resultado.insert("1.0", "O texto transcrito aparecerá aqui...")
            self.text_resultado.config(fg=COLORS["muted"])
        self.text_resultado.config(state="disabled")


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
def main():
    # Verifica ffmpeg (compatível com Windows, Linux e Mac)
    cmd = "where" if sys.platform == "win32" else "which"
    if subprocess.run([cmd, "ffmpeg"], capture_output=True).returncode != 0:
        msg = (
            "ffmpeg não encontrado!\n\n"
            "Windows: Baixe em https://ffmpeg.org/download.html\n"
            "e adicione ao PATH do sistema.\n\n"
            "Ou instale pelo winget:\n"
            "  winget install ffmpeg"
        )
        messagebox.showerror("ffmpeg não encontrado", msg)
        sys.exit(1)

    root = tk.Tk()
    app = TranscriptorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
