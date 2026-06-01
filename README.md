# IELTS Speaking Judge

<p align="center">
  <strong>Practice IELTS Speaking in your browser with an AI examiner, real test timing, and practical feedback after the session.</strong>
</p>

<p align="center">
  <a href="README.md"><strong>English</strong></a>
  ·
  <a href="README.zh-CN.md"><strong>中文</strong></a>
  ·
  <a href="README.ar.md"><strong>العربية</strong></a>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/fastapi-0.136-009688.svg" alt="FastAPI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"></a>
  <a href="DEPLOY.md"><img src="https://img.shields.io/badge/deploy-Render%20%2B%20Supabase%20%2B%20Groq-orange.svg" alt="Deploy"></a>
</p>

---

## Why this project exists

I built **IELTS Speaking Judge** because most speaking practice tools feel too loose: they either ask random questions, give only a score, or do not follow the pressure of the real IELTS Speaking test.

This project tries to keep the practice closer to the actual exam. The examiner goes through the three parts in order, Part 2 has a real preparation and speaking timer, and the final feedback focuses on what the candidate actually said instead of giving a vague comment like “good job”.

It is mainly designed for IELTS learners who want to practise alone, repeat sessions, and understand how to improve their answers step by step.

## What it does

The app simulates the IELTS Speaking flow:

- **Intro** — the examiner greets the candidate and asks for their name
- **Part 1** — short personal questions on one familiar topic
- **Part 2** — a cue card with 1 minute to prepare and 2 minutes to speak
- **Part 3** — follow-up questions that move into more abstract opinions
- **Feedback** — a band-based report with examples from the candidate's own answers and stronger rewrites

The browser handles speech recognition and speech playback through the Web Speech API. That means the backend does not need to receive or store raw audio.

## Highlights

- 71 Part 1 topics, 61 Part 2 cue cards, and 61 Part 3 theme sets
- Question selection is tied to the session, so the same session can be reviewed later
- Part 2 includes a built-in preparation timer and speaking timer
- Feedback is designed around IELTS band descriptors, not just a random AI score
- Supports **Ollama** for local use and **Groq** for cloud inference
- Uses **SQLite** for local development and **Postgres** for deployment
- Single-file frontend, so the project is easy to run and understand

## Quick start

You need **Python 3.12+**.

```bash
git clone https://github.com/paynetim713/IELTS-Speaking-Judge
cd IELTS-Speaking-Judge

python -m venv .venv
.venv/Scripts/activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### Option A — run with Ollama locally

```bash
ollama pull qwen2.5:7b
ollama create ielts-examiner -f Modelfile.ielts-examiner
uvicorn webapp:app --port 8000
```

### Option B — run with Groq

```bash
export LLM_PROVIDER=groq
export GROQ_API_KEY=gsk_your_key_here
uvicorn webapp:app --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

## Project structure

```text
.
├── webapp.py                    # FastAPI backend: auth, sessions, chat stream
├── llm_provider.py              # Ollama / Groq provider wrapper
├── db.py                        # SQLite / Postgres database wrapper
├── question_bank.py             # IELTS Speaking question bank
├── build_bank.py                # Rebuilds the generated question bank
├── extract_speaking.py          # Extracts speaking questions from PDFs
├── cambridge_manual.json        # Manually collected Cambridge questions
├── Modelfile.ielts-examiner     # Ollama examiner prompt
├── index.html                   # Browser frontend
├── requirements.txt             # Python dependencies
├── render.yaml                  # Render deployment config
└── DEPLOY.md                    # Deployment notes
```

## Configuration

See [`.env.example`](.env.example) for all available options.

| Variable | Purpose |
|---|---|
| `LLM_PROVIDER` | Choose `ollama` or `groq` |
| `OLLAMA_URL` | Ollama server URL |
| `GROQ_API_KEY` | Required when using Groq |
| `DATABASE_URL` | Database connection URL |
| `IELTS_SECRET_KEY` | Cookie signing key |
| `CORS_ORIGINS` | Allowed frontend origins |

## Notes

This is a practice tool, not an official IELTS scoring system. The feedback is meant to help learners notice repeated problems, improve their answers, and practise under a more realistic speaking-test flow.

Browser speech recognition quality can also vary depending on the browser, microphone, accent, and network environment.

## Acknowledgements

- Cambridge IELTS Books 4–18
- IELTS Liz
- Keith Speaking Academy
- Groq
- Supabase

> This project is an IELTS preparation aid and is not affiliated with or endorsed by Cambridge University Press, IDP IELTS, or the British Council.
