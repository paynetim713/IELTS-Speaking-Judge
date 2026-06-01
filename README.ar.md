# IELTS Speaking Judge

<p align="center">
  <strong>تدرّب على IELTS Speaking من المتصفح مع ممتحن ذكاء اصطناعي، توقيت قريب من الاختبار الحقيقي، وتغذية راجعة عملية بعد الجلسة.</strong>
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

<div dir="rtl">

## لماذا تم بناء هذا المشروع

تم بناء **IELTS Speaking Judge** لأن كثيرًا من أدوات تدريب المحادثة تبدو ذكية، لكنها لا تشبه اختبار IELTS Speaking الحقيقي.

بعض الأدوات تطرح أسئلة عشوائية فقط، وبعضها يعطي درجة بدون شرح واضح، وبعضها لا يحاكي ضغط الجزء الثاني، حيث يحتاج المتقدم إلى التحضير خلال دقيقة واحدة ثم التحدث لمدة دقيقتين. لذلك يحاول هذا المشروع جعل التدريب أقرب إلى تجربة الاختبار الفعلية، وليس مجرد محادثة عادية مع روبوت.

المشروع مناسب للمتعلمين الذين يريدون التدريب بمفردهم، إعادة الجلسات، وفهم كيف يمكن تحسين إجاباتهم خطوة بخطوة.

## ماذا يفعل المشروع

يحاكي التطبيق تدفق IELTS Speaking الكامل:

- **المقدمة**: يحيي الممتحن المتقدم ويسأله عن اسمه
- **الجزء الأول**: أسئلة قصيرة وشخصية حول موضوع مألوف
- **الجزء الثاني**: بطاقة موضوع مع دقيقة واحدة للتحضير ودقيقتين للتحدث
- **الجزء الثالث**: أسئلة متابعة أكثر تجريدًا مرتبطة بموضوع الجزء الثاني
- **التقييم**: تقرير مبني على مستوى IELTS، مع أمثلة من إجابات المتقدم وإعادة صياغة أقوى لبعض الجمل

يتم التعرف على الصوت وتشغيل الكلام داخل المتصفح باستخدام Web Speech API، لذلك لا يحتاج الخادم الخلفي إلى استقبال أو تخزين الصوت الخام.

## أبرز المميزات

- 71 موضوعًا للجزء الأول، 61 بطاقة للجزء الثاني، و61 مجموعة موضوعات للجزء الثالث
- اختيار الأسئلة مرتبط بالجلسة، مما يجعل مراجعة الجلسة لاحقًا أسهل
- مؤقت مدمج للجزء الثاني: وقت للتحضير ووقت للتحدث
- التغذية الراجعة مبنية على IELTS band descriptors، وليست مجرد درجة عشوائية من الذكاء الاصطناعي
- دعم **Ollama** للتشغيل المحلي ودعم **Groq** للتشغيل السحابي
- استخدام **SQLite** للتطوير المحلي و **Postgres** عند النشر
- واجهة أمامية في ملف واحد، لذلك من السهل تشغيل المشروع وفهم بنيته

## التشغيل المحلي

تحتاج إلى **Python 3.12+**.

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

### الخيار A: التشغيل محليًا باستخدام Ollama

</div>

```bash
ollama pull qwen2.5:7b
ollama create ielts-examiner -f Modelfile.ielts-examiner
uvicorn webapp:app --port 8000
```

<div dir="rtl">

### الخيار B: التشغيل باستخدام Groq

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

<div dir="rtl">

## الإعدادات

راجع [`.env.example`](.env.example) لمعرفة جميع الخيارات المتاحة.

| المتغير | الغرض |
|---|---|
| `LLM_PROVIDER` | اختيار `ollama` أو `groq` |
| `OLLAMA_URL` | رابط خادم Ollama |
| `GROQ_API_KEY` | مطلوب عند استخدام Groq |
| `DATABASE_URL` | رابط الاتصال بقاعدة البيانات |
| `IELTS_SECRET_KEY` | مفتاح توقيع Cookie |
| `CORS_ORIGINS` | مصادر الواجهة الأمامية المسموح بها |

## ملاحظات

هذا المشروع أداة تدريبية، وليس نظام تقييم رسمي لاختبار IELTS. الهدف منه هو مساعدة المتعلم على ملاحظة الأخطاء المتكررة، تحسين الإجابات، والتدرب داخل تدفق أقرب للاختبار الحقيقي.

قد تختلف جودة التعرف على الصوت حسب المتصفح، الميكروفون، اللهجة، وبيئة الشبكة.

## شكر وتقدير

- Cambridge IELTS Books 4–18
- IELTS Liz
- Keith Speaking Academy
- Groq
- Supabase

> هذا المشروع مخصص للمساعدة في التحضير لاختبار IELTS، وليس تابعًا رسميًا لـ Cambridge University Press أو IDP IELTS أو British Council.

</div>
