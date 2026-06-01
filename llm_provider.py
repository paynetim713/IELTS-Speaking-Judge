"""LLM provider abstraction so webapp.py can switch between local Ollama and
hosted Groq (or any OpenAI-compatible API) without code changes.

Env vars (all optional):
    LLM_PROVIDER          - "ollama" (default) or "groq"
    OLLAMA_URL            - default http://localhost:11434
    GROQ_API_KEY          - required when LLM_PROVIDER=groq
    GROQ_BASE_URL         - default https://api.groq.com/openai/v1
    LLM_EXAMINER_MODEL    - default "ielts-examiner" for ollama, "llama-3.3-70b-versatile" for groq
    LLM_FEEDBACK_MODEL    - default "qwen2.5:14b-instruct-q3_K_M" for ollama, same as examiner for groq

Public API (used by webapp.py):
    chat_stream(messages, kind, options) -> generator yielding (chunk_text, done_flag)
    list_available_models() -> set[str]   # for the cached availability check
    examiner_model() / feedback_model()   # the model name to pass downstream
    embed_system_prompt(messages, kind) -> messages   # injects the Modelfile system
                                                       # prompt when using Groq
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Generator, Iterable

import requests

HERE = Path(__file__).parent

# ── Provider selection ──────────────────────────────────────────────────
PROVIDER = (os.environ.get("LLM_PROVIDER") or "ollama").strip().lower()

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434").rstrip("/")
GROQ_BASE_URL = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY") or ""

# ── Model selection (per-provider defaults, overridable via env) ────────
if PROVIDER == "groq":
    DEFAULT_EXAMINER = "llama-3.3-70b-versatile"   # best free Groq model
    DEFAULT_FEEDBACK = "llama-3.3-70b-versatile"   # same — Groq has no 'bigger' tier on free
else:
    DEFAULT_EXAMINER = "ielts-examiner"
    DEFAULT_FEEDBACK = "qwen2.5:14b-instruct-q3_K_M"

EXAMINER_MODEL = os.environ.get("LLM_EXAMINER_MODEL", DEFAULT_EXAMINER)
FEEDBACK_MODEL = os.environ.get("LLM_FEEDBACK_MODEL", DEFAULT_FEEDBACK)


def examiner_model() -> str:
    return EXAMINER_MODEL


def feedback_model() -> str:
    return FEEDBACK_MODEL


# ── System-prompt injection for Groq ────────────────────────────────────
# Ollama's Modelfile bakes the examiner persona/system prompt into the model
# itself, so webapp.py never sends it explicitly. For Groq we have to send it
# every call.
_MODELFILE_PATH = HERE / "Modelfile.ielts-examiner"


def _extract_modelfile_system() -> str:
    if not _MODELFILE_PATH.exists():
        return ""
    txt = _MODELFILE_PATH.read_text(encoding="utf-8")
    # SYSTEM """...""" block
    m = re.search(r'SYSTEM\s+"""(.*?)"""', txt, re.DOTALL)
    return m.group(1).strip() if m else ""


_BASE_SYSTEM_PROMPT = _extract_modelfile_system()


def embed_system_prompt(messages: list[dict], kind: str) -> list[dict]:
    """For Groq: prepend the examiner persona system prompt that Ollama bakes in.
    For Ollama: pass-through (model already has the persona). For the feedback
    turn we DON'T prepend — the feedback hint is fully self-contained and the
    examiner persona is irrelevant there."""
    if PROVIDER != "groq" or not _BASE_SYSTEM_PROMPT or kind == "feedback":
        return messages
    return [{"role": "system", "content": _BASE_SYSTEM_PROMPT}] + messages


# ── Streaming chat ──────────────────────────────────────────────────────
def chat_stream(
    messages: list[dict],
    *,
    model: str,
    temperature: float = 0.5,
    num_ctx: int = 8192,
    timeout: float = 600.0,
) -> Generator[tuple[str, bool], None, None]:
    """Yield (chunk_text, done_flag) for each streamed token.

    `done_flag` is True only on the final yield, so callers can break safely.
    """
    if PROVIDER == "groq":
        yield from _groq_stream(messages, model=model, temperature=temperature, timeout=timeout)
    else:
        yield from _ollama_stream(
            messages, model=model, temperature=temperature, num_ctx=num_ctx, timeout=timeout
        )


def _ollama_stream(
    messages: list[dict],
    *,
    model: str,
    temperature: float,
    num_ctx: int,
    timeout: float,
) -> Generator[tuple[str, bool], None, None]:
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "options": {"num_ctx": num_ctx, "temperature": temperature},
    }
    with requests.post(
        f"{OLLAMA_URL}/api/chat",
        json=payload,
        stream=True,
        timeout=timeout,
    ) as r:
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


def _groq_stream(
    messages: list[dict],
    *,
    model: str,
    temperature: float,
    timeout: float,
) -> Generator[tuple[str, bool], None, None]:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set but LLM_PROVIDER=groq")
    payload = {
        "model": model,
        "messages": messages,
        "stream": True,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    with requests.post(
        f"{GROQ_BASE_URL}/chat/completions",
        json=payload,
        headers=headers,
        stream=True,
        timeout=timeout,
    ) as r:
        r.raise_for_status()
        for raw in r.iter_lines():
            if not raw:
                continue
            line = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            # OpenAI-compat SSE: "data: {json}" lines, terminated by "data: [DONE]"
            if line.startswith("data: "):
                data = line[6:].strip()
            elif line.startswith("data:"):
                data = line[5:].strip()
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
            delta = choices[0].get("delta") or {}
            piece = delta.get("content") or ""
            finish = choices[0].get("finish_reason")
            done = finish is not None
            if piece:
                yield (piece, done)
            if done:
                yield ("", True)
                break


# ── Model availability (for the existing cached check) ──────────────────
def list_available_models() -> set[str]:
    """Return the set of model names known to the provider. Used by the
    existing 60s availability cache in webapp.py."""
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
    # Ollama
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        r.raise_for_status()
        return {m["name"] for m in r.json().get("models", [])}
    except Exception:
        return set()


def is_connection_error(exc: BaseException) -> bool:
    """Stable predicate so webapp.py doesn't have to know provider internals."""
    return isinstance(
        exc,
        (requests.exceptions.ConnectionError, requests.exceptions.Timeout),
    )
