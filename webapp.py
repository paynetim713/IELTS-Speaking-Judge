r"""
IELTS Examiner web UI backend.

Streams ollama responses over Server-Sent Events. Browser handles STT/TTS.

A phase hint is injected before each generation so the 7B model knows
where it is in the test (Part 1 Q n, time to deliver cue card, etc.).

Run:
    .\.venv\Scripts\python.exe webapp.py
"""

import json
import os
import random
import re
import secrets
import time
import uuid
from pathlib import Path

import bcrypt
import requests
from fastapi import FastAPI, HTTPException, Request

import llm_provider
import db as _db_mod
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# LLM model selection is delegated to llm_provider.py — it reads LLM_PROVIDER
# (ollama|groq) and LLM_EXAMINER_MODEL / LLM_FEEDBACK_MODEL from env. We keep
# these aliases so the rest of webapp.py reads naturally.
MODEL_NAME = llm_provider.examiner_model()
# Feedback fallback chain stays Ollama-only — on Groq there's no 'bigger' tier,
# both examiner and feedback use the same 70B model and the chain collapses to one.
if llm_provider.PROVIDER == "groq":
    FEEDBACK_MODEL_CANDIDATES = [llm_provider.feedback_model()]
else:
    FEEDBACK_MODEL_CANDIDATES = [
        os.environ.get("IELTS_FEEDBACK_MODEL"),
        llm_provider.feedback_model(),
        "deepseek-r1:14b",
        "qwen2.5:14b-instruct-q3_K_M",
    ]
    FEEDBACK_MODEL_CANDIDATES = [m for m in FEEDBACK_MODEL_CANDIDATES if m]
FEEDBACK_MODEL_NAME = FEEDBACK_MODEL_CANDIDATES[0]  # legacy alias for logs

# DeepSeek R1 emits <think>...</think> reasoning blocks before the actual answer.
# Strip them before clamping / showing the user — they leak the band-anchor protocol.
_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


def _strip_think_blocks(text: str) -> str:
    if not text:
        return text
    return _THINK_RE.sub("", text).strip()


def _pick_feedback_model() -> str:
    """First model in the priority list that is actually pulled."""
    for name in FEEDBACK_MODEL_CANDIDATES:
        if _model_available(name):
            return name
    return MODEL_NAME  # ultimate fallback: the examiner model itself

_MODEL_AVAIL_CACHE: dict = {}


def _model_available(name: str) -> bool:
    """Cached check against the provider's model list. Cache for 60s so we don't hit it every chat."""
    now = time.time()
    cached = _MODEL_AVAIL_CACHE.get(name)
    if cached and now - cached[0] < 60:
        return cached[1]
    tags = llm_provider.list_available_models()
    # Match either exact id/tag or Ollama-style short form (qwen2.5:14b → qwen2.5:14b-...)
    ok = (
        name in tags
        or any(t.startswith(name + "-") or t == name + ":latest" for t in tags)
    )
    # On Groq, an empty model list almost certainly means the listing endpoint
    # is rate-limited — don't pessimistically refuse the model we're configured to use.
    if not tags and llm_provider.PROVIDER == "groq":
        ok = True
    _MODEL_AVAIL_CACHE[name] = (now, ok)
    return ok

HERE = Path(__file__).parent
DB_PATH = HERE / "sessions.db"
_KEY_FILE = HERE / ".secret_key"

# Production sets IELTS_ENV=prod. In prod we require IELTS_SECRET_KEY in env;
# falling back to a file-backed key on a stateless serverless host (Render free
# tier respawns) would log everyone out on every restart.
IELTS_ENV = (os.environ.get("IELTS_ENV") or "dev").strip().lower()
IS_PROD = IELTS_ENV in ("prod", "production")


def _load_or_create_secret() -> str:
    env_key = os.environ.get("IELTS_SECRET_KEY")
    if env_key:
        return env_key
    if IS_PROD:
        raise RuntimeError(
            "IELTS_SECRET_KEY env var is required when IELTS_ENV=prod. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    if _KEY_FILE.exists():
        return _KEY_FILE.read_text().strip()
    key = secrets.token_hex(32)
    _KEY_FILE.write_text(key)
    return key


SECRET_KEY = _load_or_create_secret()


def _allowed_origins() -> list[str]:
    """Dev: localhost variants. Prod: read CORS_ORIGINS comma-list from env."""
    extra = [o.strip() for o in (os.environ.get("CORS_ORIGINS") or "").split(",") if o.strip()]
    dev = [
        "http://localhost:8000", "http://127.0.0.1:8000",
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:8765", "http://127.0.0.1:8765",
    ]
    return list(dict.fromkeys((extra + ([] if IS_PROD else dev))))


app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    max_age=60 * 60 * 24 * 30,   # 30 days
    # In prod the cookie MUST be secure + cross-site so the frontend on Cloudflare
    # Pages can carry it to the Render API.
    same_site="none" if IS_PROD else "lax",
    https_only=IS_PROD,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# ── Session storage: sqlite for local dev, Postgres (Supabase) when DATABASE_URL is set ──
def _db():
    """Backwards-compat alias used throughout this module."""
    return _db_mod.db()


def _init_db():
    with _db() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id          TEXT PRIMARY KEY,
                created_at  REAL NOT NULL,
                updated_at  REAL NOT NULL,
                status      TEXT NOT NULL,
                history     TEXT NOT NULL,
                phase       TEXT NOT NULL,
                feedback    TEXT
            )
            """
        )
        c.execute("CREATE INDEX IF NOT EXISTS sessions_updated_idx ON sessions(updated_at DESC)")
        # Migration: old schema used email; switch to phone-only identifier.
        existing_user_cols = _db_mod.column_names(c, "users")
        if "email" in existing_user_cols and "phone" not in existing_user_cols:
            c.execute("DROP TABLE users")
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                phone          TEXT UNIQUE NOT NULL,
                password_hash  TEXT NOT NULL,
                name           TEXT,
                created_at     REAL NOT NULL
            )
            """
        )
    # Additive ALTERs: each in its own connection/transaction so a duplicate-
    # column error on one doesn't poison the others (postgres rolls back the
    # whole transaction on any error; sqlite tolerates per-statement failure
    # within a single transaction, but doing it the same way works for both).
    for ddl in [
        "ALTER TABLE sessions ADD COLUMN user_id INTEGER",
        "ALTER TABLE sessions ADD COLUMN target_band TEXT",
        "ALTER TABLE sessions ADD COLUMN accent TEXT",
        "ALTER TABLE sessions ADD COLUMN p1_topic TEXT",
        "ALTER TABLE users ADD COLUMN target_band TEXT",
        "ALTER TABLE users ADD COLUMN accent TEXT",
        "ALTER TABLE users ADD COLUMN preferred_topic TEXT",
    ]:
        try:
            with _db() as c:
                c.execute(ddl)
        except Exception as e:
            if not _db_mod.is_duplicate_column_error(e):
                raise
            # column already exists — fine
    with _db() as c:
        c.execute("CREATE INDEX IF NOT EXISTS sessions_user_idx ON sessions(user_id, updated_at DESC)")


