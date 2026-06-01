# IELTS Speaking Judge

<p align="center">
  <strong>AI-driven IELTS Speaking mock exam with streaming voice examiner and band-anchored feedback.</strong>
</p>

<p align="center">
  <a href="#english">English</a> •
  <a href="#chinese">中文</a> •
  <a href="#arabic">العربية</a>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/fastapi-0.136-009688.svg" alt="FastAPI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"></a>
  <a href="DEPLOY.md"><img src="https://img.shields.io/badge/deploy-Render%20%2B%20Supabase%20%2B%20Groq-orange.svg" alt="Deploy"></a>
</p>

---

## <a id="english"></a>English

### What it does

**IELTS Speaking Judge** is a full IELTS Speaking simulator that replicates the real exam flow:

- **Intro** — the examiner greets you and asks your name
- **Part 1** — 4 personal questions on one familiar topic
- **Part 2** — cue card with a 1-minute preparation timer and a 2-minute long-turn timer
- **Part 3** — 5 abstract / opinion questions connected to the Part 2 theme
- **Feedback** — a band-anchored Chinese report covering F&C, Lexical Resource, Grammar, Pronunciation and Overall Band, with candidate quotes rewritten one band higher

The examiner runs on a 70B Llama model through **Groq** free tier, or any local **Ollama** model. Speech-to-text and text-to-speech are handled in the browser through the Web Speech API, so no audio data is sent to the backend.

### Features

- **71 Part 1 topics**, **61 Part 2 cue cards**, and **61 Part 3 theme sets** from Cambridge IELTS 4–18
- **Deterministic question selection per session** — the same session ID always gets the same topic
- **Per-candidate statistics** — vocabulary diversity, discourse-marker count and average sentence length help estimate band range
- **Anti-inflation clamp** — model band scores are rounded toward the server-computed range
- **Dual-timer cue card** — 60-second preparation timer and 120-second speaking timer with traffic-light UI
- **Pluggable LLM** — use `LLM_PROVIDER=ollama` for local inference or `groq` for cloud inference
- **Pluggable database** — SQLite for local development and Postgres for production
- **Multilingual README** — English, Chinese and Arabic sections in one document

### Quick start — local

Requires **Python 3.12+** and optionally **Ollama** for offline LLM usage.

```bash
git clone https://github.com/paynetim713/IELTS-Speaking-Judge
cd IELTS-Speaking-Judge

python -m venv .venv
.venv/Scripts/activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

# Option A — local LLM via Ollama
ollama pull qwen2.5:7b
ollama create ielts-examiner -f Modelfile.ielts-examiner

# Option B — hosted LLM via Groq
export LLM_PROVIDER=groq
export GROQ_API_KEY=gsk_your_key_here

uvicorn webapp:app --port 8000
# open http://127.0.0.1:8000
```

### Architecture

```text
┌──────────────┐       ┌─────────────────────┐       ┌──────────────────┐
│   Browser    │       │      FastAPI        │       │   LLM provider   │
│              │       │                     │       │                  │
│ Web Speech   │ ◄───► │  /api/chat (SSE)    │ ◄───► │ Ollama or Groq   │
│ (STT / TTS)  │       │                     │       │ (chat streaming) │
│              │       │  /api/topics        │       └──────────────────┘
│  index.html  │       │  /api/session       │
└──────────────┘       │  /api/me  /signup   │       ┌──────────────────┐
                       │                     │ ◄───► │  Persistence     │
                       │  question_bank.py   │       │ sqlite / Postgres│
                       └─────────────────────┘       └──────────────────┘
```

The browser handles all audio, so the backend stays cheap and mostly stateless. The server is the source of truth for topics, cue cards and Part 3 sub-themes, while the LLM only acts as the examiner voice.

### Question bank

The question bank contains 71 Part 1 topics, 61 Part 2 cue cards and 61 Part 3 theme sets, sourced from:

- **15 curated topics** — researched from Cambridge 18/19/20, IELTS Liz and Keith Speaking Academy
- **PDF text extraction** — generated through `extract_speaking.py`
- **Manual transcription** — stored in `cambridge_manual.json`

