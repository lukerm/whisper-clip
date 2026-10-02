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
"""All tunables in one place. Edit and restart."""

# Audio. Whisper and Silero both want 16 kHz mono; 512 samples is the chunk
# size Silero's streaming API is trained on (32 ms).
SAMPLE_RATE = 16_000
CHUNK_SAMPLES = 512

# VAD. Only used to drop silence *within* a recording; the hotkey decides when
# a recording starts and ends. A speech segment closes after this much silence.
END_SILENCE_MS = 700
# Audio kept from just before speech was detected, so the first syllable isn't clipped.
PRE_ROLL_MS = 300
# Segments shorter than this are dropped (coughs, clicks).
MIN_SEGMENT_MS = 400

# Whisper.
MODEL = "large-v3-turbo"
DEVICE = "cuda"
COMPUTE_TYPE = "float16"
LANGUAGE = "en"
