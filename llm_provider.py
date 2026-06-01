"""Local Ollama / hosted Groq abstraction. Switch via LLM_PROVIDER env var.

Env:
    LLM_PROVIDER          ollama (default) | groq
    OLLAMA_URL            http://localhost:11434
    GROQ_API_KEY          required for groq
    GROQ_BASE_URL         https://api.groq.com/openai/v1
    LLM_EXAMINER_MODEL    overrides default examiner model
    LLM_FEEDBACK_MODEL    overrides default feedback model
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Generator

import requests

HERE = Path(__file__).parent

PROVIDER = (os.environ.get("LLM_PROVIDER") or "ollama").strip().lower()
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/")
GROQ_BASE_URL = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or ""

if PROVIDER == "groq":
    DEFAULT_EXAMINER = "llama-3.3-70b-versatile"
    DEFAULT_FEEDBACK = "llama-3.3-70b-versatile"
else:
    DEFAULT_EXAMINER = "ielts-examiner"
    DEFAULT_FEEDBACK = "qwen2.5:14b-instruct-q3_K_M"

EXAMINER_MODEL = os.environ.get("LLM_EXAMINER_MODEL", DEFAULT_EXAMINER)
FEEDBACK_MODEL = os.environ.get("LLM_FEEDBACK_MODEL", DEFAULT_FEEDBACK)


def examiner_model() -> str:
    return EXAMINER_MODEL


def feedback_model() -> str:
    return FEEDBACK_MODEL


# The examiner persona is baked into Ollama via the Modelfile; for Groq we
# extract it here and prepend it on every call.
_MODELFILE_PATH = HERE / "Modelfile.ielts-examiner"


def _extract_modelfile_system() -> str:
    if not _MODELFILE_PATH.exists():
        return ""
    txt = _MODELFILE_PATH.read_text(encoding="utf-8")
    m = re.search(r'SYSTEM\s+"""(.*?)"""', txt, re.DOTALL)
    return m.group(1).strip() if m else ""


_BASE_SYSTEM_PROMPT = _extract_modelfile_system()


def embed_system_prompt(messages: list[dict], kind: str) -> list[dict]:
    """Prepend the examiner persona for Groq. Pass-through for Ollama (baked in)
    and for the feedback turn (its hint is already self-contained)."""
    if PROVIDER != "groq" or not _BASE_SYSTEM_PROMPT or kind == "feedback":
        return messages
    return [{"role": "system", "content": _BASE_SYSTEM_PROMPT}] + messages


def chat_stream(
    messages: list[dict],
    *,
    model: str,
    temperature: float = 0.5,
    num_ctx: int = 8192,
    timeout: float = 600.0,
) -> Generator[tuple[str, bool], None, None]:
    """Yield (chunk_text, done_flag) for each streamed token. done_flag is True
    only on the final yield."""
    if PROVIDER == "groq":
        yield from _groq_stream(messages, model=model, temperature=temperature, timeout=timeout)
    else:
        yield from _ollama_stream(
            messages, model=model, temperature=temperature, num_ctx=num_ctx, timeout=timeout
        )


def _ollama_stream(messages, *, model, temperature, num_ctx, timeout):
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {"num_ctx": num_ctx, "temperature": temperature},
    }
    with requests.post(f"{OLLAMA_URL}/api/chat", json=payload, stream=True, timeout=timeout) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line:
                continue
            obj = json.loads(line)
            piece = obj.get("message", {}).get("content", "")
            done = bool(obj.get("done"))
            if piece:
                yield (piece, done)
            elif done:
                yield ("", True)
            if done:
                break


def _groq_stream(messages, *, model, temperature, timeout):
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set but LLM_PROVIDER=groq")
    payload = {"model": model, "messages": messages, "stream": True, "temperature": temperature}
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    with requests.post(
        f"{GROQ_BASE_URL}/chat/completions",
        json=payload, headers=headers, stream=True, timeout=timeout,
    ) as r:
        r.raise_for_status()
        for raw in r.iter_lines():
            if not raw:
                continue
            line = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            # OpenAI SSE: `data: {...}` per chunk, terminated by `data: [DONE]`.
            if line.startswith("data:"):
                data = line[5:].lstrip()
            else:
                continue
            if data == "[DONE]":
                yield ("", True)
                break
            try:
                obj = json.loads(data)
            except json.JSONDecodeError:
                continue
            choices = obj.get("choices") or []
            if not choices:
                continue
            piece = (choices[0].get("delta") or {}).get("content") or ""
            done = choices[0].get("finish_reason") is not None
            if piece:
                yield (piece, done)
            if done:
                yield ("", True)
                break


def list_available_models() -> set[str]:
    """Set of model names the provider currently exposes. Empty on error."""
    if PROVIDER == "groq":
        if not GROQ_API_KEY:
            return set()
        try:
            r = requests.get(
                f"{GROQ_BASE_URL}/models",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                timeout=5,
            )
            r.raise_for_status()
            return {m["id"] for m in r.json().get("data", [])}
        except Exception:
            return set()
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        r.raise_for_status()
        return {m["name"] for m in r.json().get("models", [])}
    except Exception:
        return set()


def is_connection_error(exc: BaseException) -> bool:
    return isinstance(exc, (requests.exceptions.ConnectionError, requests.exceptions.Timeout))
