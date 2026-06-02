"""Local Ollama / hosted Groq / DeepSeek abstraction. Switch via env vars.

Env:
    LLM_PROVIDER             ollama (default) | groq | deepseek
    LLM_FEEDBACK_PROVIDER    overrides provider for the feedback turn only;
                             defaults to LLM_PROVIDER. Set to "deepseek" to
                             route just the band-scoring turn to DeepSeek R1
                             while keeping the chattier examiner on Groq.
    OLLAMA_URL               http://localhost:11434
    GROQ_API_KEY             required when groq is in use
    GROQ_BASE_URL            https://api.groq.com/openai/v1
    DEEPSEEK_API_KEY         required when deepseek is in use
    DEEPSEEK_BASE_URL        https://api.deepseek.com/v1
    LLM_EXAMINER_MODEL       overrides default examiner model
    LLM_FEEDBACK_MODEL       overrides default feedback model
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Generator

import requests

HERE = Path(__file__).parent


def _env(name: str, default: str = "") -> str:
    return (os.environ.get(name) or default).strip()


PROVIDER = _env("LLM_PROVIDER", "ollama").lower()
FEEDBACK_PROVIDER = _env("LLM_FEEDBACK_PROVIDER", PROVIDER).lower()

OLLAMA_URL = _env("OLLAMA_URL", "http://localhost:11434").rstrip("/")
GROQ_BASE_URL = _env("GROQ_BASE_URL", "https://api.groq.com/openai/v1").rstrip("/")
GROQ_API_KEY = _env("GROQ_API_KEY")
DEEPSEEK_BASE_URL = _env("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1").rstrip("/")
DEEPSEEK_API_KEY = _env("DEEPSEEK_API_KEY")


def _default_model(provider: str, kind: str) -> str:
    if provider == "groq":
        return "llama-3.3-70b-versatile"
    if provider == "deepseek":
        # v4-pro shines for grading (longer reasoning); v4-flash is the cheaper
        # tier that fits the chattier examiner role.
        return "deepseek-v4-pro" if kind == "feedback" else "deepseek-v4-flash"
    return "ielts-examiner" if kind == "examiner" else "qwen2.5:14b-instruct-q3_K_M"


def _model_belongs_to(provider: str, model: str) -> bool:
    """Heuristic: does `model` look like one the provider actually serves?
    Used to catch stale env vars where someone changes LLM_FEEDBACK_PROVIDER
    but forgets to also update LLM_FEEDBACK_MODEL."""
    m = (model or "").lower()
    if provider == "groq":
        return "llama" in m or "mixtral" in m or "gemma" in m or "qwen" in m
    if provider == "deepseek":
        return m.startswith("deepseek")
    return True  # ollama — anything goes


def _resolve_model(env_var: str, provider: str, kind: str) -> str:
    """Pick the env override only if it matches the provider; otherwise log
    and fall back to the provider's default, so a stale env var can't take
    down the deploy."""
    explicit = _env(env_var)
    if explicit and _model_belongs_to(provider, explicit):
        return explicit
    fallback = _default_model(provider, kind)
    if explicit and explicit != fallback:
        print(f"[llm] {env_var}={explicit!r} doesn't match provider={provider}; "
              f"using {fallback!r} instead.")
    return fallback


EXAMINER_MODEL = _resolve_model("LLM_EXAMINER_MODEL", PROVIDER, "examiner")
FEEDBACK_MODEL = _resolve_model("LLM_FEEDBACK_MODEL", FEEDBACK_PROVIDER, "feedback")


def examiner_model() -> str:
    return EXAMINER_MODEL


def feedback_model() -> str:
    return FEEDBACK_MODEL


_MODELFILE_PATH = HERE / "Modelfile.ielts-examiner"


def _extract_modelfile_system() -> str:
    if not _MODELFILE_PATH.exists():
        return ""
    txt = _MODELFILE_PATH.read_text(encoding="utf-8")
    m = re.search(r'SYSTEM\s+"""(.*?)"""', txt, re.DOTALL)
    return m.group(1).strip() if m else ""


_BASE_SYSTEM_PROMPT = _extract_modelfile_system()


def embed_system_prompt(messages: list[dict], kind: str) -> list[dict]:
    """Prepend the examiner persona for non-Ollama providers. Ollama bakes the
    persona into the model via Modelfile, so we don't re-send it there.
    Feedback turns get a fully self-contained hint, so persona is irrelevant."""
    if kind == "feedback":
        return messages
    if PROVIDER == "ollama" or not _BASE_SYSTEM_PROMPT:
        return messages
    return [{"role": "system", "content": _BASE_SYSTEM_PROMPT}] + messages


def _alternate_provider(primary: str) -> str | None:
    """If the primary cloud provider rate-limits, who can we try instead?
    Only returns a provider we actually have credentials for."""
    if primary == "groq" and DEEPSEEK_API_KEY:
        return "deepseek"
    if primary == "deepseek" and GROQ_API_KEY:
        return "groq"
    return None


def _stream_one(messages, *, model, temperature, num_ctx, timeout, provider, for_feedback):
    if provider == "ollama":
        yield from _ollama_stream(
            messages, model=model, temperature=temperature, num_ctx=num_ctx, timeout=timeout
        )
    else:
        yield from _openai_compat_stream(
            messages, model=model, temperature=temperature, timeout=timeout,
            provider=provider, for_feedback=for_feedback,
        )


def chat_stream(
    messages: list[dict],
    *,
    model: str,
    temperature: float = 0.5,
    num_ctx: int = 8192,
    timeout: float = 600.0,
    for_feedback: bool = False,
) -> Generator[tuple[str, bool], None, None]:
    """Yield (chunk_text, done_flag) for each streamed token. done_flag is True
    only on the final yield. for_feedback routes to LLM_FEEDBACK_PROVIDER.

    On a primary-provider 429 (rate-limited BEFORE any token is streamed) the
    call transparently retries against the alternate provider — Groq's free
    100k-tokens/day quota is tight enough that we'd otherwise lock users out
    until UTC midnight. The fallback only fires if no chunks have been yielded
    yet so the user never sees a duplicate or partial reply.
    """
    primary = FEEDBACK_PROVIDER if for_feedback else PROVIDER
    fallback = _alternate_provider(primary) if primary != "ollama" else None

    # Probe-and-buffer the first chunk so we can detect 429 before the caller
    # starts consuming tokens.
    gen = _stream_one(messages, model=model, temperature=temperature,
                      num_ctx=num_ctx, timeout=timeout, provider=primary,
                      for_feedback=for_feedback)
    try:
        first = next(gen)
    except StopIteration:
        return
    except RuntimeError as e:
        msg = str(e)
        if fallback and (" 429" in msg or " 503" in msg or " 502" in msg):
            kind = "feedback" if for_feedback else "examiner"
            alt_model = _default_model(fallback, kind)
            print(f"[llm] {primary} {msg.split(':')[1].strip()[:30]} — falling back to {fallback} ({alt_model})")
            yield from _stream_one(
                messages, model=alt_model, temperature=temperature,
                num_ctx=num_ctx, timeout=timeout, provider=fallback,
                for_feedback=for_feedback,
            )
            return
        raise
    yield first
    yield from gen


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


def _openai_compat_stream(messages, *, model, temperature, timeout, provider, for_feedback=False):
    """OpenAI-format SSE — works for Groq, DeepSeek, and OpenAI itself.

    for_feedback controls reasoning_content handling: feedback turns get the
    chain-of-thought wrapped in <think>...</think> (the SSE strip layer then
    removes it before the user sees anything). Examiner turns drop reasoning
    entirely — otherwise the live chat fills with tiny <think>X</think> chunks."""
    if provider == "groq":
        base_url, api_key = GROQ_BASE_URL, GROQ_API_KEY
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set but LLM_PROVIDER=groq")
    elif provider == "deepseek":
        base_url, api_key = DEEPSEEK_BASE_URL, DEEPSEEK_API_KEY
        if not api_key:
            raise RuntimeError("DEEPSEEK_API_KEY not set but provider=deepseek")
    else:
        raise RuntimeError(f"unsupported provider: {provider}")
    payload = {"model": model, "messages": messages, "stream": True, "temperature": temperature}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    with requests.post(
        f"{base_url}/chat/completions",
        json=payload, headers=headers, stream=True, timeout=timeout,
    ) as r:
        if r.status_code >= 400:
            # Bare raise_for_status hides the JSON detail that says WHICH field
            # was rejected. Pull the body and bake it into the exception so the
            # SSE error event surfaces it to the client.
            try:
                body = next(r.iter_content(8192, decode_unicode=True)) or ""
            except Exception:
                body = "<unreadable>"
            print(f"[llm] {provider} {r.status_code}: {body[:500]}")
            raise RuntimeError(f"{provider} {r.status_code}: {body[:300]}")
        for raw in r.iter_lines():
            if not raw:
                continue
            line = raw.decode("utf-8") if isinstance(raw, bytes) else raw
            if not line.startswith("data:"):
                continue
            data = line[5:].lstrip()
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
            # DeepSeek v4 streams chain-of-thought in delta.reasoning_content,
            # separate from delta.content. For feedback we keep it (wrapped so
            # the post-stream <think> strip catches it). For examiner turns
            # we drop it — those go straight to the user, no strip layer.
            if for_feedback and not piece:
                reasoning = delta.get("reasoning_content") or ""
                if reasoning:
                    piece = f"<think>{reasoning}</think>"
            done = choices[0].get("finish_reason") is not None
            if piece:
                yield (piece, done)
            if done:
                yield ("", True)
                break


def list_available_models() -> set[str]:
    """Best-effort model list from the primary provider. Empty on error/auth fail."""
    if PROVIDER == "ollama":
        try:
            r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
            r.raise_for_status()
            return {m["name"] for m in r.json().get("models", [])}
        except Exception:
            return set()
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
    if PROVIDER == "deepseek":
        if not DEEPSEEK_API_KEY:
            return set()
        try:
            r = requests.get(
                f"{DEEPSEEK_BASE_URL}/models",
                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
                timeout=5,
            )
            r.raise_for_status()
            return {m["id"] for m in r.json().get("data", [])}
        except Exception:
            return set()
    return set()


def is_connection_error(exc: BaseException) -> bool:
    return isinstance(exc, (requests.exceptions.ConnectionError, requests.exceptions.Timeout))
