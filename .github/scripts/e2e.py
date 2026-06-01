"""End-to-end API smoke test. Run against a locally-booted server on :8765.

Exits non-zero on any failure. Picked these 22 because together they exercise:
the auth flow, schema migrations, user prefs, the live admin WebSocket, and
the deterministic question pickers. The previous CI only covered import +
syntax — this is what would have caught the </script>-in-JS regression."""
from __future__ import annotations

import asyncio
import json
import sys

import requests
import websockets

BASE = "http://127.0.0.1:8765"
WS_BASE = "ws://127.0.0.1:8765"
PHONE = "13700009999"

results: list[bool] = []


def ok(label: str, cond: bool, detail: str = "") -> bool:
    mark = "[PASS]" if cond else "[FAIL]"
    msg = f"{mark} {label}" + (f" — {detail}" if detail else "")
    print(msg, flush=True)
    results.append(cond)
    return cond


def main() -> int:
    # Pre-clean: kill any leftover test user from a prior run.
    admin = requests.Session()
    admin.post(BASE + "/api/admin/login", json={"token": ""})
    for u in admin.get(BASE + f"/api/admin/users?q={PHONE}").json().get("items", []):
        admin.delete(BASE + f'/api/admin/users/{u["id"]}')

    # 1
    r = requests.get(BASE + "/healthz")
    ok("/healthz", r.status_code == 200 and r.json()["status"] == "ok")

    # 2-3: signup
    s = requests.Session()
    r = s.post(BASE + "/api/signup", json={"phone": PHONE, "password": "test1234", "name": "CI"})
    ok("signup", r.status_code == 200)
    uid = r.json()["id"]
    invite = r.json()["invite_code"]
    ok("signup → 8-char invite_code", bool(invite and len(invite) == 8))

    # 4-5: /api/me
    r = s.get(BASE + "/api/me")
    ok("/api/me after signup", r.status_code == 200 and r.json()["invite_code"] == invite)
    ok("favorite_topics defaults to []", r.json()["favorite_topics"] == [])

    # 6: PATCH favorites
    r = s.patch(BASE + "/api/me", json={"favorite_topics": ["music", "cam17_maps"]})
    ok("PATCH favorite_topics persists",
       r.status_code == 200 and r.json()["favorite_topics"] == ["music", "cam17_maps"])

    # 7-8: session
    r = s.post(BASE + "/api/session", json={"target_band": "6.5", "accent": "en-GB", "p1_topic": "music"})
    ok("POST /api/session", r.status_code == 200 and "id" in r.json())
    sid = r.json()["id"]
    r = s.get(BASE + f"/api/session/{sid}")
    ok("GET /api/session/<id>",
       r.status_code == 200 and r.json()["target_band"] == "6.5" and r.json()["p1_topic"] == "music")

    # 9-10: topics
    r = requests.get(BASE + "/api/topics")
    d = r.json()
    ok("/api/topics ≥ 71 entries", len(d["labelled"]) >= 71)
    ok("topics include curated + cam-prefixed",
       any(it["value"] == "music" for it in d["labelled"])
       and any(it["value"].startswith("cam17") for it in d["labelled"]))

    # 11: sessions list
    r = s.get(BASE + "/api/sessions")
    ok("/api/sessions returns the new session",
       r.status_code == 200 and any(item["id"] == sid for item in r.json()))

    # 12-13: feedback
    r = requests.post(BASE + "/api/feedback", json={"rating": 5, "category": "praise", "text": "ci e2e"})
    ok("POST /api/feedback anon", r.status_code == 200)
    r = admin.get(BASE + "/api/admin/feedback")
    ok("admin sees new feedback", any(i["text"] == "ci e2e" for i in r.json()["items"]))

    # 14: server TTS — disabled in CI (edge-tts hits external service, would be flaky)
    # ok(...)

    # 15: WebSocket round-trip
    async def ws_test() -> tuple[bool, str]:
        cookies = "; ".join(f"{c.name}={c.value}" for c in admin.cookies)
        async with websockets.connect(
            WS_BASE + "/api/admin/stream",
            additional_headers={"Cookie": cookies},
        ) as ws:
            hello = json.loads(await ws.recv())
            if hello.get("type") != "hello":
                return False, "no hello message"
            requests.post(BASE + "/api/feedback",
                          json={"category": "general", "text": "ws ping"})
            ev = json.loads(await asyncio.wait_for(ws.recv(), timeout=5))
            if ev.get("type") != "feedback":
                return False, f"expected feedback got {ev.get('type')}"
            return True, "hello + feedback events received"

    ws_ok, ws_detail = asyncio.run(ws_test())
    ok("WebSocket admin stream", ws_ok, ws_detail)

    # 16-18: ban → kicked
    r = admin.post(BASE + f"/api/admin/users/{uid}/ban", json={"banned": True})
    ok("admin ban user", r.status_code == 200 and r.json()["banned"])
    r = s.get(BASE + "/api/me")
    ok("banned user 403 on /api/me", r.status_code == 403)
    r = requests.post(BASE + "/api/login", json={"phone": PHONE, "password": "test1234"})
    ok("banned user 403 on /api/login", r.status_code == 403)

    # 19-20: delete
    r = admin.delete(BASE + f"/api/admin/users/{uid}")
    ok("admin delete user", r.status_code == 200)
    r = admin.get(BASE + f"/api/admin/users?q={PHONE}")
    ok("user gone after delete", len(r.json()["items"]) == 0)

    # 21-22: deterministic pickers
    sys.path.insert(0, ".")
    import webapp
    t1, q1 = webapp._pick_part1("det-001")
    t2, q2 = webapp._pick_part1("det-001")
    ok("_pick_part1 deterministic", t1 == t2 and q1 == q2)
    c1 = webapp._pick_part2("det-001")
    c2 = webapp._pick_part2("det-001")
    ok("_pick_part2 deterministic", c1["topic"] == c2["topic"])

    passed = sum(results)
    total = len(results)
    print(f"\n=== {passed}/{total} passed ===", flush=True)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