_init_db()


def _load_session(sid: str):
    with _db() as c:
        row = c.execute("SELECT * FROM sessions WHERE id = ?", (sid,)).fetchone()
    if not row:
        return None
    keys = row.keys()
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "status": row["status"],
        "history": json.loads(row["history"]),
        "phase": row["phase"],
        "feedback": row["feedback"],
        "user_id":     row["user_id"]     if "user_id"     in keys else None,
        "target_band": row["target_band"] if "target_band" in keys else None,
        "accent":      row["accent"]      if "accent"      in keys else None,
        "p1_topic":    row["p1_topic"]    if "p1_topic"    in keys else None,
    }


def _save_session(sid, history, phase, status, feedback, user_id=None,
                  target_band=None, accent=None, p1_topic=None):
    now = time.time()
    with _db() as c:
        c.execute(
            """
            INSERT INTO sessions (id, created_at, updated_at, status, history, phase, feedback,
                                  user_id, target_band, accent, p1_topic)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                updated_at  = excluded.updated_at,
                status      = excluded.status,
                history     = excluded.history,
                phase       = excluded.phase,
                feedback    = COALESCE(excluded.feedback, sessions.feedback)
            """,
            (sid, now, now, status, json.dumps(history, ensure_ascii=False), phase, feedback,
             user_id, target_band, accent, p1_topic),
        )


# ── Auth helpers ──
def _require_user(request: Request) -> int:
    uid = request.session.get("user_id")
    if not uid:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return uid


def _user_row(user_id: int):
    with _db() as c:
        row = c.execute(
            "SELECT id, phone, name, target_band, accent, preferred_topic, created_at "
            "FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    return dict(row) if row else None


# Chinese mobile: 11 digits starting with 1 (1[3-9]xxxxxxxxx). Strip any +86 country code first.
_PHONE_RE = re.compile(r"^1[3-9]\d{9}$")


def _normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw or "")
    if len(digits) == 13 and digits.startswith("86"):
        digits = digits[2:]
    return digits


def _owns_session(sess: dict, user_id: int) -> bool:
    """Strict ownership: legacy sessions (user_id NULL) are orphaned and invisible."""
    return sess.get("user_id") == user_id


# ── IELTS pacing (content-aware) ──
# The strip and hints used to be purely position-based (Nth assistant turn → phase X),
# but a 7B model often jumps phases (e.g. delivers the cue card after 5 questions
# instead of 6). So we *derive* each past reply's true phase from its content
# (cue-card markers, feedback markers) and only fall back to position-based defaults
# when content has no signal. This keeps the UI strip and next-turn hint in sync.
PART1_QUESTIONS = 4    # 1 topic frame, 4 questions on that topic
PART3_QUESTIONS = 5    # 2 sub-themes: 3 + 2


# ── Server-driven question bank: see question_bank.py.
# The model is the "voice"; the server decides WHICH topic, cue card, and Part 3
# sub-themes apply so the 7B can't drift off-topic or hallucinate a different cue card.
# Bank combines 15 curated high-frequency topics with verbatim Cambridge IELTS 4-17 extractions
# (51 P1 topics, 42 P2 cue cards, 42 P3 theme sets). See build_bank.py + extract_speaking.py.
from question_bank import PART1_BANK, PART2_BANK, PART3_THEMES, DEFAULT_PART3  # noqa: F401


def _session_rng(sid: str | None, salt: str = ""):
    r = random.Random()
    r.seed((sid or "default") + ":" + salt)
    return r


def _pick_part1(sid: str | None, topic_override: str | None = None):
    """Single Part 1 topic, deterministic per session. 4 question focuses on that topic.
    Real IELTS: examiner picks ONE familiar topic and stays on it for the whole Part 1."""
    if topic_override and topic_override in PART1_BANK:
        return topic_override, list(PART1_BANK[topic_override][:4])
    rng = _session_rng(sid, "p1")
    topic = rng.choice(sorted(PART1_BANK.keys()))
    return topic, list(PART1_BANK[topic][:4])


def _pick_part2(sid: str | None):
    rng = _session_rng(sid, "p2")
    return rng.choice(PART2_BANK)


def _pick_part3(card: dict, sid: str | None):
    """2 sub-themes × 2 focuses, locked to the Part 2 cue card."""
    themes = PART3_THEMES.get(card.get("p3_key") or "", DEFAULT_PART3)
    # Mix sub-theme ORDER per session for variety, but keep focus order stable.
    rng = _session_rng(sid, "p3")
    themes = list(themes)
    rng.shuffle(themes)
    return themes


def _build_cue_card(card: dict) -> str:
    bullets = "\n".join(f"- {b}" for b in card["bullets"])
    return (
        "Now I'd like you to talk about a topic for one to two minutes. "
        "You'll have one minute to think about what you are going to say. "
        "You can make some notes to help you if you wish.\n\n"
        f"Describe {card['topic']}.\n"
        f"You should say:\n{bullets}\n"
        f"And explain {card['explain']}."
    )


def _prev_examiner_openers(history: list, n: int = 3) -> list:
    """Last n examiner turn openers (first 4 words) — used to discourage repetition."""
    asst = [m.get("content", "") for m in history if m.get("role") == "assistant"]
    out = []
    for c in asst[-n:]:
        words = (c or "").strip().split()[:4]
        if words:
            out.append(" ".join(words))
    return out


