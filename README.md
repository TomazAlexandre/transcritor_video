# 🎬 Transcritor de Vídeo para Texto

Transcribes videos and audio files directly from your PC to text, using OpenAI's Whisper model — no internet required, no API key, no cost.

> 🇧🇷 Supports multiple languages — including Portuguese, English, Spanish, and more.

---

## How it works

Open the app, select the file, choose the model and language, and click transcribe. The text appears on screen and you can save it as a `.txt` whenever you want.

Under the hood, it uses [OpenAI Whisper](https://github.com/openai/whisper) to run transcription locally on your machine. The first run downloads the chosen model (~75 MB to ~1.5 GB depending on the size), after that it works 100% offline.

---

## Requirements

- Python 3.8 or higher
- ffmpeg installed on the system
- ~2 GB RAM (base model)

---

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/TomazAlexandre/transcritor_video.git
cd transcritor_video
```

**2. Install Whisper**
```bash
pip install openai-whisper
```

**3. Install ffmpeg**

Windows:
```bash
winget install ffmpeg
```

Linux:
```bash
sudo apt install ffmpeg
```

Mac:
```bash
brew install ffmpeg
```

> After installing ffmpeg on Windows, close and reopen the terminal to update the PATH.

---

## Usage

```bash
python transcritor_video.py
```

The interface opens, you select the video/audio file, choose the model and language. That's it.

---

## Available Models

| Model  | Speed     | Accuracy | RAM (approx.) |
|--------|-----------|----------|---------------|
| tiny   | ⚡⚡⚡⚡ | ★☆☆☆    | ~1 GB         |
| base   | ⚡⚡⚡   | ★★☆☆    | ~1 GB         |
| small  | ⚡⚡     | ★★★☆    | ~2 GB         |
| medium | ⚡       | ★★★★    | ~5 GB         |
| large  | 🐢        | ★★★★★   | ~10 GB        |

For most use cases, **base** works great. If you need more accuracy with accents or difficult audio, try **small** or **medium**.

---

## Supported Languages

| Language   | Code |
|------------|------|
| Portuguese | pt   |
| English    | en   |
| Spanish    | es   |
| French     | fr   |
| German     | de   |
| Italian    | it   |
| Japanese   | ja   |
| Chinese    | zh   |
| Russian    | ru   |
| Arabic     | ar   |
| Auto-detect | —   |

> **Auto-detect** lets Whisper identify the language automatically — useful when you're unsure.

---

## Supported Formats

Video: `mp4`, `mkv`, `avi`, `mov`, `wmv`, `flv`, `webm`, `m4v`, `mpeg`

Audio: `mp3`, `wav`, `ogg`, `flac`, `aac`, `m4a`

---

## Features

- Native GUI (no external frameworks needed)
- Multi-language transcription with auto-detect option
- Saves result as `.txt` with metadata (date, file name, model used)
- Works offline after the first model download
- Compatible with Windows, Linux and Mac

---

## Common Issues

**`ffmpeg not found` on Windows**
Run `winget install ffmpeg` and restart the terminal before running the script.

**Transcription is very slow**
Use a smaller model (`tiny` or `base`), or run on a machine with a GPU — Whisper uses CUDA automatically if available.

**Errors on technical words or proper names**
This is a known limitation for specific vocabulary. Larger models (`medium`, `large`) tend to handle it better.

---

## License

MIT