To add more material, edit `cambridge_manual.json`, then run:

```bash
python build_bank.py
```

### Configuration

All configuration is managed through environment variables. See [`.env.example`](.env.example) for the full list.

| Variable | Default | Purpose |
|---|---|---|
| `IELTS_ENV` | `dev` | `prod` enables strict secret handling and secure cookies |
| `LLM_PROVIDER` | `ollama` | `ollama` for local inference or `groq` for cloud inference |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server address |
| `GROQ_API_KEY` | — | Required when `LLM_PROVIDER=groq` |
| `LLM_EXAMINER_MODEL` | depends | Override examiner model |
| `LLM_FEEDBACK_MODEL` | depends | Override feedback model |
| `DATABASE_URL` | SQLite | Set to Postgres URL for cloud database |
| `IELTS_SECRET_KEY` | random | Cookie signing key, required in production |
| `CORS_ORIGINS` | localhost | Comma-separated list of allowed frontend origins |

### Project structure

```text
.
├── webapp.py                    # FastAPI app — auth, sessions, /api/chat SSE
├── llm_provider.py              # Ollama ↔ Groq abstraction
├── db.py                        # SQLite ↔ Postgres abstraction
├── question_bank.py             # Generated IELTS question bank
├── build_bank.py                # Merges extraction + manual data into bank
├── extract_speaking.py          # PDF text-extraction tool
├── cambridge_manual.json        # Manually transcribed Cambridge questions
├── Modelfile.ielts-examiner     # Ollama Modelfile
├── index.html                   # Single-file frontend
├── voice_ielts.py               # Legacy CLI version
├── requirements.txt             # Python dependencies
├── render.yaml                  # Render Blueprint
├── runtime.txt                  # Python version pin
└── DEPLOY.md                    # Cloud deployment guide
```

### Acknowledgements

- Cambridge IELTS Books 4–18 — source of practice questions
- IELTS Liz and Keith Speaking Academy — Part 1 phrasing reference
- Groq — fast LLM inference
- Supabase — hosted Postgres database

> This project is an exam preparation aid and is not affiliated with or endorsed by Cambridge University Press, IDP IELTS or the British Council.