DISCOURSE_MARKERS = (
    "however", "moreover", "furthermore", "additionally", "in addition",
    "nevertheless", "consequently", "therefore", "thus", "hence",
    "for instance", "for example", "such as", "particularly", "specifically",
    "although", "though", "whereas", "while", "despite", "in spite of",
    "because", "since", "as a result", "in fact", "indeed", "actually",
    "on the other hand", "on the contrary", "in contrast", "similarly",
    "to be honest", "to be fair", "frankly", "personally",
)


def _candidate_stats(history: list):
    """Quantitative signals so feedback can anchor band scores, not just guess."""
    user_msgs = [m.get("content", "") for m in history
                 if m.get("role") == "user" and m.get("content")]
    user_msgs = [m for m in user_msgs if "ready to start the test" not in m.lower()
                 and m.lower().strip() not in {"feedback now", "stop", "end", "exit"}]
    if not user_msgs:
        return None
    words_per_turn = [len(m.split()) for m in user_msgs]
    if not words_per_turn:
        return None
    total = sum(words_per_turn)
    longest_idx = max(range(len(words_per_turn)), key=lambda i: words_per_turn[i])
    shortest_idx = min(range(len(words_per_turn)), key=lambda i: words_per_turn[i])

    all_text = " ".join(user_msgs)
    all_low = all_text.lower()
    tokens = re.findall(r"[A-Za-z']+", all_low)
    unique_tokens = len(set(tokens))
    ttr = (unique_tokens / len(tokens)) if tokens else 0.0
    marker_count = sum(1 for m in DISCOURSE_MARKERS if m in all_low)
    sentences = [s.strip() for s in re.split(r"[.!?]+", all_text) if s.strip()]
    avg_sent_words = (sum(len(s.split()) for s in sentences) / len(sentences)) if sentences else 0.0

    def _short(s, n=180):
        return s[:n] + ("…" if len(s) > n else "")

    return {
        "turns": len(user_msgs),
        "total_words": total,
        "avg_words": total / len(words_per_turn),
        "longest_words": words_per_turn[longest_idx],
        "longest_quote": _short(user_msgs[longest_idx]),
        "shortest_words": words_per_turn[shortest_idx],
        "shortest_quote": _short(user_msgs[shortest_idx], 100),
        "unique_tokens": unique_tokens,
        "vocab_diversity": ttr,                # TTR: 0..1, ~0.5+ = good
        "discourse_markers": marker_count,
        "avg_sentence_words": avg_sent_words,
    }


def _full_transcript(history: list, max_chars: int = 6000) -> str:
    """Compact full transcript for embedding in the feedback prompt."""
    skip_user = {"feedback now", "stop", "end", "exit", "end → feedback", "end -> feedback"}
    lines = []
    for m in history:
        role = m.get("role")
        content = (m.get("content") or "").strip()
        if not content:
            continue
        if role == "user":
            if "ready to start the test" in content.lower():
                continue
            if content.lower().strip(" .,!?") in skip_user:
                continue
            lines.append(f"CANDIDATE: {content}")
        elif role == "assistant":
            lines.append(f"EXAMINER: {content}")
    out = "\n".join(lines)
    if len(out) > max_chars:
        out = "…(earlier turns omitted)…\n" + out[-max_chars:]
    return out


def _server_band_ranges(stats):
    """Compute defensible (low, high) band ranges for each criterion from objective signals.
    These become HARD bounds the model cannot escape — anti-inflation by construction."""
    awt = stats["avg_words"]
    dm = stats["discourse_markers"]
    ttr = stats["vocab_diversity"]
    asw = stats["avg_sentence_words"]

    # F&C — drive by length, lifted by discourse markers
    if   awt < 15: fc = [4.5, 5.5]
    elif awt < 25: fc = [5.0, 6.0]
    elif awt < 40: fc = [5.5, 6.0]
    elif awt < 60: fc = [6.0, 6.5]
    elif awt < 90: fc = [6.0, 7.0]
    else:          fc = [6.5, 7.5]
    if dm >= 5:  fc[1] = min(fc[1] + 0.5, 7.5)
    if dm >= 10: fc[1] = min(fc[1] + 0.5, 8.0)

    # Lex — TTR only, with hard ceilings
    if   ttr < 0.40: lex = [4.5, 5.5]
    elif ttr < 0.45: lex = [5.0, 6.0]
    elif ttr < 0.50: lex = [5.5, 6.0]
    elif ttr < 0.55: lex = [5.5, 6.5]
    elif ttr < 0.60: lex = [6.0, 7.0]
    else:            lex = [6.5, 7.5]

    # Gram — avg sentence length proxy
    if   asw < 7:  gram = [4.5, 5.5]
    elif asw < 11: gram = [5.0, 6.0]
    elif asw < 15: gram = [5.5, 6.5]
    else:          gram = [6.0, 7.0]

    # Pron — cannot judge from text; honest middle range
    pron = [5.5, 6.5]

    return {"fc": tuple(fc), "lex": tuple(lex), "gram": tuple(gram), "pron": tuple(pron)}


_SCORE_LINE_RE = re.compile(
    r"F&C\s*([0-9](?:\.[0-9])?)\s*\|\s*Lex\s*([0-9](?:\.[0-9])?)\s*\|\s*Gram\s*([0-9](?:\.[0-9])?)\s*"
    r"\|\s*Pron\s*([0-9](?:\.[0-9])?)\s*\|\s*Overall\s*([0-9](?:\.[0-9])?)",
    re.IGNORECASE,
)


def _clamp_to_half(x: float) -> float:
    return round(x * 2) / 2


