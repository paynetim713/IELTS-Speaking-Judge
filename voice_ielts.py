r"""
Voice-driven IELTS Speaking mock-exam runner.

Flow:
    mic -> faster-whisper (CPU/int8) -> ollama ielts-examiner (streaming) -> edge-tts -> speaker

Hard-coded for ielts-examiner model. English voice for the examiner; Chinese feedback
is printed to console (not narrated) because the model emits ~500 chars of report.

Run:
    .\.venv\Scripts\python.exe voice_ielts.py
"""

import os
# Redirect faster-whisper / huggingface model cache off C: drive
os.environ.setdefault("HF_HOME", r"F:\ollama_models\voice_ielts\hf_cache")
os.environ.setdefault("HUGGINGFACE_HUB_CACHE", r"F:\ollama_models\voice_ielts\hf_cache")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

import asyncio
import json
import re
import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import sounddevice as sd
import requests
import pygame
import edge_tts
from faster_whisper import WhisperModel


# ---------------- Config ----------------
OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "ielts-examiner"

WHISPER_MODEL_SIZE = "small.en"   # tiny.en (fast/inaccurate) | base.en | small.en (recommended) | medium.en
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE = "int8"

SAMPLE_RATE = 16000
FRAME_MS = 30
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)

SILENCE_END_SEC = 2.5             # stop after this much silence following speech
PART2_SILENCE_END_SEC = 3.5       # longer tolerance during Part 2 long turn
MIN_SPEECH_SEC = 0.4
WAIT_FOR_START_SEC = 30
MAX_RECORD_SEC = 180

EN_VOICE = "en-GB-RyanNeural"     # British male — typical examiner profile
ZH_VOICE = "zh-CN-XiaoxiaoNeural"

# Kick the examiner to start speaking
KICKOFF_MESSAGE = "Hi, I'm ready to start the test."


# ---------------- Mic / VAD ----------------
def calibrate_threshold(seconds: float = 1.0) -> float:
    print("[ambient] keep quiet for 1 second...")
    audio = sd.rec(int(seconds * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype="int16")
    sd.wait()
    rms = float(np.sqrt(np.mean(audio.astype(np.float32) ** 2)))
    threshold = max(rms * 3.0, 400.0)
    print(f"[ambient] noise rms={rms:.0f}  speech threshold={threshold:.0f}")
    return threshold


def record_until_silence(threshold: float, silence_end_sec: float = SILENCE_END_SEC) -> np.ndarray:
    """Block on the mic until the user stops talking, return mono int16 buffer."""
    silence_frames_needed = int(silence_end_sec * 1000 / FRAME_MS)
    min_speech_frames = int(MIN_SPEECH_SEC * 1000 / FRAME_MS)
    wait_frames = int(WAIT_FOR_START_SEC * 1000 / FRAME_MS)
    max_frames = int(MAX_RECORD_SEC * 1000 / FRAME_MS)

    chunks = []
    speech_frames = 0
    silent_streak = 0
    has_spoken = False
    waited = 0

    print("[mic] listening...", flush=True)
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16",
                        blocksize=FRAME_SAMPLES) as stream:
        for i in range(max_frames):
            frame, _ = stream.read(FRAME_SAMPLES)
            chunks.append(frame.copy())
            rms = float(np.sqrt(np.mean(frame.astype(np.float32) ** 2)))
            is_speech = rms > threshold
            if is_speech:
                speech_frames += 1
                if speech_frames >= min_speech_frames:
                    has_spoken = True
                silent_streak = 0
            else:
                if has_spoken:
                    silent_streak += 1
                    if silent_streak >= silence_frames_needed:
                        break
                else:
                    waited += 1
                    if waited >= wait_frames:
                        print("[mic] no speech detected, giving up.")
                        return np.zeros(0, dtype=np.int16)
    return np.concatenate(chunks).flatten()


