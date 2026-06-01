# IELTS Speaking Judge

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/English-README-blue?style=for-the-badge" alt="English"></a>
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/%E4%B8%AD%E6%96%87-README-red?style=for-the-badge" alt="中文"></a>
  <a href="README.ar.md"><img src="https://img.shields.io/badge/%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9-README-green?style=for-the-badge" alt="العربية"></a>
</p>

<p align="center">
  <strong>AI 雅思口语模考系统：三段式考试、流式语音考官、基于 IELTS band descriptors 的评分反馈。</strong>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/fastapi-0.136-009688.svg" alt="FastAPI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"></a>
  <a href="DEPLOY.md"><img src="https://img.shields.io/badge/deploy-Render%20%2B%20Supabase%20%2B%20Groq-orange.svg" alt="Deploy"></a>
</p>

---

## 项目介绍

**IELTS Speaking Judge** 是一个 AI 雅思口语模考系统，用来模拟真实 IELTS Speaking 考试流程。

它包含：

- **Intro**：考官问候并询问姓名
- **Part 1**：围绕一个熟悉话题提问 4 个个人问题
- **Part 2**：Cue Card 题卡，包含 1 分钟准备和 2 分钟作答
- **Part 3**：围绕 Part 2 主题继续提问 5 个观点类问题
- **Feedback**：根据 IELTS 评分标准生成中文反馈报告，并给出更高分表达改写

语音识别和语音朗读都在浏览器中完成，不会把音频上传到后端。

## 功能特点

- 71 个 Part 1 话题
- 61 个 Part 2 Cue Cards
- 61 组 Part 3 主题
- 固定 session 抽题，方便复盘
- Part 2 双计时器：60 秒准备 + 120 秒作答
- 支持本地 Ollama 或云端 Groq
- 支持 SQLite 本地数据库和 Postgres 云端数据库

## 本地运行

需要 **Python 3.12+**。

```bash
git clone https://github.com/paynetim713/IELTS-Speaking-Judge
cd IELTS-Speaking-Judge

python -m venv .venv
.venv/Scripts/activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### 方案 A：使用 Ollama 本地模型

```bash
ollama pull qwen2.5:7b
ollama create ielts-examiner -f Modelfile.ielts-examiner
uvicorn webapp:app --port 8000
```

### 方案 B：使用 Groq 云端模型

```bash
export LLM_PROVIDER=groq
export GROQ_API_KEY=gsk_your_key_here
uvicorn webapp:app --port 8000
```

然后打开：

```text
http://127.0.0.1:8000
```

## 项目结构

```text
.
├── webapp.py                    # FastAPI 后端
├── llm_provider.py              # Ollama / Groq 模型抽象层
├── db.py                        # SQLite / Postgres 数据库抽象层
├── question_bank.py             # 雅思口语题库
├── build_bank.py                # 生成题库
├── extract_speaking.py          # PDF 题目提取工具
├── cambridge_manual.json        # 人工整理题目
├── Modelfile.ielts-examiner     # Ollama 模型配置
├── index.html                   # 前端页面
├── requirements.txt             # Python 依赖
├── render.yaml                  # Render 部署配置
└── DEPLOY.md                    # 部署说明
```

## 环境变量

完整配置请查看 [`.env.example`](.env.example)。

| 变量名 | 说明 |
|---|---|
| `LLM_PROVIDER` | `ollama` 或 `groq` |
| `OLLAMA_URL` | Ollama 服务地址 |
| `GROQ_API_KEY` | Groq API Key |
| `DATABASE_URL` | 数据库连接地址 |
| `IELTS_SECRET_KEY` | Cookie 签名密钥 |
| `CORS_ORIGINS` | 允许访问的前端来源 |

## 致谢

- Cambridge IELTS Books 4–18
- IELTS Liz
- Keith Speaking Academy
- Groq
- Supabase

> 本项目仅用于 IELTS 备考练习，与 Cambridge University Press、IDP IELTS 或 British Council 无官方关联。