def _clamp_feedback(text: str, stats) -> str:
    """Parse the score line out of the model's feedback and force-clamp every
    sub-band to its server-computed range. Then recompute Overall from clamped
    sub-bands so the report is internally consistent. If model output didn't
    include a parseable score line, return unchanged."""
    if not text or not stats:
        return text
    m = _SCORE_LINE_RE.search(text)
    if not m:
        return text
    ranges = _server_band_ranges(stats)
    raw = {
        "fc":   float(m.group(1)),
        "lex":  float(m.group(2)),
        "gram": float(m.group(3)),
        "pron": float(m.group(4)),
    }
    clamped = {}
    notes = []
    for key, lo_hi in ranges.items():
        lo, hi = lo_hi
        v = raw[key]
        cv = max(lo, min(hi, v))
        cv = _clamp_to_half(cv)
        clamped[key] = cv
        if abs(cv - v) >= 0.5:
            notes.append(f"{key.upper()} {v} → {cv}")
    overall = _clamp_to_half(sum(clamped.values()) / 4)
    new_line = (f"F&C {clamped['fc']:.1f} | Lex {clamped['lex']:.1f} | "
                f"Gram {clamped['gram']:.1f} | Pron {clamped['pron']:.1f} | "
                f"Overall {overall:.1f}")
    out = text[:m.start()] + new_line + text[m.end():]
    if notes:
        # Surface that the server overrode the model so the user can see why.
        out += f"\n\n> 服务端反通胀截断:{' / '.join(notes)}(基于客观统计的合法区间)"
    return out


def _build_range_block(stats) -> str:
    """Format the server-computed band ranges as a hard-bounds block for the prompt."""
    r = _server_band_ranges(stats)
    return (
        "========== SERVER-COMPUTED HARD BAND RANGES (you MUST stay inside) ==========\n"
        f"  F&C must be between {r['fc'][0]:.1f} and {r['fc'][1]:.1f}\n"
        f"  Lex must be between {r['lex'][0]:.1f} and {r['lex'][1]:.1f}\n"
        f"  Gram must be between {r['gram'][0]:.1f} and {r['gram'][1]:.1f}\n"
        f"  Pron must be between {r['pron'][0]:.1f} and {r['pron'][1]:.1f} "
        "(narrow because text alone can't reveal pronunciation)\n"
        "  Overall = round(mean × 2) / 2 — NO creative weighting\n"
        "These ranges are derived directly from the candidate's measured TTR, length and discourse "
        "markers. They will be enforced by the server after you reply — anything outside will be "
        "CLAMPED automatically and exposed to the candidate as 'server anti-inflation'. So save us "
        "both the trouble and score inside the ranges.\n\n"
    )


def _band_anchored_feedback_hint(stats, history, target_band=None):
    """Build a feedback hint that grounds every band score in the candidate's
    actual words. STRICT mode — anti-inflation rules are enforced because
    LLM graders default to flattery."""
    transcript = _full_transcript(history)
    band_target = (
        f"\nThe candidate's stated target is band {target_band}. Be honest about whether they reach "
        f"it. Over-scoring hurts their practice — they need to know what's actually blocking them."
    ) if target_band else (
        "\nBe HONEST and tough. Over-scoring is the #1 feedback failure for IELTS practice apps."
    )

    return (
        "Phase=END. You are an experienced IELTS examiner delivering the Chinese feedback report. "
        "Most real candidates score 5.5-6.5; band 7.0+ requires clear, repeated evidence of higher "
        "range — not just long answers. Follow the protocol BELOW STRICTLY." + band_target + "\n\n"
        "========== FULL TRANSCRIPT ==========\n"
        f"{transcript}\n"
        "========== END TRANSCRIPT ==========\n\n"
        "========== OBJECTIVE SIGNALS (from the candidate's actual speech) ==========\n"
        f"- Candidate turns: {stats['turns']}\n"
        f"- Total words: {stats['total_words']}\n"
        f"- Avg words / turn: {stats['avg_words']:.1f}\n"
        f"- Type-token ratio (unique/total): {stats['vocab_diversity']:.3f}\n"
        f"- Discourse markers used: {stats['discourse_markers']}\n"
        f"- Avg sentence length: {stats['avg_sentence_words']:.1f} words\n\n"
        + _build_range_block(stats) +
        "========== STRICT BAND ANCHORS — do NOT inflate ==========\n"
        "F&C (Fluency & Coherence):\n"
        "  - Avg words/turn <15 → 5.0   15-25 → 5.5   25-40 → 6.0   40-60 → 6.5   60-90 → 7.0\n"
        "  - 7.5 requires ALL: 60+ avg words AND 8+ discourse markers AND varied structures\n"
        "  - 8.0+ requires near-native sustained flow — almost never warranted in mock tests\n"
        "Lex (Lexical Resource):\n"
        "  - TTR <0.40 → 5.0   0.40-0.45 → 5.5   0.45-0.50 → 6.0   0.50-0.55 → 6.5\n"
        "  -       0.55-0.60 → 7.0   >0.60 → 7.5\n"
        "  - HARD CAP 6.0 if 'good / nice / very / really / important / different / like / feel' "
        "appear repeatedly without paraphrase\n"
        "  - 7.0+ requires repeated less-common precise items (significant / particularly / "
        "substantial / diverse / acknowledge / contribute)\n"
        "  - 8.0+ requires idiomatic / nuanced choices throughout — DO NOT assign casually\n"
        "Gram (Grammatical Range & Accuracy):\n"
        "  - Mostly simple sentences joined with 'because / and / but' → 5.5-6.0 max\n"
        "  - First conditional (if...will) + some past perfect / relative clauses correctly used → 6.5\n"
        "  - Sustained variety: passives, perfect aspects, subordinate clauses, modal nuance → 7.0\n"
        "  - 7.5 requires complex structures with rare, minor errors only\n"
        "Pron (Pronunciation):\n"
        "  - Cannot judge from text alone. Default 6.0.\n"
        "  - Lower to 5.5 if obvious L1 transfer in word choice (rices / equipments / advices / "
        "repeatedly missing articles or plurals)\n\n"
        "========== ANTI-INFLATION CHECKS — apply BEFORE writing scores ==========\n"
        "1. If Lex < 6.5, then F&C CANNOT exceed Lex + 0.5 (you can't be fluent without range).\n"
        "2. If Gram < 6.0 (sentences mostly simple), then Overall CANNOT exceed 6.5.\n"
        "3. Long answers built from REPETITIVE simple structures = F&C 6.0-6.5, NOT 7.0+.\n"
        "4. If TTR < 0.50 AND no precise vocabulary, Lex is 6.0 maximum.\n"
        "5. Overall = round((F&C + Lex + Gram + Pron) / 4 × 2) / 2. NO creative averaging.\n"
        "6. Self-check before output: 'Does the transcript SHOW this level, sentence by sentence?' "
        "If you can't point to 3 specific high-band sentences, you're inflating.\n\n"
        "========== REQUIRED OUTPUT (Chinese, EXACT template) ==========\n"
        "## 评分(基于本场对话)\n"
        "F&C x.x | Lex x.x | Gram x.x | Pron x.x | Overall x.x\n"
        "\n"
        "## 主要问题(2-3 条)\n"
        "1. 原句:\"<verbatim quote candidate actually said>\" → 改写:\"<higher-band version>\" — <one-line diagnosis>\n"
        "2. 原句:\"<another verbatim quote>\" → 改写:\"<better>\" — <issue>\n"
        "3. (可选) 原句:\"...\" → 改写:\"...\" — <issue>\n"
        "\n"
        "## 一句话建议\n"
        "<one concrete actionable practice step grounded in the issues above>\n\n"
        "RULES:\n"
        "- 原句 MUST be verbatim from the transcript. Do NOT invent or paraphrase.\n"
        "- 改写 keeps the candidate's meaning but lifts the band level visibly.\n"
        "- Apply ALL anti-inflation checks. Score the transcript you actually see, not a hopeful "
        "version of it. Being honest is more useful than being kind."
    )

