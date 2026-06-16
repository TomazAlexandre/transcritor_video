# 🎬 Transcritor de Vídeo para Texto

Transcreve vídeos e áudios direto do seu PC para texto em Português, usando o modelo Whisper da OpenAI — sem precisar de internet, sem API key, sem custo.

---

## Como funciona

Você abre o app, seleciona o arquivo, escolhe o modelo e clica em transcrever. O texto aparece na tela e você pode salvar num `.txt` quando quiser.

Por baixo dos panos, o script usa o [Whisper](https://github.com/openai/whisper) para fazer a transcrição localmente na sua máquina. O primeiro uso baixa o modelo escolhido (~75 MB a ~1.5 GB dependendo do tamanho), depois disso funciona 100% offline.

---

## Requisitos

- Python 3.8 ou superior
- ffmpeg instalado no sistema
- ~2 GB de RAM (modelo base)

---

## Instalação

**1. Clone o repositório**
```bash
git clone https://github.com/tomazAlexandre/transcritor-video.git
cd transcritor-video
```

**2. Instale o Whisper**
```bash
pip install openai-whisper
```

**3. Instale o ffmpeg**

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

> Após instalar o ffmpeg no Windows, feche e abra o terminal novamente para o PATH atualizar.

---

## Uso

```bash
python transcritor_video.py
```

A interface abre, você seleciona o vídeo e escolhe o modelo na lista. Simples assim.

---

## Modelos disponíveis

| Modelo | Velocidade | Precisão | RAM aprox. |
|--------|-----------|----------|------------|
| tiny   | ⚡⚡⚡⚡   | ★☆☆☆    | ~1 GB      |
| base   | ⚡⚡⚡    | ★★☆☆    | ~1 GB      |
| small  | ⚡⚡      | ★★★☆    | ~2 GB      |
| medium | ⚡        | ★★★★    | ~5 GB      |
| large  | 🐢        | ★★★★★   | ~10 GB     |

Para a maioria dos casos, o **base** já resolve bem. Se precisar de mais precisão com sotaques ou áudio difícil, vale testar o **small** ou **medium**.

---

## Formatos suportados

Vídeo: `mp4`, `mkv`, `avi`, `mov`, `wmv`, `flv`, `webm`, `m4v`, `mpeg`

Áudio: `mp3`, `wav`, `ogg`, `flac`, `aac`, `m4a`

---

## Funcionalidades

- Interface gráfica nativa (sem dependência de frameworks externos)
- Transcrição em Português Brasileiro
- Salva o resultado em `.txt` com metadados (data, arquivo, modelo usado)
- Funciona offline após o primeiro download do modelo
- Compatível com Windows, Linux e Mac

---

## Problemas comuns

**`ffmpeg not found` no Windows**
Instale pelo `winget install ffmpeg` e reinicie o terminal antes de rodar o script.

**Transcrição muito lenta**
Use um modelo menor (`tiny` ou `base`) ou rode numa máquina com GPU — o Whisper usa CUDA automaticamente se disponível.

**Texto com erros em palavras técnicas ou nomes próprios**
É uma limitação do modelo para esse tipo de vocabulário. Modelos maiores (`medium`, `large`) tendem a errar menos.

---

## Licença

MIT
