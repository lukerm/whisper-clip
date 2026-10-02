#  Copyright (C) 2026 lukerm of www.zl-labs.tech
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
"""Short audible blips, since a daemon has no visible terminal.

Tones are generated in numpy and played with sounddevice: no sound files.
Kept under 150 ms so the start blip never lands in the recording.
"""

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 48_000
DURATION_S = 0.12
VOLUME = 0.2

# (start Hz, end Hz): rising for "recording", falling for "text on clipboard".
_SWEEPS = {"start": (660, 990), "done": (990, 660)}


def _tone(f0: float, f1: float) -> np.ndarray:
    t = np.arange(int(SAMPLE_RATE * DURATION_S)) / SAMPLE_RATE
    freq = np.linspace(f0, f1, t.size)
    phase = 2 * np.pi * np.cumsum(freq) / SAMPLE_RATE
    # Hann envelope avoids clicks at the edges.
    return (VOLUME * np.sin(phase) * np.hanning(t.size)).astype(np.float32)


_TONES = {kind: _tone(*sweep) for kind, sweep in _SWEEPS.items()}


def blip(kind: str) -> None:
    """Play a blip without blocking. kind is "start" or "done"."""
    try:
        sd.play(_TONES[kind], SAMPLE_RATE)
    except sd.PortAudioError as e:
        print(f"[feedback] {e}")
