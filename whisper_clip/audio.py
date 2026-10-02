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
"""Microphone capture. Yields float32 mono chunks of CHUNK_SAMPLES."""

import queue

import numpy as np
import sounddevice as sd

from . import config


def chunks():
    """Generator of numpy float32 arrays, shape (CHUNK_SAMPLES,). Blocks between chunks."""
    q: queue.Queue[np.ndarray] = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(f"[audio] {status}")
        q.put(indata[:, 0].copy())

    with sd.InputStream(
        samplerate=config.SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=config.CHUNK_SAMPLES,
        callback=callback,
    ):
        while True:
            yield q.get()