[Back to top](#ielts-speaking-judge)

---

## <a id="chinese"></a>中文

### 项目介绍

**IELTS Speaking Judge** 是一个 AI 雅思口语模考系统，可以模拟真实 IELTS Speaking 的考试流程：

- **Intro 开场** — 考官问候并询问考生姓名
- **Part 1** — 围绕一个熟悉话题提问 4 个个人问题
- **Part 2** — Cue Card 题卡，包含 1 分钟准备时间和 2 分钟作答时间
- **Part 3** — 围绕 Part 2 主题延伸出 5 个抽象类 / 观点类问题
- **Feedback 反馈** — 根据 IELTS band descriptors 生成中文评分报告，包括 F&C、词汇、语法、发音和总分，并把考生原句改写到更高一个分段的表达

考官可以使用 **Groq** 免费层的 70B Llama 模型，也可以接入本地 **Ollama** 模型。语音识别和语音朗读都由浏览器的 Web Speech API 完成，因此音频不会上传到后端。

### 功能特点

- **71 个 Part 1 话题**、**61 个 Part 2 Cue Cards**、**61 组 Part 3 主题**，来自 Cambridge IELTS 4–18
- **固定会话抽题** — 相同 session ID 会得到相同题目，方便复盘和追踪
- **考生数据统计** — 统计词汇多样性、连接词数量和平均句长，用于辅助判断分数范围
- **防虚高评分机制** — 模型分数会向服务器计算出的合理区间靠拢，避免过度夸分
- **Part 2 双计时器** — 60 秒准备 + 120 秒作答，并带有黄灯 / 红灯提示
- **可切换 LLM** — `LLM_PROVIDER=ollama` 使用本地模型，`groq` 使用云端模型
- **可切换数据库** — 本地使用 SQLite，生产环境可使用 Postgres
- **三语言 README** — English、中文、العربية 集成在同一份文档中

### 本地快速启动

需要 **Python 3.12+**。如果想离线运行模型，可以额外安装 **Ollama**。

```bash
git clone https://github.com/paynetim713/IELTS-Speaking-Judge
cd IELTS-Speaking-Judge

python -m venv .venv
.venv/Scripts/activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

# 方案 A：使用 Ollama 本地模型
ollama pull qwen2.5:7b
ollama create ielts-examiner -f Modelfile.ielts-examiner

# 方案 B：使用 Groq 云端模型
export LLM_PROVIDER=groq
export GROQ_API_KEY=gsk_your_key_here

uvicorn webapp:app --port 8000
# 打开 http://127.0.0.1:8000
```

### 系统架构

```text
┌──────────────┐       ┌─────────────────────┐       ┌──────────────────┐
│   Browser    │       │      FastAPI        │       │   LLM provider   │
│              │       │                     │       │                  │
│ Web Speech   │ ◄───► │  /api/chat (SSE)    │ ◄───► │ Ollama or Groq   │
│ (STT / TTS)  │       │                     │       │ (chat streaming) │
│              │       │  /api/topics        │       └──────────────────┘
│  index.html  │       │  /api/session       │
└──────────────┘       │  /api/me  /signup   │       ┌──────────────────┐
                       │                     │ ◄───► │  Persistence     │
                       │  question_bank.py   │       │ sqlite / Postgres│
                       └─────────────────────┘       └──────────────────┘
```

浏览器负责所有语音相关功能，因此后端可以保持轻量。服务器负责控制当前 session 使用哪些题目、Cue Card 和 Part 3 主题，LLM 只负责扮演考官并进行对话。

### 题库来源

题库包含 71 个 Part 1 话题、61 个 Part 2 Cue Cards 和 61 组 Part 3 主题，来源包括：

- **15 个整理话题** — 参考 Cambridge 18/19/20、IELTS Liz 和 Keith Speaking Academy
- **PDF 文本提取** — 通过 `extract_speaking.py` 自动提取
- **人工转录内容** — 保存在 `cambridge_manual.json`

如果需要添加更多题目，可以修改 `cambridge_manual.json`，然后运行：

```bash
python build_bank.py
```

### 配置说明

所有配置都通过环境变量管理。完整列表可以查看 [`.env.example`](.env.example)。

| 变量名 | 默认值 | 用途 |
|---|---|---|
| `IELTS_ENV` | `dev` | 设置为 `prod` 后启用更严格的密钥和 Cookie 安全策略 |
| `LLM_PROVIDER` | `ollama` | `ollama` 表示本地模型，`groq` 表示云端模型 |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama 服务地址 |
| `GROQ_API_KEY` | — | 使用 Groq 时必须填写 |
| `LLM_EXAMINER_MODEL` | depends | 指定考官模型 |
| `LLM_FEEDBACK_MODEL` | depends | 指定反馈模型 |
| `DATABASE_URL` | SQLite | 云端部署时可设置为 Postgres 地址 |
| `IELTS_SECRET_KEY` | random | Cookie 签名密钥，生产环境必须设置 |
| `CORS_ORIGINS` | localhost | 前端允许访问的来源列表，用逗号分隔 |

### 项目结构

```text
.
├── webapp.py                    # FastAPI 应用：认证、session、/api/chat SSE
├── llm_provider.py              # Ollama ↔ Groq 抽象层
├── db.py                        # SQLite ↔ Postgres 数据库抽象层
├── question_bank.py             # 生成后的雅思口语题库
├── build_bank.py                # 合并提取内容和人工内容，生成题库
├── extract_speaking.py          # PDF 文本提取工具
├── cambridge_manual.json        # 人工转录的 Cambridge 题目
├── Modelfile.ielts-examiner     # Ollama 模型配置文件
├── index.html                   # 单文件前端页面
├── voice_ielts.py               # 旧版 CLI 语音版本
├── requirements.txt             # Python 依赖
├── render.yaml                  # Render 部署配置
├── runtime.txt                  # Python 版本锁定
└── DEPLOY.md                    # 云端部署说明
```

### 致谢

- Cambridge IELTS Books 4–18 — 练习题来源
- IELTS Liz 和 Keith Speaking Academy — Part 1 问法参考
- Groq — 快速 LLM 推理服务
- Supabase — 托管 Postgres 数据库

> 本项目仅用于 IELTS 备考练习，与 Cambridge University Press、IDP IELTS 或 British Council 无官方关联，也未获得其背书。

[返回顶部](#ielts-speaking-judge)

---

## <a id="arabic"></a>العربية

### نبذة عن المشروع

**IELTS Speaking Judge** هو نظام محاكاة لاختبار المحادثة في IELTS باستخدام الذكاء الاصطناعي. يحاكي النظام تدفق الاختبار الحقيقي:

- **المقدمة** — يحيي الممتحن المتقدم ويسأله عن اسمه
- **الجزء الأول** — 4 أسئلة شخصية حول موضوع مألوف واحد
- **الجزء الثاني** — بطاقة موضوع مع دقيقة واحدة للتحضير ودقيقتين للإجابة الطويلة
- **الجزء الثالث** — 5 أسئلة مجردة أو قائمة على الرأي مرتبطة بموضوع الجزء الثاني
- **التقييم** — تقرير صيني مبني على معايير درجات IELTS، ويغطي الطلاقة والترابط، المفردات، القواعد، النطق والدرجة الكلية، مع إعادة صياغة بعض إجابات المتقدم إلى مستوى أعلى

يعمل الممتحن باستخدام نموذج Llama بحجم 70B عبر الطبقة المجانية من **Groq**، أو باستخدام أي نموذج محلي عبر **Ollama**. يتم التعرف على الصوت وتحويل النص إلى صوت داخل المتصفح باستخدام Web Speech API، لذلك لا يتم إرسال بيانات الصوت إلى الخادم الخلفي.

### المميزات

- **71 موضوعًا للجزء الأول**، **61 بطاقة للجزء الثاني**، و **61 مجموعة موضوعات للجزء الثالث** من Cambridge IELTS 4–18
- **اختيار ثابت للأسئلة لكل جلسة** — نفس session ID يحصل دائمًا على نفس الموضوع
- **إحصاءات لكل متقدم** — تنوع المفردات، عدد أدوات الربط ومتوسط طول الجملة تساعد في تقدير نطاق الدرجة
- **آلية لتقليل تضخيم الدرجة** — يتم تقريب درجات النموذج نحو النطاق المحسوب من الخادم
- **مؤقت مزدوج للجزء الثاني** — 60 ثانية للتحضير و120 ثانية للتحدث مع واجهة تنبيه بالألوان
- **دعم أكثر من مزود LLM** — استخدم `LLM_PROVIDER=ollama` للتشغيل المحلي أو `groq` للتشغيل السحابي
- **دعم أكثر من قاعدة بيانات** — SQLite للتطوير المحلي وPostgres للإنتاج
- **README متعدد اللغات** — English، 中文، العربية داخل ملف واحد

### التشغيل المحلي السريع

يتطلب المشروع **Python 3.12+**، ويمكن استخدام **Ollama** اختياريًا لتشغيل النموذج محليًا دون اتصال سحابي.

```bash
git clone https://github.com/paynetim713/IELTS-Speaking-Judge
cd IELTS-Speaking-Judge

python -m venv .venv
.venv/Scripts/activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt

# الخيار A — نموذج محلي عبر Ollama
ollama pull qwen2.5:7b
ollama create ielts-examiner -f Modelfile.ielts-examiner

# الخيار B — نموذج سحابي عبر Groq
export LLM_PROVIDER=groq
export GROQ_API_KEY=gsk_your_key_here

uvicorn webapp:app --port 8000
# افتح http://127.0.0.1:8000
```

### البنية المعمارية

```text
┌──────────────┐       ┌─────────────────────┐       ┌──────────────────┐
│   Browser    │       │      FastAPI        │       │   LLM provider   │
│              │       │                     │       │                  │
│ Web Speech   │ ◄───► │  /api/chat (SSE)    │ ◄───► │ Ollama or Groq   │
│ (STT / TTS)  │       │                     │       │ (chat streaming) │
│              │       │  /api/topics        │       └──────────────────┘
│  index.html  │       │  /api/session       │
└──────────────┘       │  /api/me  /signup   │       ┌──────────────────┐
                       │                     │ ◄───► │  Persistence     │
                       │  question_bank.py   │       │ sqlite / Postgres│
                       └─────────────────────┘       └──────────────────┘
```

يتعامل المتصفح مع جميع وظائف الصوت، لذلك يبقى الخادم الخلفي خفيفًا. الخادم هو مصدر الحقيقة للموضوعات وبطاقات الجزء الثاني وموضوعات الجزء الثالث، بينما يعمل نموذج اللغة كممتحن يتحدث مع المتقدم.

### بنك الأسئلة

يحتوي بنك الأسئلة على 71 موضوعًا للجزء الأول، و61 بطاقة للجزء الثاني، و61 مجموعة موضوعات للجزء الثالث. المصادر تشمل:

- **15 موضوعًا منسقًا** — بالاعتماد على Cambridge 18/19/20 و IELTS Liz و Keith Speaking Academy
- **استخراج النصوص من PDF** — عبر `extract_speaking.py`
- **تفريغ يدوي للأسئلة** — محفوظ في `cambridge_manual.json`

لإضافة مواد جديدة، عدّل ملف `cambridge_manual.json` ثم شغّل:

```bash
python build_bank.py
```

### الإعدادات

تتم إدارة جميع الإعدادات من خلال متغيرات البيئة. راجع [`.env.example`](.env.example) للحصول على القائمة الكاملة.

| المتغير | القيمة الافتراضية | الغرض |
|---|---|---|
| `IELTS_ENV` | `dev` | عند استخدام `prod` يتم تفعيل إعدادات أمان أكثر صرامة |
| `LLM_PROVIDER` | `ollama` | `ollama` للتشغيل المحلي أو `groq` للتشغيل السحابي |
| `OLLAMA_URL` | `http://localhost:11434` | عنوان خادم Ollama |
| `GROQ_API_KEY` | — | مطلوب عند استخدام Groq |
| `LLM_EXAMINER_MODEL` | depends | تحديد نموذج الممتحن |
| `LLM_FEEDBACK_MODEL` | depends | تحديد نموذج التقييم |
| `DATABASE_URL` | SQLite | يمكن ضبطه إلى رابط Postgres عند النشر السحابي |
| `IELTS_SECRET_KEY` | random | مفتاح توقيع Cookie، مطلوب في الإنتاج |
| `CORS_ORIGINS` | localhost | قائمة مصادر الواجهة الأمامية المسموح بها، مفصولة بفواصل |

### هيكل المشروع

```text
.
├── webapp.py                    # تطبيق FastAPI: auth, sessions, /api/chat SSE
├── llm_provider.py              # طبقة تجريد بين Ollama و Groq
├── db.py                        # طبقة تجريد بين SQLite و Postgres
├── question_bank.py             # بنك الأسئلة المولّد
├── build_bank.py                # دمج البيانات المستخرجة واليدوية
├── extract_speaking.py          # أداة استخراج النصوص من PDF
├── cambridge_manual.json        # أسئلة Cambridge المفرغة يدويًا
├── Modelfile.ielts-examiner     # ملف إعداد نموذج Ollama
├── index.html                   # واجهة أمامية في ملف واحد
├── voice_ielts.py               # نسخة CLI قديمة
├── requirements.txt             # اعتماديات Python
├── render.yaml                  # إعداد Render Blueprint
├── runtime.txt                  # تثبيت إصدار Python
└── DEPLOY.md                    # دليل النشر السحابي
```

### شكر وتقدير

- Cambridge IELTS Books 4–18 — مصدر أسئلة التدريب
- IELTS Liz و Keith Speaking Academy — مرجع لصياغة أسئلة الجزء الأول
- Groq — خدمة استدلال سريعة لنماذج اللغة
- Supabase — قاعدة بيانات Postgres مستضافة

> هذا المشروع مخصص للمساعدة في التحضير للاختبار فقط، وليس تابعًا رسميًا لـ Cambridge University Press أو IDP IELTS أو British Council، ولا يمثل اعتمادًا منهم.

[العودة إلى الأعلى](#ielts-speaking-judge)
