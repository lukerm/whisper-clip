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
