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

Press it once to start recording, again to stop and deliver. A rising beep
means recording has started; a falling beep means the text is on the clipboard,
ready to paste. Ctrl+C in the daemon's terminal to quit. Settings live in
`whisper_clip/config.py`.

Why a separate toggle command: native Wayland doesn't let an application
listen for global hotkeys, so the daemon listens for a signal (SIGUSR1)
instead and the desktop's own shortcut system sends it. Works on X11 too.

## Run at login (systemd)

Running as a systemd user service starts the daemon at login, so the model is
already warm when you first press the hotkey.

1. Create `~/.config/systemd/user/whisper-clip.service`:
  ```ini
   [Unit]
   Description=whisper-clip dictation daemon
   After=graphical-session.target pipewire.service
   PartOf=graphical-session.target

   [Service]
   Environment=PYTHONUNBUFFERED=1
   ExecStart=/<full/path/to>/.venv/bin/whisper-clip
   Restart=on-failure
   RestartSec=3

   [Install]
   WantedBy=graphical-session.target
  ```
2. Enable and start it:
  ```bash
   systemctl --user daemon-reload && systemctl --user enable --now whisper-clip
  ```
3. Follow the logs: `journalctl --user -u whisper-clip -f`

The hotkey toggle keeps working unchanged (it finds the daemon via its PID
file). Alternatively, bind the key to
`systemctl --user kill -s USR1 whisper-clip`, which doesn't need the PID file.

### Gotchas

- The placeholder <full/path/to> needs replacing in the ExecStart field in the 
  service file, otherwise it'll fail to run.
- The clipboard needs `WAYLAND_DISPLAY` in the service environment. GNOME on
Ubuntu exports it to user services; if `pyperclip` fails in the journal,
run `systemctl --user import-environment WAYLAND_DISPLAY DISPLAY`.
- About 1.5 GB of VRAM stays in use from login, always. That's the trade off 
 for having instant dictation. Stop the service to reclaim the VRAM if needed.
- The mic must exist before the daemon opens it. The `After=pipewire.service`
line handles this; if the mic is USB and slow to enumerate, `Restart=`
covers it.
- After suspend, CUDA can wedge (`nvidia_uvm`). Symptom: transcription hangs.
Fix: `systemctl --user restart whisper-clip`; if it keeps happening,
`sudo modprobe -r nvidia_uvm && sudo modprobe nvidia_uvm`.


## Layout

```
whisper_clip/
  config.py      all tunables, one place
  audio.py       microphone -> stream of fixed-size chunks
  vad.py         Segmenter: chunks -> speech segments, silence removed
  transcribe.py  audio -> text (faster-whisper)
  clipboard.py   text -> clipboard
  feedback.py    start / done beeps
  __main__.py    daemon loop, hotkey signal, toggle command
```