# ---------------- Whisper ----------------
def load_whisper() -> WhisperModel:
    print(f"[whisper] loading {WHISPER_MODEL_SIZE} on {WHISPER_DEVICE}/{WHISPER_COMPUTE} ...")
    t0 = time.time()
    model = WhisperModel(WHISPER_MODEL_SIZE, device=WHISPER_DEVICE, compute_type=WHISPER_COMPUTE)
    print(f"[whisper] loaded in {time.time()-t0:.1f}s")
    return model


def transcribe(model: WhisperModel, audio_int16: np.ndarray) -> str:
    if audio_int16.size == 0:
        return ""
    audio_float = audio_int16.astype(np.float32) / 32768.0
    segments, _ = model.transcribe(audio_float, language="en", beam_size=1, vad_filter=False)
    return " ".join(s.text.strip() for s in segments).strip()


# ---------------- Ollama ----------------
def stream_chat(history: list) -> str:
    """POST /api/chat with stream=true, print as it arrives, return full reply."""
    payload = {"model": MODEL_NAME, "messages": history, "stream": True,
               "options": {"num_ctx": 8192}}
    full = []
    with requests.post(f"{OLLAMA_URL}/api/chat", json=payload, stream=True, timeout=600) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            obj = json.loads(line)
            piece = obj.get("message", {}).get("content", "")
            if piece:
                print(piece, end="", flush=True)
                full.append(piece)
            if obj.get("done"):
                break
    print()
    return "".join(full)


# ---------------- TTS ----------------
async def _edge_save(text: str, voice: str, path: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(path)


def speak_en(text: str):
    if not text.strip():
        return
    # Strip markdown / fenced code blocks before narrating
    spoken = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    spoken = re.sub(r"[*_`#>|]+", "", spoken)
    spoken = re.sub(r"\s+", " ", spoken).strip()
    if not spoken:
        return
    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.close()
    try:
        asyncio.run(_edge_save(spoken, EN_VOICE, tmp.name))
        pygame.mixer.music.load(tmp.name)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(50)
        pygame.mixer.music.unload()
    finally:
        try:
            os.remove(tmp.name)
        except OSError:
            pass


# ---------------- Phase / language detection ----------------
def is_feedback_phase(text: str) -> bool:
    """The Chinese feedback section starts with the '## 评分报告' header."""
    return "评分报告" in text or "评分项" in text


def is_part2_cue_card(text: str) -> bool:
    """Detect the Part 2 cue card so we can use longer silence tolerance afterwards."""
    return "you should say" in text.lower() or "one to two minutes" in text.lower()


# ---------------- Main loop ----------------
def main():
    pygame.mixer.init()
    whisper = load_whisper()
    threshold = calibrate_threshold()
    silence_end = SILENCE_END_SEC

    history = [{"role": "user", "content": KICKOFF_MESSAGE}]
    feedback_done = False

    while True:
        print("\n🎓 examiner:")
        reply = stream_chat(history)
        history.append({"role": "assistant", "content": reply})

        if is_feedback_phase(reply):
            print("\n[done] feedback printed above. Exiting.")
            feedback_done = True
            break

        # Speak the examiner's English turn
        speak_en(reply)

        # Adapt silence threshold if a cue card was just delivered
        if is_part2_cue_card(reply):
            silence_end = PART2_SILENCE_END_SEC
            print(f"[part2] silence tolerance bumped to {silence_end}s for long turn")
        else:
            silence_end = SILENCE_END_SEC

        # Record candidate
        audio = record_until_silence(threshold, silence_end)
        if audio.size == 0:
            print("[loop] no input, ending test.")
            break

        print("[whisper] transcribing...")
        t0 = time.time()
        text = transcribe(whisper, audio)
        print(f"👤 you ({time.time()-t0:.1f}s): {text}")

        if not text.strip():
            continue

        low = text.lower().strip(" .,!?")
        if low in {"stop", "exit", "quit", "feedback now", "end the test"}:
            history.append({"role": "user", "content": "feedback now"})
            continue
        if low in {"skip to part 2", "next part"}:
            history.append({"role": "user", "content": "skip to part 2"})
            continue

        history.append({"role": "user", "content": text})


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nbye.")
        sys.exit(0)
