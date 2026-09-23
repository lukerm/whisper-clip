"""Wire the stages: hotkey -> mic -> VAD -> whisper -> clipboard.

    whisper-clip          run the daemon
    whisper-clip toggle   start or stop a recording (bind this to a key)

Native Wayland forbids an app from grabbing global hotkeys, so the toggle is a
separate command that signals the daemon (SIGUSR1). Bind it to a key in your
desktop's keyboard-shortcut settings; that works on every compositor and X11.

While recording, VAD keeps only the speech and drops the pauses. Stopping the
recording sends everything collected to Whisper and the text replaces the
clipboard, so one recording == one clipboard entry.
"""

import os
import queue
import signal
import sys
import threading
from pathlib import Path

import numpy as np

from . import audio, clipboard
from .transcribe import Transcriber
from .vad import Segmenter

PID_FILE = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "whisper-clip.pid"


def _worker(jobs: queue.Queue[np.ndarray], transcriber: Transcriber) -> None:
    while True:
        text = transcriber(jobs.get())
        if text:
            clipboard.copy(text)
            print(f"> {text}")


def run() -> None:
    toggle = threading.Event()
    signal.signal(signal.SIGUSR1, lambda *_: toggle.set())
    PID_FILE.write_text(str(os.getpid()))

    print("Loading model...")
    transcriber = Transcriber()
    segmenter = Segmenter()
    jobs: queue.Queue[np.ndarray] = queue.Queue()
    threading.Thread(target=_worker, args=(jobs, transcriber), daemon=True).start()

    recording = False
    segments: list[np.ndarray] = []
    print("Ready. Press your hotkey to start/stop recording. Ctrl+C to quit.")
    try:
        for chunk in audio.chunks():
            if toggle.is_set():
                toggle.clear()
                recording = not recording
                if recording:
                    segmenter.reset()
                    segments = []
                    print("● Recording")
                else:
                    if (tail := segmenter.flush()) is not None:
                        segments.append(tail)
                    print(f"■ Stopped, {len(segments)} speech segment(s)")
                    if segments:
                        jobs.put(np.concatenate(segments))
            if recording and (segment := segmenter.feed(chunk)) is not None:
                segments.append(segment)
    except KeyboardInterrupt:
        print("\nBye.")
    finally:
        PID_FILE.unlink(missing_ok=True)


def toggle() -> None:
    try:
        os.kill(int(PID_FILE.read_text()), signal.SIGUSR1)
    except (FileNotFoundError, ProcessLookupError, ValueError):
        sys.exit("whisper-clip is not running")


def main() -> None:
    if sys.argv[1:] == ["toggle"]:
        toggle()
    elif sys.argv[1:]:
        sys.exit(__doc__)
    else:
        run()


if __name__ == "__main__":
    main()
