# TODO: wake word ("vocoder start" / "vocoder stop")

Goal: zero-keypress dictation. Coexists with the hotkey; either can start or
stop a recording.

## Design

- Add `wakeword.py`: thin wrapper around `openwakeword` exposing
  `Detector.feed(chunk) -> "start" | "stop" | None`.
- In `__main__.run()`, feed every chunk to the detector alongside the
  existing `toggle` event. A "start" while idle or a "stop" while recording
  flips `recording`, through the same code path the signal uses.
- On a spoken "stop", the phrase itself is inside the recording. Strip it
  from the transcript with a regex on the trailing words (more robust than
  trimming audio).
- Keep the signal/hotkey path unchanged.

## Steps

1. `pip install openwakeword` (adds onnxruntime, ~50 MB). Add to pyproject.
2. Train two custom models with the openWakeWord Colab notebook
   (synthetic speech, ~1 h): `vocoder_start.onnx`, `vocoder_stop.onnx`.
   Store under `whisper_clip/models/`.
3. Write `wakeword.py`. openWakeWord expects 16 kHz int16 frames of 1280
   samples (80 ms); buffer 512-sample float32 chunks into 1280 and convert.
4. Wire into the loop; add `WAKE_THRESHOLD` and `WAKE_STOP_PATTERN` to
   `config.py`.
5. Tune the threshold against your mic: log scores for a day, pick a value
   with no false triggers during normal typing/talking.

## Gotchas

- "start"/"stop" share the "vocoder" prefix; if confusion is common, pick a
  second word with different phonemes (e.g. "vocoder done").
- ~0.5 s lag after the phrase before the detector fires; expected.
- Detector runs continuously, so the daemon is always processing audio.
  Mute means stopping the daemon (or add a mute toggle later).
- Audio blip (see TODO-systemd.md) becomes essential: you need to know
  whether "vocoder start" was heard.
