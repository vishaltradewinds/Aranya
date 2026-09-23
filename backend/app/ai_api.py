from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .ai_gateway import interpret
from .intent import understand

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])
_requests: dict[str, deque[float]] = defaultdict(deque)
WINDOW_SECONDS = 60
MAX_REQUESTS = 30

class UnderstandRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    context: dict[str, Any] = Field(default_factory=dict)


def _rate_limit(request: Request) -> None:
    key = request.client.host if request.client else "unknown"
    now = time.monotonic()
    bucket = _requests[key]
    while bucket and now - bucket[0] > WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= MAX_REQUESTS:
        raise HTTPException(429, "Too many requests. Please wait a moment and try again.")
    bucket.append(now)

@router.get("/health")
def ai_health():
    return {"service": "aranya-ai", "mode": "local-first", "configured_model": __import__("os").getenv("OLLAMA_MODEL", "gemma3:4b")}

@router.post("/understand")
def ai_understand(payload: UnderstandRequest, request: Request):
    _rate_limit(request)
    parsed = understand(payload.message, payload.context)
    ai = interpret(payload.message, {**payload.context, "structured_intent": parsed.as_dict()})
    return {
        "intent": parsed.as_dict(),
        "ai": ai,
        "journey": {
            "key": parsed.journey_key,
            "state": "INTENT_IDENTIFIED",
            "next_action": parsed.next_action,
            "questions": list(parsed.missing_questions),
        },
    }
