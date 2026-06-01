# IELTS Speaking Judge

> AI-driven IELTS Speaking mock exam — Cambridge-style 3-part test, streaming voice examiner, band-anchored feedback.
> 雅思口语 AI 模考 — 完整三段式考试,71 个剑桥真题主题,流式语音考官,基于 band descriptors 的反馈。

[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-0.136-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Deploy](https://img.shields.io/badge/deploy-Render%20%2B%20Supabase%20%2B%20Groq-orange.svg)](DEPLOY.md)

---

## What it does

A full IELTS Speaking simulator that replicates the real exam flow:

- **Intro** — examiner greets you and asks your name
- **Part 1** — 4 personal questions on a single familiar topic
- **Part 2** — cue card with a 1-minute prep timer + 2-minute long-turn timer
- **Part 3** — 5 abstract / opinion questions tied to the Part 2 theme (2 sub-themes, 3 + 2 Q)
- **Feedback** — band-anchored Chinese report (F&C / Lex / Gram / Pron / Overall) with **verbatim candidate quotes** rewritten one band higher

The examiner runs on a 70B Llama model (Groq, free tier) or any local Ollama model. STT / TTS happens in the browser via the Web Speech API — no audio data hits the backend.

## Features

- **71 Part 1 topics**, **61 Part 2 cue cards**, **61 Part 3 theme sets** — verbatim Cambridge IELTS 4–18
- **Deterministic question selection per session** — same session ID always gets the same topic, so a candidate's history is reproducible
- **Per-candidate stats** — vocab diversity (TTR), discourse-marker count, avg sentence length feed band thresholds
- **Anti-inflation clamp** — model band scores rounded toward server-computed range; can't flatter the candidate
- **Dual-timer cue card** — 60 s prep then 120 s long-turn with traffic-light UI (yellow @ 30, red @ 10)
- **Pluggable LLM** — `LLM_PROVIDER=ollama` (local) or `groq` (cloud)
- **Pluggable DB** — sqlite local file, Postgres in prod, same SQL
- **Mandarin UI** with English / 中文 toggle

## Quick start — local

Requires **Python 3.12+** and (optionally) **Ollama** for offline LLM.

```bash
git clone https://github.com/paynetim713/IELTS-Speaking-Judge
cd IELTS-Speaking-Judge

python -m venv .venv
.venv/Scripts/activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

# Option A — local LLM via Ollama (recommended for offline use)
ollama pull qwen2.5:7b
ollama create ielts-examiner -f Modelfile.ielts-examiner

# Option B — hosted LLM via Groq (no GPU needed)
export LLM_PROVIDER=groq
export GROQ_API_KEY=gsk_your_key_here

uvicorn webapp:app --port 8000
# open http://127.0.0.1:8000
```

## Deploy to cloud (free)

See **[DEPLOY.md](DEPLOY.md)** for the full Render + Supabase + Groq walkthrough. End-to-end setup is under 15 minutes and stays within all three free tiers:

| Component | Service | Free tier limit |
|---|---|---|
| Backend | Render | 750 h/month |
| Database | Supabase Postgres | 500 MB |
| LLM | Groq (Llama 3.3 70B) | 30 req/min, 14 400 req/day |

## Architecture

```
┌──────────────┐       ┌─────────────────────┐       ┌──────────────────┐
│   Browser    │       │      FastAPI        │       │   LLM provider   │
│              │       │                     │       │                  │
│ Web Speech   │ ◄───► │  /api/chat (SSE)    │ ◄───► │ Ollama or Groq   │
│ (STT / TTS)  │       │                     │       │ (chat streaming) │
│              │       │  /api/topics        │       └──────────────────┘
│  index.html  │       │  /api/session       │
└──────────────┘       │  /api/me  /signup   │       ┌──────────────────┐
                       │                     │ ◄───► │  Persistence     │
                       │  question_bank.py   │       │  sqlite / Postgres
                       └─────────────────────┘       └──────────────────┘
```

The browser handles all audio, so the backend stays cheap-and-stateless.
The server is the source of truth for *which* topic / cue card / Part 3 sub-themes are in play; the LLM is just the voice that delivers them. This prevents the 7B model from "drifting" mid-test.

## Question bank

71 Part 1 topics + 61 cue cards + 61 Part 3 theme sets, sourced from:

- **15 curated topics** — deep-research over Cambridge 18/19/20, IELTS Liz, Keith Speaking Academy
- **PDF text-extraction** (`extract_speaking.py`) — verbatim from Cambridge IELTS 4-7, 8, 10-13, 17 (text-PDF books)
- **Manual transcription** (`cambridge_manual.json`) — user-typed Cam 9 / 14 / 15 / 16 / 18 (image-only scanned PDFs)

To add more material, edit `cambridge_manual.json` then run:

```bash
python build_bank.py     # regenerates question_bank.py
```

The bank is a separate Python module so it doesn't bloat `webapp.py` (1500+ lines of bank vs 1100 lines of business logic).

## Configuration

All via env vars. See [`.env.example`](.env.example) for the full list.

| Var | Default | Purpose |
|---|---|---|
| `IELTS_ENV` | `dev` | `prod` → strict secret handling + secure cookies |
| `LLM_PROVIDER` | `ollama` | `ollama` (local) or `groq` (cloud) |
| `OLLAMA_URL` | `http://localhost:11434` | Where Ollama listens |
| `GROQ_API_KEY` | — | Required when `LLM_PROVIDER=groq` |
| `LLM_EXAMINER_MODEL` | depends | Override the examiner model |
| `LLM_FEEDBACK_MODEL` | depends | Override the feedback model |
| `DATABASE_URL` | sqlite | Set to Postgres URL for cloud DB |
| `IELTS_SECRET_KEY` | random | Cookie signing key; **required in prod** |
| `CORS_ORIGINS` | localhost | Comma-list of allowed frontend origins |

## Project structure

```
.
├── webapp.py                    # FastAPI app — auth, sessions, /api/chat SSE
├── llm_provider.py              # Ollama ↔ Groq abstraction
├── db.py                        # sqlite ↔ Postgres abstraction
├── question_bank.py             # 71 P1 / 61 P2 / 61 P3 (generated)
├── build_bank.py                # merges extractions + manual data → bank
├── extract_speaking.py          # PDF text-extraction tool
├── cambridge_manual.json        # user-transcribed Cam 9/14/15/16/18
├── Modelfile.ielts-examiner     # Ollama Modelfile (system prompt baked in)
├── index.html                   # single-file frontend (vanilla JS)
├── voice_ielts.py               # legacy CLI version (mic + speaker, dev only)
├── requirements.txt             # Python deps
├── render.yaml                  # Render Blueprint
├── runtime.txt                  # Python version pin
└── DEPLOY.md                    # cloud deployment walkthrough
```

## Acknowledgements

- Cambridge IELTS Books 4–18 — source of all verbatim questions
- [IELTS Liz](https://ieltsliz.com) and [Keith Speaking Academy](https://keithspeakingacademy.com) — Part 1 phrasing reference
- Groq — fastest free LLM inference around
- Supabase — Postgres made painless

## License

[MIT](LICENSE) — do whatever you want; no warranty.

> This project is an exam preparation aid and is in no way affiliated with or endorsed by Cambridge University Press or IDP IELTS.
