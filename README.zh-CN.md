# IELTS Speaking Judge

<p align="center">
  <strong>在浏览器里练 IELTS Speaking：AI 考官、真实考试节奏、结束后给出可修改的口语反馈。</strong>
</p>

<h3 align="center">选择语言</h3>

<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/English-README-1f6feb?style=for-the-badge&labelColor=0d1117" alt="English README"></a>
  <a href="README.zh-CN.md"><img src="https://img.shields.io/badge/%E4%B8%AD%E6%96%87-README-1f6feb?style=for-the-badge&labelColor=0d1117" alt="中文 README"></a>
  <a href="README.ar.md"><img src="https://img.shields.io/badge/%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9-README-1f6feb?style=for-the-badge&labelColor=0d1117" alt="Arabic README"></a>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12+-blue.svg" alt="Python"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/fastapi-0.136-009688.svg" alt="FastAPI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"></a>
  <a href="DEPLOY.md"><img src="https://img.shields.io/badge/deploy-Render%20%2B%20Supabase%20%2B%20Groq-orange.svg" alt="Deploy"></a>
</p>

---

## 为什么做这个项目

我做 **IELTS Speaking Judge** 的原因很简单：很多口语练习工具看起来很智能，但练起来不像真正的 IELTS Speaking。

有些工具只是随机问几个问题，有些只给一个分数，还有些不会模拟 Part 2 的准备时间和作答压力。真正考试的时候，考生要按 Intro、Part 1、Part 2、Part 3 的节奏一路说下去，所以我希望这个项目更接近真实模考，而不是普通聊天机器人。

这个项目主要适合想自己练口语、想反复复盘、想知道自己答案哪里可以改的 IELTS 学习者。

## 它能做什么

系统会模拟 IELTS Speaking 的完整流程：

- **Intro**：考官先问候，并确认考生姓名
- **Part 1**：围绕一个常见话题问几个简短个人问题
- **Part 2**：给出 Cue Card，有 1 分钟准备和 2 分钟作答时间
- **Part 3**：根据 Part 2 主题继续追问更抽象的观点类问题
- **Feedback**：根据考生真实回答生成反馈，并给出更自然、更高分的表达改写

语音识别和语音朗读都在浏览器里完成，后端不需要接收或保存原始音频。

## 主要特点

- 71 个 Part 1 话题、61 个 Part 2 Cue Cards、61 组 Part 3 主题
- 每个 session 的题目是固定的，方便之后复盘
- Part 2 内置准备计时器和作答计时器
- 反馈会参考 IELTS band descriptors，不只是随便给一个 AI 分数
- 支持本地 **Ollama**，也支持云端 **Groq**
- 本地开发用 **SQLite**，部署时可以切换到 **Postgres**
- 前端是单文件页面，项目结构比较容易看懂

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

### 方案 A：使用 Ollama 本地运行

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
├── webapp.py                    # FastAPI 后端：认证、session、聊天流
├── llm_provider.py              # Ollama / Groq 模型封装
├── db.py                        # SQLite / Postgres 数据库封装
├── question_bank.py             # IELTS Speaking 题库
├── build_bank.py                # 重新生成题库
├── extract_speaking.py          # 从 PDF 提取口语题目
├── cambridge_manual.json        # 人工整理的 Cambridge 题目
├── Modelfile.ielts-examiner     # Ollama 考官提示词
├── index.html                   # 浏览器前端
├── requirements.txt             # Python 依赖
├── render.yaml                  # Render 部署配置
└── DEPLOY.md                    # 部署说明
```

## 配置

完整配置可以看 [`.env.example`](.env.example)。

| 变量名 | 说明 |
|---|---|
| `LLM_PROVIDER` | 选择 `ollama` 或 `groq` |
| `OLLAMA_URL` | Ollama 服务地址 |
| `GROQ_API_KEY` | 使用 Groq 时需要填写 |
| `DATABASE_URL` | 数据库连接地址 |
| `IELTS_SECRET_KEY` | Cookie 签名密钥 |
| `CORS_ORIGINS` | 允许访问的前端来源 |

## 说明

这个项目不是官方 IELTS 评分系统。它更像是一个练习工具：帮助学习者在接近真实考试的流程里开口说话，然后根据回答内容发现重复问题、修改表达、继续练习。

浏览器语音识别效果也会受浏览器、麦克风、口音和网络环境影响。

## 致谢

- Cambridge IELTS Books 4–18
- IELTS Liz
- Keith Speaking Academy
- Groq
- Supabase

> 本项目仅用于 IELTS 备考练习，与 Cambridge University Press、IDP IELTS 或 British Council 无官方关联。