_CUE_MARKERS = ("one to two minutes", "you should say", "and explain")
_FEEDBACK_MARKERS_EN = ("f&c", "lexical resource", "grammatical range")
_OVERALL_BAND_RE = re.compile(r"Overall\s*[0-9](?:\.[0-9])?", re.IGNORECASE)


def _is_cue_card(content: str) -> bool:
    low = (content or "").lower()
    return sum(1 for m in _CUE_MARKERS if m in low) >= 2


def _is_feedback_content(content: str) -> bool:
    if not content:
        return False
    if "评分" in content:
        return True
    if _OVERALL_BAND_RE.search(content):
        return True
    low = content.lower()
    return sum(1 for m in _FEEDBACK_MARKERS_EN if m in low) >= 2


def derive_phases(history: list) -> list:
    """
    Walk history left-to-right and classify each assistant reply's phase.
    Content markers (cue card / feedback) override the default progression so
    the UI doesn't get out of sync when the model jumps ahead.
    """
    phases = []
    for m in history:
        if m.get("role") != "assistant":
            continue
        content = m.get("content", "")
        if _is_feedback_content(content):
            phases.append("feedback")
            continue
        if _is_cue_card(content):
            phases.append("part2")
            continue
        if not phases:
            phases.append("intro")
            continue
        last = phases[-1]
        if last == "intro":
            phases.append("part1")
        elif last == "part1":
            phases.append("part1")
        elif last == "part2":
            # cue was already classified above; this non-cue reply is the follow-up
            p2 = sum(1 for p in phases if p == "part2")
            phases.append("part2" if p2 < 2 else "part3")
        elif last == "part3":
            phases.append("part3")
        else:
            phases.append("feedback")
    return phases


_DESCRIBE_RE = re.compile(r"Describe\s+(.+?)\s*(?:\.|\n|$)", re.IGNORECASE)


def _extract_part2_theme(history: list):
    """Pull the cue-card topic (e.g. 'a memorable journey') so Part 3 can stay on theme."""
    for m in history:
        if m.get("role") != "assistant":
            continue
        c = m.get("content", "")
        if _is_cue_card(c):
            m2 = _DESCRIBE_RE.search(c)
            if m2:
                return m2.group(1).strip().rstrip(".")
    return None


def phase_step(history: list):
    upcoming = phase_label(history)
    phases = derive_phases(history)
    if upcoming in ("intro", "feedback"):
        return None
    if upcoming == "part1":
        n = sum(1 for p in phases if p == "part1") + 1
        return f"{min(n, PART1_QUESTIONS)} / {PART1_QUESTIONS}"
    if upcoming == "part2":
        p2 = sum(1 for p in phases if p == "part2")
        return "cue card" if p2 == 0 else "wrap-up"
    if upcoming == "part3":
        n = sum(1 for p in phases if p == "part3") + 1
        return f"{min(n, PART3_QUESTIONS)} / {PART3_QUESTIONS}"
    return None


def phase_label(history: list) -> str:
    """Phase of the upcoming examiner turn — drives the UI progress strip."""
    phases = derive_phases(history)
    if not phases:
        return "intro"
    last = phases[-1]
    if last == "intro":
        return "part1"
    if last == "feedback":
        return "feedback"
    if last == "part1":
        p1 = sum(1 for p in phases if p == "part1")
        return "part2" if p1 >= PART1_QUESTIONS else "part1"
    if last == "part2":
        p2 = sum(1 for p in phases if p == "part2")
        return "part2" if p2 < 2 else "part3"  # second part2 reply is the followup
    if last == "part3":
        p3 = sum(1 for p in phases if p == "part3")
        return "feedback" if p3 >= PART3_QUESTIONS else "part3"
    return "part1"


