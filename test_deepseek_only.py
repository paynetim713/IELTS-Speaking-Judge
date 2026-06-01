"""Minimal test that exercises ONLY the feedback path (DeepSeek), bypassing
Groq entirely. Useful when Groq's daily quota is exhausted but we still
want to verify the band-scoring pipeline.

Sends a single 'feedback now' message — server treats this as the feedback
trigger and routes straight to the configured feedback provider.
"""
from __future__ import annotations

import json
import re
import sys
import time

import requests

# Windows console defaults to GBK which can't encode ✓/×. Force utf-8.
try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
except Exception:
    pass

BASE = "https://voice-ielts.onrender.com"
PHONE = "13900000099"
PASSWORD = "livetest123"


def stream_chat(session, sid, user_message):
    r = session.post(
        f"{BASE}/api/chat",
        json={"session_id": sid, "user_message": user_message},
        stream=True, timeout=120,
    )
    r.raise_for_status()
    chunks, phase, err = [], None, None
    for raw in r.iter_lines():
        if not raw:
            continue
        line = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        try:
            obj = json.loads(data)
        except json.JSONDecodeError:
            continue
        if obj.get("phase"):
            phase = obj["phase"]
        if obj.get("chunk"):
            chunks.append(obj["chunk"])
        if obj.get("error"):
            err = obj
        if obj.get("done"):
            break
    return {"phase": phase, "text": "".join(chunks), "error": err}


def main():
    print("== /healthz ==")
    h = requests.get(f"{BASE}/healthz").json()
    print(f"  {h}")

    print("\n== login (reuse prior test user) ==")
    s = requests.Session()
    r = s.post(f"{BASE}/api/login", json={"phone": PHONE, "password": PASSWORD})
    if r.status_code != 200:
        r = s.post(f"{BASE}/api/signup", json={"phone": PHONE, "password": PASSWORD, "name": "T"})
        if r.status_code != 200:
            print(f"  failed: {r.status_code} {r.text}")
            return 1
    print(f"  uid={r.json()['id']}")

    print("\n== new session ==")
    r = s.post(f"{BASE}/api/session", json={"target_band": "6.5", "accent": "en-GB", "p1_topic": "music"})
    sid = r.json()["id"]
    print(f"  sid={sid}")

    print("\n== fire 'feedback now' directly → routes to DeepSeek ==")
    t0 = time.time()
    result = stream_chat(s, sid, "feedback now")
    dt = time.time() - t0
    print(f"  took {dt:.1f}s")
    if result["error"]:
        print(f"  ERROR: {result['error']}")
        return 1
    text = result["text"]
    print(f"\n  ─── feedback report ({len(text)} chars) ───")
    print(text)
    print(f"  ──────────────────────────────────────")

    # Validation
    band = None
    m = re.search(r"Overall\s*([0-9](?:\.[0-9])?)", text)
    if m:
        band = float(m.group(1))
        print(f"\n  parsed Overall band = {band}")
    else:
        print("\n  !!! no Overall band parsed from output")
        return 1

    # NOTE: empty history skips _candidate_stats → no clamp → model picks a
    # default mid-band score. That's expected here; the floor kicks in for
    # real sessions where the candidate actually spoke. So we just check
    # that DeepSeek produced a parseable, well-formatted score line.

    if "<think>" in text or "</think>" in text:
        print(f"  !!! <think> tags leaked into UI")
        return 1
    print(f"  ✓ no reasoning tokens leaked")

    # Verify it followed the IELTS template, not some generic interview format.
    expected_markers = ["F&C", "Lex", "Gram", "Pron", "Overall"]
    missing = [m for m in expected_markers if m not in text]
    if missing:
        print(f"  !!! template markers missing: {missing}")
        return 1
    print(f"  ✓ all 5 band criteria present (F&C/Lex/Gram/Pron/Overall)")

    print("\n=== PASS — DeepSeek-v4-pro is producing valid IELTS feedback ===")
    print("    Real sessions with transcript will clamp scores to the")
    print("    catastrophic-engagement floor (2.0-3.5) when candidates")
    print("    only give one-word answers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
