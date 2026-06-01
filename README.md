# IELTS Speaking Judge

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/English-README-blue?style=for-the-badge" alt="English"></a>
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/%E4%B8%AD%E6%96%87-README-red?style=for-the-badge" alt="中文"></a>
  <a href="README.ar.md"><img src="https://img.shields.io/badge/%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9-README-green?style=for-the-badge" alt="العربية"></a>
</p>

<p align="center">
  <strong>AI-driven IELTS Speaking mock exam — Cambridge-style 3-part test, streaming voice examiner, band-anchored feedback.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/fastapi-0.136-009688.svg" alt="FastAPI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"></a>
  <a href="DEPLOY.md"><img src="https://img.shields.io/badge/deploy-Render%20%2B%20Supabase%20%2B%20Groq-orange.svg" alt="Deploy"></a>
</p>

---

## What it does

**IELTS Speaking Judge** is a full IELTS Speaking simulator that replicates the real exam flow.

It includes:

- **Intro** — the examiner greets you and asks your name
- **Part 1** — 4 personal questions on one familiar topic
- **Part 2** — cue card with a 1-minute preparation timer and a 2-minute long-turn timer
- **Part 3** — 5 abstract / opinion questions connected to the Part 2 theme
- **Feedback** — a band-anchored Chinese report with improved answer rewrites

Speech-to-text and text-to-speech are handled in the browser through the Web Speech API, so no audio data is sent to the backend.

## Features

- 71 Part 1 topics
- 61 Part 2 cue cards
- 61 Part 3 theme sets
- Deterministic question selection per session
- Dual-timer cue card: 60-second preparation and 120-second speaking timer
- Local Ollama or cloud Groq support
- SQLite for local development and Postgres for production

## Quick start

Requires **Python 3.12+**.

```bash
git clone https://github.com/paynetim713/IELTS-Speaking-Judge
cd IELTS-Speaking-Judge

python -m venv .venv
.venv/Scripts/activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### Option A — local LLM via Ollama

```bash
ollama pull qwen2.5:7b
ollama create ielts-examiner -f Modelfile.ielts-examiner
uvicorn webapp:app --port 8000
```

### Option B — hosted LLM via Groq

```bash
export LLM_PROVIDER=groq
export GROQ_API_KEY=gsk_your_key_here
uvicorn webapp:app --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

## Project structure

```text
.
├── webapp.py                    # FastAPI backend
├── llm_provider.py              # Ollama / Groq abstraction
├── db.py                        # SQLite / Postgres abstraction
├── question_bank.py             # IELTS question bank
├── build_bank.py                # Question bank builder
├── extract_speaking.py          # PDF extraction tool
├── cambridge_manual.json        # Manually collected Cambridge questions
├── Modelfile.ielts-examiner     # Ollama model file
├── index.html                   # Frontend page
├── requirements.txt             # Python dependencies
├── render.yaml                  # Render deployment config
└── DEPLOY.md                    # Deployment guide
```

## Configuration

See [`.env.example`](.env.example) for the full list.

| Variable | Purpose |
|---|---|
| `LLM_PROVIDER` | `ollama` or `groq` |
| `OLLAMA_URL` | Ollama server URL |
| `GROQ_API_KEY` | Groq API key |
| `DATABASE_URL` | Database connection URL |
| `IELTS_SECRET_KEY` | Cookie signing key |
| `CORS_ORIGINS` | Allowed frontend origins |

## Acknowledgements

- Cambridge IELTS Books 4–18
- IELTS Liz
- Keith Speaking Academy
- Groq
- Supabase

> This project is an exam preparation aid and is not affiliated with or endorsed by Cambridge University Press, IDP IELTS or the British Council.