def phase_hint(history: list, sid: str = None, p1_topic: str = None,
               target_band: str = None) -> str:
    """Return a one-line stage-direction for the examiner's upcoming turn.

    Server-driven: Part 1 topic, Part 2 cue card, and Part 3 sub-themes are all
    picked from curated banks (deterministic per session id) so the 7B can't
    drift off-topic or hallucinate a different cue card.
    """
    upcoming = phase_label(history)
    phases = derive_phases(history)
    variety = _prev_examiner_openers(history, 3)
    variety_hint = (
        f" Vary your opener — do NOT start like any of these recent ones: {variety!r}."
        if variety else ""
    )

    if upcoming == "intro":
        return (
            "Phase=INTRO. Output ONE combined greeting that asks the candidate's name "
            "and where they're from. Pick a different examiner first-name each session. Then stop."
        )

    if upcoming == "part1":
        topic, focuses = _pick_part1(sid, p1_topic)
        n = sum(1 for p in phases if p == "part1") + 1
        focus = focuses[(n - 1) % len(focuses)]
        topic_display = topic.replace("_", " / ")
        ack = (" Briefly acknowledge the candidate's previous answer first "
               "(≤ 1 short sentence — echo a detail they mentioned). Then ask the next question.")

        if n == 1:
            return (
                f"Phase=PART 1 Q1 of {PART1_QUESTIONS}. The topic for ALL of Part 1 is: "
                f"'{topic_display}'. Open with EXACTLY: \"Let's talk about {topic_display}.\" Then "
                f"ask ONE Cambridge-style personal question on this focus: \"{focus}\". Stop."
            )
        if n == PART1_QUESTIONS:
            return (
                f"Phase=PART 1 Q{n} of {PART1_QUESTIONS} — FINAL Part 1 question, still on "
                f"'{topic_display}'.{ack} Ask ONE Cambridge-style personal question on this focus: "
                f"\"{focus}\". Do NOT deliver the cue card yet — the next turn does that "
                f"automatically.{variety_hint}"
            )
        return (
            f"Phase=PART 1 Q{n} of {PART1_QUESTIONS}. STILL on '{topic_display}' — do NOT switch "
            f"topics.{ack} Ask ONE Cambridge-style personal question on this focus: \"{focus}\". "
            f"FORBIDDEN here (these are Part 3): \"Why do people...\", \"How important is...\", "
            f"\"What are the benefits of...\".{variety_hint}"
        )

    if upcoming == "part2":
        p2 = sum(1 for p in phases if p == "part2")
        if p2 == 0:
            card = _pick_part2(sid)
            cue = _build_cue_card(card)
            return (
                "Phase=PART 2 — DO NOT ASK A QUESTION. Part 1 is OVER. Output the cue card below "
                "EXACTLY as written, with NOTHING added before or after. After delivering it, stop "
                "completely (the candidate now has 1 minute to prepare).\n\n"
                "=== CUE CARD START ===\n" + cue + "\n=== CUE CARD END ==="
            )
        return (
            "Phase=PART 2 follow-up. The candidate just finished the long turn. Ask ONE short "
            "rounding-off question on what they said (e.g. 'Did you enjoy it?' / 'Would you do it "
            "again if you had the chance?'). Then stop."
        )

    if upcoming == "part3":
        card = _pick_part2(sid)
        themes = _pick_part3(card, sid)
        n = sum(1 for p in phases if p == "part3") + 1
        # n=1-3 → sub-theme 0 (3 focuses); n=4-5 → sub-theme 1 (2 focuses)
        if n <= 3:
            sub_idx, focus_idx = 0, n - 1
        else:
            sub_idx, focus_idx = 1, n - 4
        sub_theme, sub_focuses = themes[sub_idx % len(themes)]
        sub_focus = sub_focuses[focus_idx % len(sub_focuses)]
        is_new_sub = focus_idx == 0
        if is_new_sub:
            opener_phrase = "Let's go on to discuss" if sub_idx == 0 else "Now let's talk about"
            return (
                f"Phase=PART 3 Q{n} of {PART3_QUESTIONS}. The Part 2 theme is '{card['topic']}'. "
                f"{'NEW ' if sub_idx else ''}Sub-theme: '{sub_theme}'. Open with EXACTLY: "
                f"\"{opener_phrase} {sub_theme.lower()}.\" Then ONE abstract / opinion / society-level "
                f"question on this focus: \"{sub_focus}\". STAY on the Part 2 theme — do NOT "
                f"introduce unrelated subjects.{variety_hint}"
            )
        return (
            f"Phase=PART 3 Q{n} of {PART3_QUESTIONS}. STILL on sub-theme '{sub_theme}' "
            f"(tied to Part 2 theme '{card['topic']}'). You SHOULD briefly react to the "
            f"candidate's previous answer first (echo a key phrase they used, or "
            f"\"That's an interesting view, ...\") then ask ONE abstract / opinion question on "
            f"this focus: \"{sub_focus}\". Or probe them once with 'Why do you think that is?' / "
            f"'Could you give an example?' before pivoting.{variety_hint}"
        )

    # feedback — band-anchored from candidate stats
    stats = _candidate_stats(history)
    if not stats:
        band_hint = (f" Candidate's stated target band: {target_band}.") if target_band else ""
        return (
            "Phase=END. Deliver the Chinese feedback report now using the EXACT template "
            "(## 评分 / F&C x.x | Lex x.x | Gram x.x | Pron x.x | Overall x.x / "
            "## 主要问题 / ## 一句话建议). No more questions." + band_hint
        )
    return _band_anchored_feedback_hint(stats, history, target_band)


def _has_chinese(text: str) -> bool:
    """Detect any CJK Unified Ideographs in the candidate's input."""
    return any("一" <= ch <= "鿿" for ch in (text or ""))


def is_feedback_trigger(text: str) -> bool:
    low = text.lower().strip(" .,!?\"'")
    triggers = {"feedback now", "stop", "exit", "end the test", "end → feedback", "end -> feedback"}
    return low in triggers


@app.get("/")
def index():
    return FileResponse(HERE / "index.html")


# ── Auth (phone-based). Error details are stable keys the client maps to localized text. ──
@app.post("/api/signup")
async def signup(request: Request):
    body = await request.json()
    phone = _normalize_phone(body.get("phone") or "")
    password = body.get("password") or ""
    name = (body.get("name") or "").strip() or None
    if not _PHONE_RE.match(phone):
        raise HTTPException(400, "phone_invalid")
    if len(password) < 6:
        raise HTTPException(400, "password_short")
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    try:
        with _db() as c:
            cur = c.execute(
                "INSERT INTO users (phone, password_hash, name, created_at) VALUES (?, ?, ?, ?) RETURNING id",
                (phone, pw_hash, name, time.time()),
            )
            row = cur.fetchone()
            user_id = row["id"]
    except _db_mod.IntegrityError:
        raise HTTPException(409, "phone_taken")
    request.session["user_id"] = user_id
    return {"id": user_id, "phone": phone, "name": name}


