"""Speech to text with faster-whisper."""

"""Speech to text with faster-whisper."""

import ctypes
import sysconfig
from pathlib import Path

import numpy as np

# CTranslate2 is linked against CUDA 12 and looks up libcublas.so.12 /
# libcudnn.so.9 by soname. The pip-installed copies live inside site-packages
# where the loader can't see them, so load them globally by path before
# faster_whisper is imported. Works the same under systemd as in a shell.
_site = Path(sysconfig.get_paths()["purelib"]) / "nvidia"
for _name in ("libcublas.so.12", "libcudnn.so.9"):
    _hits = list(_site.rglob(_name))
    if not _hits:
        raise ImportError(f"{_name} not found under {_site}; run: uv pip install nvidia-cublas-cu12 'nvidia-cudnn-cu12>=9'")
    ctypes.CDLL(str(_hits[0]), mode=ctypes.RTLD_GLOBAL)

from faster_whisper import WhisperModel  # noqa: E402

from . import config

class Transcriber:
    def __init__(self):
        self.model = WhisperModel(
            config.MODEL, device=config.DEVICE, compute_type=config.COMPUTE_TYPE
        )

    def __call__(self, audio: np.ndarray) -> str:
        segments, _ = self.model.transcribe(
            audio,
            language=config.LANGUAGE,
            beam_size=1,
            condition_on_previous_text=False,
        )
        return " ".join(s.text.strip() for s in segments).strip()
