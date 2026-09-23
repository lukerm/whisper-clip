"""Keep only the speech in a stream of audio chunks, using Silero VAD."""

from collections import deque

import numpy as np
import torch
from silero_vad import VADIterator, load_silero_vad

from . import config


def _ms_to_samples(ms: int) -> int:
    return ms * config.SAMPLE_RATE // 1000


class Segmenter:
    """Feed chunks in; get back speech segments (silence between them removed).

    A segment is returned from feed() when Silero sees END_SILENCE_MS of quiet,
    or from flush() if speech is still in progress when the recording stops.
    """

    def __init__(self):
        self._model = load_silero_vad()
        self._vad = VADIterator(
            self._model,
            sampling_rate=config.SAMPLE_RATE,
            min_silence_duration_ms=config.END_SILENCE_MS,
        )
        pre_roll_chunks = max(1, _ms_to_samples(config.PRE_ROLL_MS) // config.CHUNK_SAMPLES)
        self._pre_roll: deque[np.ndarray] = deque(maxlen=pre_roll_chunks)
        self._min_samples = _ms_to_samples(config.MIN_SEGMENT_MS)
        self._current: list[np.ndarray] | None = None  # None while not in speech

    def reset(self) -> None:
        self._vad.reset_states()
        self._pre_roll.clear()
        self._current = None

    def feed(self, chunk: np.ndarray) -> np.ndarray | None:
        event = self._vad(torch.from_numpy(chunk))

        if self._current is None:
            self._pre_roll.append(chunk)
            if event and "start" in event:
                self._current = list(self._pre_roll)
            return None

        self._current.append(chunk)
        if event and "end" in event:
            return self._close()
        return None

    def flush(self) -> np.ndarray | None:
        return self._close() if self._current is not None else None

    def _close(self) -> np.ndarray | None:
        audio = np.concatenate(self._current)
        self._current = None
        self._pre_roll.clear()
        return audio if len(audio) >= self._min_samples else None