@app.post("/api/login")
async def login(request: Request):
    body = await request.json()
    phone = _normalize_phone(body.get("phone") or "")
    password = body.get("password") or ""
    if not phone:
        raise HTTPException(400, "phone_required")
    with _db() as c:
        row = c.execute(
            "SELECT id, password_hash, name FROM users WHERE phone = ?", (phone,)
        ).fetchone()
    if not row or not bcrypt.checkpw(password.encode(), row["password_hash"].encode()):
        raise HTTPException(401, "invalid_credentials")
    request.session["user_id"] = row["id"]
    return {"id": row["id"], "phone": phone, "name": row["name"]}


@app.post("/api/logout")
def logout(request: Request):
    request.session.clear()
    return {"ok": True}


@app.get("/api/me")
def me(request: Request):
    uid = request.session.get("user_id")
    if not uid:
        raise HTTPException(401, "Not authenticated")
    u = _user_row(uid)
    if not u:
        request.session.clear()
        raise HTTPException(401, "User not found")
    return u


@app.patch("/api/me")
async def update_me(request: Request):
    """Update editable profile fields. Any subset of name/target_band/accent/preferred_topic."""
    uid = _require_user(request)
    body = await request.json()
    allowed = {"name", "target_band", "accent", "preferred_topic"}
    updates = {}
    for k in allowed:
        if k not in body:
            continue
        v = body[k]
        if isinstance(v, str):
            v = v.strip() or None
        updates[k] = v
    # Validate
    if "target_band" in updates and updates["target_band"] not in (None, "5.5", "6.0", "6.5", "7.0", "7.5", "8.0"):
        raise HTTPException(400, "bad_target_band")
    if "accent" in updates and updates["accent"] not in (None, "en-GB", "en-US", "en-AU", "en-IN"):
        raise HTTPException(400, "bad_accent")
    if "preferred_topic" in updates and updates["preferred_topic"] not in (None, *PART1_BANK.keys()):
        raise HTTPException(400, "bad_topic")
    if not updates:
        return _user_row(uid)
    sets = ", ".join(f"{k} = ?" for k in updates)
    with _db() as c:
        c.execute(f"UPDATE users SET {sets} WHERE id = ?", (*updates.values(), uid))
    return _user_row(uid)


def _topic_label(slug: str) -> str:
    """Pretty label for the setup dropdown. 'cam7_keeping_in_contact_with_people'
    → 'Cam 7 — Keeping in contact with people'; 'work_study' → 'Work / Study'."""
    m = re.match(r"^cam(\d+)_(.+)$", slug)
    if m:
        return f"Cam {m.group(1)} — {m.group(2).replace('_', ' ').capitalize()}"
    if slug == "work_study":
        return "Work / Study"
    return slug.replace("_", " ").capitalize()


def _topic_sort_key(slug: str):
    """Curated 15 topics first (alphabetical), then Cambridge variants by book then alphabetic."""
    m = re.match(r"^cam(\d+)_(.+)$", slug)
    if m:
        return (1, int(m.group(1)), m.group(2))
    return (0, 0, slug)


@app.get("/healthz")
def healthz():
    """Health check for Render. Doesn't touch the DB or LLM — must answer fast."""
    return {
        "status": "ok",
        "env": IELTS_ENV,
        "llm_provider": llm_provider.PROVIDER,
        "db": _db_mod.kind(),
    }


@app.get("/api/topics")
def get_topics():
    """Topics the setup screen can offer. Returns both legacy `topics` (slugs only,
    backward compat) and `labelled` (list of {value, label}) so the dropdown shows
    pretty names while POST still sends the slug."""
    keys = sorted(PART1_BANK.keys(), key=_topic_sort_key)
    return {
        "topics": keys,
        "labelled": [{"value": k, "label": _topic_label(k)} for k in keys],
    }


# ── Sessions (scoped per user) ──
@app.post("/api/session")
async def new_session(request: Request):
    """Create a fresh mock-test session.
    Optional body: {target_band, accent, p1_topic}. Missing fields fall back to user prefs."""
    uid = _require_user(request)
    body = {}
    try:
        body = await request.json()
    except Exception:
        body = {}
    target_band = body.get("target_band") or None
    accent = body.get("accent") or None
    p1_topic = body.get("p1_topic") or None
    # Fall back to user prefs for any unset field
    if not (target_band and accent and p1_topic):
        u = _user_row(uid) or {}
        target_band = target_band or u.get("target_band")
        accent      = accent      or u.get("accent")
        p1_topic    = p1_topic    or u.get("preferred_topic")
    # Validate (silently drop invalid values rather than 400 — defaults take over)
    if target_band not in (None, "5.5", "6.0", "6.5", "7.0", "7.5", "8.0"):
        target_band = None
    if accent not in (None, "en-GB", "en-US", "en-AU", "en-IN"):
        accent = None
    if p1_topic not in (None, *PART1_BANK.keys()):
        p1_topic = None
    sid = uuid.uuid4().hex[:12]
    _save_session(sid, [], "intro", "active", None, user_id=uid,
                  target_band=target_band, accent=accent, p1_topic=p1_topic)
    return {
        "id": sid, "phase": "intro", "step": None, "history": [],
        "status": "active", "feedback": None,
        "target_band": target_band, "accent": accent, "p1_topic": p1_topic,
    }


@app.get("/api/session/{sid}")
def get_session(sid: str, request: Request):
    """Resume a session — full transcript, current phase, feedback if any."""
    uid = _require_user(request)
    s = _load_session(sid)
    if not s or not _owns_session(s, uid):
        return JSONResponse({"error": "not found"}, status_code=404)
    phases = derive_phases(s["history"])
    s["phase"] = phases[-1] if phases else "intro"
    s["step"] = phase_step(s["history"])
    return s


BAND_REGEX = re.compile(r"Overall\s*([0-9](?:\.[0-9])?)", re.IGNORECASE)


def _extract_band(feedback):
    """Pull the 'Overall x.x' band out of a feedback report; None if missing."""
    if not feedback:
        return None
    m = BAND_REGEX.search(feedback)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


