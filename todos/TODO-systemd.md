# TODO: systemd user service + audio blip

Goal: daemon starts at login, model already warm; audible feedback since the
terminal output is no longer visible.

## Audio blip (done)

- `feedback.py` has `blip(kind)`: rising tone on `● Recording`, falling tone
  once the text has been copied to the clipboard (not on stop, so you hear
  when it's ready to paste). 120 ms, numpy-generated, via `sounddevice.play()`.

## Service

1. Create `~/.config/systemd/user/whisper-clip.service`:

   ```ini
   [Unit]
   Description=whisper-clip dictation daemon
   After=graphical-session.target pipewire.service
   PartOf=graphical-session.target

   [Service]
   ExecStart=/full/path/to/.venv/bin/whisper-clip
   Restart=on-failure
   RestartSec=3

   [Install]
   WantedBy=graphical-session.target
   ```

2. `systemctl --user daemon-reload && systemctl --user enable --now whisper-clip`
3. Logs: `journalctl --user -u whisper-clip -f`
4. The hotkey toggle keeps working unchanged (PID file). Alternative that
   drops the PID file: bind the key to
   `systemctl --user kill -s USR1 whisper-clip`.

## Gotchas

- Clipboard needs `WAYLAND_DISPLAY` in the service environment. GNOME on
  Ubuntu exports it to user services; if `pyperclip` fails in the journal,
  run `systemctl --user import-environment WAYLAND_DISPLAY DISPLAY`.
- Mic must exist before the daemon opens it: the `After=pipewire.service`
  line handles this. If the mic is USB and slow to enumerate, `Restart=`
  covers it.
- After suspend, CUDA can wedge (`nvidia_uvm`). Symptom: transcription
  hangs. Fix: `systemctl --user restart whisper-clip`; if recurring,
  `sudo modprobe -r nvidia_uvm && sudo modprobe nvidia_uvm`.
- ~1.5 GB VRAM resident from login. Acceptable trade for instant dictation.
