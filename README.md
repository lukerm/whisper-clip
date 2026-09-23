# whisper-clip

Local dictation for Linux. Press a key to start recording, talk (pauses are
trimmed by VAD), press again to stop. The recording is transcribed on your GPU
and replaces the clipboard. One recording, one clipboard entry.

Pipeline: hotkey → `sounddevice` mic → Silero VAD (drop silence) →
`faster-whisper` on CUDA → `pyperclip`.

## Install (Ubuntu)

```bash
sudo apt install libportaudio2 xclip   # xclip works on Wayland via XWayland; wl-clipboard also fine
uv venv && source .venv/bin/activate
uv pip install .
```

`silero-vad` pulls in PyTorch (~2 GB with CUDA). `faster-whisper` needs the
cuBLAS/cuDNN runtime libraries; a CUDA build of torch already provides them.

## Run

Start the daemon (first run downloads the model, ~1.6 GB for large-v3-turbo):

```bash
whisper-clip
```

Bind the toggle to a key. GNOME: Settings → Keyboard → View and Customize
Shortcuts → Custom Shortcuts → `+`, command:

```
/<full/path/to>/.venv/bin/whisper-clip toggle
```

Something innocuous like F14 is a good choice.

Press it once to start recording, again to stop and deliver. Ctrl+C in the
daemon's terminal to quit. Settings live in `whisper_clip/config.py`.

Why a separate toggle command: native Wayland doesn't let an application
listen for global hotkeys, so the daemon listens for a signal (SIGUSR1)
instead and the desktop's own shortcut system sends it. Works on X11 too.

## Layout

```
whisper_clip/
  config.py      all tunables, one place
  audio.py       microphone -> stream of fixed-size chunks
  vad.py         Segmenter: chunks -> speech segments, silence removed
  transcribe.py  audio -> text (faster-whisper)
  clipboard.py   text -> clipboard
  __main__.py    daemon loop, hotkey signal, toggle command
```