@app.get("/api/sessions")
def list_sessions(request: Request, limit: int = 50):
    """Past mock-test sessions for the logged-in user, newest first."""
    uid = _require_user(request)
    with _db() as c:
        rows = c.execute(
            "SELECT id, created_at, updated_at, status, phase, history, feedback FROM sessions "
            "WHERE user_id = ? ORDER BY updated_at DESC LIMIT ?",
            (uid, limit),
        ).fetchall()
    out = []
    for r in rows:
        history = json.loads(r["history"])
        examiner_turns = sum(1 for m in history if m.get("role") == "assistant")
        phases = derive_phases(history)
        out.append({
            "id": r["id"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
            "status": r["status"],
            "phase": phases[-1] if phases else "intro",
            "turns": len(history),
            "examiner_turns": examiner_turns,
            "band": _extract_band(r["feedback"]),
        })
    return out


@app.delete("/api/session/{sid}")
def delete_session(sid: str, request: Request):
    """Remove a session — used by the history page's delete button."""
    uid = _require_user(request)
    with _db() as c:
        cur = c.execute("DELETE FROM sessions WHERE id = ? AND user_id = ?", (sid, uid))
        if cur.rowcount == 0:
            return JSONResponse({"error": "not found"}, status_code=404)
    return {"deleted": sid}


@app.post("/api/chat")
async def chat(request: Request):
    """
    Append one candidate turn to a session and stream the examiner's reply.

    Body: { session_id: str, user_message: str }   user_message may be "" on resume.
    Server is authoritative for the transcript — clients only send the new turn.
    """
    uid = _require_user(request)
    body = await request.json()
    sid = body.get("session_id")
    user_text = (body.get("user_message") or "").strip()
    if not sid:
        return JSONResponse({"error": "session_id required"}, status_code=400)
    sess = _load_session(sid)
    if not sess or not _owns_session(sess, uid):
        return JSONResponse({"error": "session not found"}, status_code=404)
    if sess["status"] == "complete":
        return JSONResponse({"error": "session already complete"}, status_code=409)

    history = sess["history"]
    if user_text:
        history.append({"role": "user", "content": user_text})

    last_user = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
    if is_feedback_trigger(last_user):
        hint = "Phase=END. The candidate asked for feedback. Output the Chinese feedback report now."
        label = "feedback"
    elif _has_chinese(last_user):
        # Don't advance the test — re-prompt in English and keep phase as-is.
        label = phase_label(history)
        hint = (
            "LANGUAGE ALERT: the candidate just replied in Chinese during a test phase. "
            "Output exactly: \"Could you answer in English, please?\" — then re-ask your "
            "previous question (or the current phase question) in clear, simple English. "
            "Stay entirely in English. Then stop."
        )
    else:
        hint = phase_hint(history, sid=sid,
                          p1_topic=sess.get("p1_topic"),
                          target_band=sess.get("target_band"))
        label = phase_label(history)

    # Persist the user turn before streaming so a mid-stream failure doesn't lose it.
    _save_session(sid, history, label, "active", None, user_id=uid)

    # For feedback the transcript is already inside the hint — avoid sending it twice.
    if label == "feedback":
        messages = [
            {"role": "system", "content": hint},
            {"role": "user", "content": "Now produce the feedback report in Chinese as instructed."},
        ]
    else:
        messages = history + [{"role": "system", "content": hint}]

    step_initial = phase_step(history)
    # Use the bigger reasoning model for the feedback turn (7B picks scores by vibe).
    # The transcript-grounded prompt is long, so bump the context window too.
    is_feedback_turn = label == "feedback"
    chosen_model = _pick_feedback_model() if is_feedback_turn else MODEL_NAME
    chosen_ctx = 12288 if is_feedback_turn else 8192

    # Groq doesn't have a baked-in system persona like Ollama's Modelfile, so we
    # have to embed it ourselves for non-feedback turns.
    stream_messages = llm_provider.embed_system_prompt(
        messages, kind="feedback" if is_feedback_turn else "examiner"
    )

    def event_stream():
        # First event: tell the client which phase + sub-step + session this stream belongs to.
        yield f"data: {json.dumps({'phase': label, 'step': step_initial, 'session_id': sid})}\n\n"
        full = []
        try:
            for piece, _done in llm_provider.chat_stream(
                stream_messages,
                model=chosen_model,
                num_ctx=chosen_ctx,
                temperature=0.3 if is_feedback_turn else 0.5,
                timeout=600,
            ):
                if not piece:
                    continue
                full.append(piece)
                # For feedback we buffer the whole reply so R1's <think>
                # reasoning never appears on screen — only the cleaned,
                # clamped final report is emitted.
                if not is_feedback_turn:
                    yield f"data: {json.dumps({'chunk': piece})}\n\n"
        except Exception as e:
            if llm_provider.is_connection_error(e):
                yield f"data: {json.dumps({'error': 'llm_down'})}\n\n"
            else:
                yield f"data: {json.dumps({'error': 'examiner_error', 'detail': str(e)[:200]})}\n\n"
            return

        # Persist the examiner reply and mark the session complete on feedback.
        reply_text = "".join(full).strip()
        actual_label = label
        if reply_text:
            if is_feedback_turn:
                # 1) Strip R1's <think>...</think> reasoning blocks
                reply_text = _strip_think_blocks(reply_text)
                # 2) Anti-inflation clamp: force every band into server-computed range
                stats_for_clamp = _candidate_stats(history)
                if stats_for_clamp:
                    reply_text = _clamp_feedback(reply_text, stats_for_clamp)
                # 3) Emit the cleaned, clamped report as ONE chunk (we suppressed
                #    streaming above so the UI only sees the final version).
                yield f"data: {json.dumps({'chunk': reply_text})}\n\n"
            history.append({"role": "assistant", "content": reply_text})
            actual_label = derive_phases(history)[-1]
            if actual_label != label:
                corrected_step = phase_step(history)
                yield f"data: {json.dumps({'phase': actual_label, 'step': corrected_step})}\n\n"
        is_fb = actual_label == "feedback"
        _save_session(
            sid,
            history,
            actual_label,
            "complete" if is_fb else "active",
            reply_text if is_fb else None,
            user_id=uid,
        )
        yield "data: {\"done\": true}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/api/state")
def state(history_json: str = ""):
    """Optional helper: client can ask for current phase label."""
    try:
        history = json.loads(history_json) if history_json else []
    except Exception:
        history = []
    return {"hint": phase_hint(history), "phase": phase_label(history)}


if __name__ == "__main__":
    import uvicorn
    print("Open http://localhost:8000 in Chrome or Edge.")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")
