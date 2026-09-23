"""ARANYA model-agnostic local AI gateway.

Default: Ollama + Gemma 3 4B. No paid AI API is required.
The gateway is deliberately provider/model agnostic so ARANYA can switch
open-weight models without changing journey code.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:4b")
OLLAMA_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "45"))


class AIUnavailable(RuntimeError):
    pass


def _ollama_chat(message: str, context: dict[str, Any] | None = None) -> str:
    system = (
        "You are ARANYA's local AI interpreter. Understand the stakeholder's "
        "intent and context, then suggest only the next useful real-world action. "
        "Do not grant legal authority, invent facts, certify claims, or declare "
        "regulatory approval. If information is missing, ask the minimum useful "
        "question. Keep responses simple and suitable for mobile users."
    )
    if context:
        system += "\nContext:\n" + json.dumps(context, ensure_ascii=False)

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ],
        "options": {"temperature": 0.2},
    }).encode("utf-8")

    request = urllib.request.Request(
        f"{OLLAMA_BASE_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=OLLAMA_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as exc:
        raise AIUnavailable("Local AI is not reachable. Start Ollama and load the configured model.") from exc
    except json.JSONDecodeError as exc:
        raise AIUnavailable("Local AI returned an invalid response.") from exc

    content = data.get("message", {}).get("content")
    if not content:
        raise AIUnavailable("Local AI returned no response.")
    return content.strip()


def interpret(message: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    if not message.strip():
        raise ValueError("message is required")
    try:
        reply = _ollama_chat(message.strip(), context)
        return {
            "provider": "ollama",
            "model": OLLAMA_MODEL,
            "mode": "local",
            "available": True,
            "reply": reply,
        }
    except AIUnavailable as exc:
        return {
            "provider": "ollama",
            "model": OLLAMA_MODEL,
            "mode": "local",
            "available": False,
            "reply": "ARANYA is ready, but its local AI is not connected yet. You can continue capturing the task and sync when AI is available.",
            "error": str(exc),
        }
