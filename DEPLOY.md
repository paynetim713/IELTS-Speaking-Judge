# Deploy to Render + Supabase + Groq (all free tier)

End state: webapp on Render at `https://voice-ielts.onrender.com`,
talking to Supabase Postgres for users/sessions and Groq for LLM inference.

## Prereqs

- GitHub account (Render reads from a repo)
- Supabase account → free 500 MB Postgres
- Groq account → free 30 req/min, Llama 3.3 70B
- Render account → free 750h/month web service

## 1. Push this folder to GitHub

```bash
cd F:/ollama_models/voice_ielts
git init -b main
git add .
git commit -m "init"
# Create a new GitHub repo, then:
git remote add origin git@github.com:<you>/voice-ielts.git
git push -u origin main
```

Add this to a `.gitignore` (matters because `sessions.db` and `.secret_key`
contain local-only state):

```gitignore
.venv/
__pycache__/
hf_cache/
.pdf_extract/
sessions.db
.secret_key
.env
*.pyc
```

## 2. Provision Supabase Postgres

1. https://supabase.com → New project (free tier)
2. Wait ~2 min for the DB to come up
3. Settings → Database → Connection string → **URI** (pooled, port 6543)
4. Copy the URI — it looks like `postgresql://postgres.xxx:[YOUR-PASSWORD]@aws-0-...supabase.com:6543/postgres`
5. Replace `[YOUR-PASSWORD]` with the password you set
6. Save for step 4

The schema auto-creates on first boot via `_init_db()`.

## 3. Get a Groq API key

1. https://console.groq.com → Sign in (Google login works)
2. API keys → Create API key
3. Copy `gsk_...`, save for step 4
4. Default model `llama-3.3-70b-versatile` is in the free tier (30 req/min)

## 4. Deploy on Render

1. https://dashboard.render.com → New → Blueprint
2. Connect the GitHub repo from step 1
3. Render reads `render.yaml`, creates the service
4. In the service's Environment tab, set the three "sync: false" vars:
   - `IELTS_SECRET_KEY` → run locally: `python -c "import secrets; print(secrets.token_hex(32))"`
   - `GROQ_API_KEY` → from step 3
   - `DATABASE_URL` → from step 2
5. Deploy. First boot takes ~5 min. Health check is `/healthz`.

## 5. Verify

```bash
curl https://voice-ielts.onrender.com/healthz                          # should 200
curl https://voice-ielts.onrender.com/api/topics | head -200           # 71 topics
```

Open the URL in a browser — the setup screen loads, signup creates a user,
starting a session triggers an LLM call to Groq, you see the examiner streaming
the first question.

## 6. Optional: front-end on Cloudflare Pages

Cheaper than serving HTML from Render (which sleeps). Render becomes a pure API.

1. Make a new repo with just `index.html` (or use a sibling `frontend/` folder)
2. Before the existing `<script>` blocks in index.html, add:
   ```html
   <script>window.IELTS_API_BASE = 'https://voice-ielts.onrender.com';</script>
   ```
3. Push to GitHub, connect to Cloudflare Pages, build command `none`, output `.`
4. Add the Pages URL (e.g. `https://voice-ielts.pages.dev`) to Render's
   `CORS_ORIGINS` env var, redeploy. Confirm cookies + SSE chunks still arrive.

## Notes / Gotchas

- **Render free tier sleeps after 15 min idle.** First request after sleep takes
  ~30s cold-start. For an exam-prep app this is noticeable on the very first
  click; subsequent are instant.
- **Supabase free tier pauses inactive projects after 1 week.** Hit the dashboard
  weekly or set up a uptime monitor.
- **Groq free rate limit**: 30 req/min, 14,400 req/day. Each IELTS session is
  ~17 LLM calls (intro + 10 P1 + cue + 5 P3 + feedback). ≈ 850 sessions/day max.
  More than enough for personal practice.
- **Cookie cross-origin**: with the Pages → Render split, `same_site=None; Secure`
  is required. The code sets this automatically when `IELTS_ENV=prod`.
- **STT/TTS run in the browser**, no cost.
