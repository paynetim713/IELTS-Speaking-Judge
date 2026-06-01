# IELTS Speaking Judge

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/English-README-blue?style=for-the-badge" alt="English"></a>
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/%E4%B8%AD%E6%96%87-README-red?style=for-the-badge" alt="中文"></a>
  <a href="README.ar.md"><img src="https://img.shields.io/badge/%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9-README-green?style=for-the-badge" alt="العربية"></a>
</p>

<div dir="rtl">

<p align="center">
  <strong>نظام محاكاة لاختبار IELTS Speaking باستخدام الذكاء الاصطناعي، مع ممتحن صوتي مباشر وتقييم مرتبط بمعايير الدرجات.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/fastapi-0.136-009688.svg" alt="FastAPI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"></a>
  <a href="DEPLOY.md"><img src="https://img.shields.io/badge/deploy-Render%20%2B%20Supabase%20%2B%20Groq-orange.svg" alt="Deploy"></a>
</p>

---

## نبذة عن المشروع

**IELTS Speaking Judge** هو نظام يحاكي اختبار المحادثة في IELTS باستخدام الذكاء الاصطناعي.

يشمل النظام:

- **المقدمة**: يحيي الممتحن المتقدم ويسأله عن اسمه
- **الجزء الأول**: 4 أسئلة شخصية حول موضوع مألوف
- **الجزء الثاني**: بطاقة موضوع مع دقيقة واحدة للتحضير ودقيقتين للإجابة
- **الجزء الثالث**: 5 أسئلة رأي مرتبطة بموضوع الجزء الثاني
- **التقييم**: تقرير تقييم باللغة الصينية اعتمادًا على معايير IELTS، مع إعادة صياغة بعض الإجابات إلى مستوى أعلى

يتم التعرف على الصوت وتحويل النص إلى صوت داخل المتصفح، لذلك لا يتم إرسال الصوت إلى الخادم الخلفي.

## المميزات

- 71 موضوعًا للجزء الأول
- 61 بطاقة للجزء الثاني
- 61 مجموعة موضوعات للجزء الثالث
- اختيار ثابت للأسئلة لكل جلسة
- مؤقت مزدوج للجزء الثاني: 60 ثانية للتحضير و120 ثانية للإجابة
- دعم Ollama محليًا أو Groq سحابيًا
- دعم SQLite محليًا وPostgres في الإنتاج

## التشغيل المحلي

يتطلب المشروع **Python 3.12+**.

</div>

```bash
git clone https://github.com/paynetim713/IELTS-Speaking-Judge
cd IELTS-Speaking-Judge

python -m venv .venv
.venv/Scripts/activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

<div dir="rtl">

### الخيار A: استخدام Ollama محليًا

</div>

```bash
ollama pull qwen2.5:7b
ollama create ielts-examiner -f Modelfile.ielts-examiner
uvicorn webapp:app --port 8000
```

<div dir="rtl">

### الخيار B: استخدام Groq سحابيًا

</div>

```bash
export LLM_PROVIDER=groq
export GROQ_API_KEY=gsk_your_key_here
uvicorn webapp:app --port 8000
```

<div dir="rtl">

ثم افتح:

</div>

```text
http://127.0.0.1:8000
```

<div dir="rtl">

## هيكل المشروع

</div>

```text
.
├── webapp.py                    # FastAPI backend
├── llm_provider.py              # Ollama / Groq abstraction
├── db.py                        # SQLite / Postgres abstraction
├── question_bank.py             # IELTS question bank
├── build_bank.py                # Question bank builder
├── extract_speaking.py          # PDF extraction tool
├── cambridge_manual.json        # Manually collected questions
├── Modelfile.ielts-examiner     # Ollama model file
├── index.html                   # Frontend page
├── requirements.txt             # Python dependencies
├── render.yaml                  # Render deployment config
└── DEPLOY.md                    # Deployment guide
```

<div dir="rtl">

## متغيرات البيئة

راجع [`.env.example`](.env.example) للحصول على القائمة الكاملة.

| المتغير | الوصف |
|---|---|
| `LLM_PROVIDER` | `ollama` أو `groq` |
| `OLLAMA_URL` | عنوان خدمة Ollama |
| `GROQ_API_KEY` | مفتاح Groq API |
| `DATABASE_URL` | رابط قاعدة البيانات |
| `IELTS_SECRET_KEY` | مفتاح توقيع Cookie |
| `CORS_ORIGINS` | مصادر الواجهة الأمامية المسموح بها |

## شكر وتقدير

- Cambridge IELTS Books 4–18
- IELTS Liz
- Keith Speaking Academy
- Groq
- Supabase

> هذا المشروع مخصص للتدريب على اختبار IELTS فقط، وليس تابعًا رسميًا لـ Cambridge University Press أو IDP IELTS أو British Council.

</div>
