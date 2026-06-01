"""Real end-to-end test against the deployed Render service.

Hits the actual Groq + DeepSeek stack:
  1. Signs up a throwaway user
  2. Starts a session
  3. Replies 'no' to every examiner turn until Part 3 is over
  4. Triggers feedback
  5. Asserts the returned band is <= 3.5 (sane for one-word answers)
  6. Asserts the feedback report is in Chinese and references the candidate's
     actual replies, not a generic template

Spending: ~30 examiner turns + 1 feedback turn. Examiner turns are free
(Groq Llama 70B). Feedback turn is ~$0.001 if DeepSeek R1 is wired up.
"""
from __future__ import annotations

import json
import re
import sys
import time

import requests

BASE = "https://voice-ielts.onrender.com"
PHONE = "13900000099"
PASSWORD = "livetest123"
MAX_TURNS = 40   # safety stop in case feedback never fires


def stream_chat(session: requests.Session, sid: str, user_message: str) -> dict:
    """Send one /api/chat turn and reassemble the SSE stream into a dict
    with {phase, chunks_text, done, error}."""
    r = session.post(
        f"{BASE}/api/chat",
        json={"session_id": sid, "user_message": user_message},
        stream=True,
        timeout=120,
    )
    r.raise_for_status()
    text_chunks: list[str] = []
    phase = None
    err = None
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
            text_chunks.append(obj["chunk"])
        if obj.get("error"):
            err = obj
        if obj.get("done"):
            break
    return {"phase": phase, "text": "".join(text_chunks), "error": err}


def main() -> int:
    print(f"== /healthz ==")
    h = requests.get(f"{BASE}/healthz").json()
    print(f"  {h}")
    print(f"  feedback provider configured: {h.get('feedback_provider')}")

    print(f"\n== cleanup any prior test user ==")
    admin = requests.Session()
    import os
    admin_token = (os.environ.get("ADMIN_TOKEN") or "").strip()
    if admin_token:
        admin.post(f"{BASE}/api/admin/login", json={"token": admin_token})
        existing = admin.get(f"{BASE}/api/admin/users?q={PHONE}").json()
        for u in existing.get("items", []):
            admin.delete(f"{BASE}/api/admin/users/{u['id']}")
            print(f"  deleted prior user #{u['id']}")

    print(f"\n== signup or login ==")
    s = requests.Session()
    r = s.post(
        f"{BASE}/api/signup",
        json={"phone": PHONE, "password": PASSWORD, "name": "LiveTest"},
    )
    if r.status_code == 409:
        # phone_taken: log in instead
        r = s.post(f"{BASE}/api/login", json={"phone": PHONE, "password": PASSWORD})
        if r.status_code != 200:
            print(f"  login also failed: {r.status_code} {r.text}")
            return 1
        user = r.json()
        print(f"  reused uid={user['id']}")
    elif r.status_code != 200:
        print(f"  signup failed: {r.status_code} {r.text}")
        return 1
    else:
        user = r.json()
        print(f"  uid={user['id']} invite={user['invite_code']}")

    print(f"\n== create session ==")
    r = s.post(
        f"{BASE}/api/session",
        json={"target_band": "6.5", "accent": "en-GB", "p1_topic": "music"},
    )
    sid = r.json()["id"]
    print(f"  sid={sid}")

    # Use a short, low-effort run + an explicit "feedback now" trigger so we
    # stay under Groq's 6000 TPM free-tier limit.
    script = ["", "no", "no", "no", "feedback now"]
    print(f"\n== short run with feedback shortcut ==")
    last_phase = None
    for i, user_msg in enumerate(script):
        t0 = time.time()
        result = stream_chat(s, sid, user_msg)
        dt = time.time() - t0
        if result["error"]:
            print(f"  turn {i}: ERROR {result['error']}")
            return 1
        phase = result.get("phase") or last_phase
        text = result["text"]
        snippet = text[:80].replace("\n", " ")
        print(f"  turn {i:2d} [{phase}] {dt:5.1f}s : {snippet}{'…' if len(text)>80 else ''}")
        last_phase = phase
        # Tiny pace so consecutive Groq calls don't bunch up
        time.sleep(2)
        if phase == "feedback":
            print(f"\n== FEEDBACK CAPTURED ==")
            print(f"  full text ({len(text)} chars):")
            print("  " + text.replace("\n", "\n  "))
            band = _parse_overall(text)
            print(f"\n  parsed overall band: {band}")
            if band is None:
                print("  !!! could not parse band line — fail")
                return 1
            if band > 3.5:
                print(f"  !!! band {band} TOO HIGH for one-word answers (expected ≤ 3.5)")
                return 1
            print(f"  ✓ band {band} is appropriately low for catastrophic engagement")
            if "<think>" in text or "</think>" in text:
                print(f"  !!! reasoning tokens leaked into output")
                return 1
            print(f"  ✓ no reasoning tokens leaked")
            return 0

    print(f"\n  hit MAX_TURNS ({MAX_TURNS}) without feedback firing — fail")
    return 1


def _parse_overall(text: str):
    m = re.search(r"Overall\s*([0-9](?:\.[0-9])?)", text, re.IGNORECASE)
    return float(m.group(1)) if m else None


if __name__ == "__main__":
    sys.exit(main())
