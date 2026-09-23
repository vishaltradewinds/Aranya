from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

class IntentType(str, Enum):
    HAVE = "I_HAVE"
    NEED = "I_NEED"
    CAN = "I_CAN"
    CONNECT = "I_WANT_TO_CONNECT"
    UNKNOWN = "UNKNOWN"

@dataclass(frozen=True)
class Intent:
    intent_type: IntentType
    object: str | None
    quantity: str | None
    location: str | None
    goal: str | None
    language: str
    confidence: float
    missing_questions: tuple[str, ...]
    journey_key: str
    next_action: str

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["intent_type"] = self.intent_type.value
        data["missing_questions"] = list(self.missing_questions)
        return data

_KEYWORDS = {
    IntentType.HAVE: ("mere paas", "i have", "available", "hai", "है", "पास"),
    IntentType.NEED: ("mujhe chahiye", "i need", "need", "kharid", "buy", "चाहिए", "खरीद"),
    IntentType.CAN: ("main kar sakta", "i can", "capacity", "service", "कर सकता", "क्षमता"),
    IntentType.CONNECT: ("judna", "connect", "network", "partner", "जुड़", "नेटवर्क"),
}


def _detect_intent(message: str, selected: str | None) -> IntentType:
    if selected:
        return {"have": IntentType.HAVE, "need": IntentType.NEED, "can": IntentType.CAN, "connect": IntentType.CONNECT}.get(selected, IntentType.UNKNOWN)
    low = message.lower()
    scores = {kind: sum(1 for token in tokens if token in low) for kind, tokens in _KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else IntentType.UNKNOWN


def _quantity(message: str) -> str | None:
    match = re.search(r"\b\\d+(?:[.,]\\d+)?\\s*(?:kg|kgs|kilo|kilos|kg|kgs|tonne|tonnes|tons?|quintal|litre|litres|units?|truckloads?)?\\b", message.lower())
    return match.group(0) if match else None


def _location(message: str) -> str | None:
    patterns = [r"(?:from|se|mein|in|at|near|जिला|में)\s+([A-Za-z][A-Za-z .'-]{2,50})"]
    for pattern in patterns:
        m = re.search(pattern, message, re.I)
        if m:
            value = m.group(1).strip(" .,-")
            if value and value.lower() not in {"hai", "chahiye", "mp", "india"}:
                return value
    return None


def _object(message: str) -> str | None:
    low = message.lower()
    known = ["mahua", "bamboo", "tendu", "lac", "honey", "medicinal plant", "medicinal plants", "transport", "truck", "warehouse", "processing", "research"]
    for item in known:
        if item in low:
            return item
    cleaned = re.sub(r"\b(?:mere paas|mujhe chahiye|i have|i need|main kar sakta hoon|i can)\b", "", low, flags=re.I).strip(" .,!?")
    return cleaned[:80] or None


def understand(message: str, context: dict[str, Any] | None = None) -> Intent:
    context = context or {}
    kind = _detect_intent(message, context.get("selected_intent"))
    quantity = _quantity(message)
    location = _location(message)
    obj = _object(message)
    goal = None
    low = message.lower()
    if any(x in low for x in ("sell", "bech", "market", "buyer", "बेचना", "खरीदार", "बाजार")):
        goal = "find_market_or_buyer"
    elif any(x in low for x in ("buy", "purchase", "kharid", "खरीद")):
        goal = "source_and_buy"
    elif any(x in low for x in ("transport", "truck", "logistics", "परिवहन")):
        goal = "arrange_logistics"
    journey = {
        IntentType.HAVE: "resource_to_outcome",
        IntentType.NEED: "need_to_source",
        IntentType.CAN: "capability_to_opportunity",
        IntentType.CONNECT: "network_to_network",
        IntentType.UNKNOWN: "clarify_intent",
    }[kind]
    missing: list[str] = []
    if kind == IntentType.UNKNOWN:
        missing.append("Aapke paas kya hai, kya chahiye, ya aap kya kar sakte hain?")
    if not obj:
        missing.append("Kis cheez ke baare mein baat ho rahi hai?")
    if kind in (IntentType.HAVE, IntentType.NEED) and not quantity:
        missing.append("Kitni quantity hai ya chahiye?")
    confidence = 0.9 if kind != IntentType.UNKNOWN and obj else (0.6 if kind != IntentType.UNKNOWN else 0.2)
    return Intent(kind, obj, quantity, location, goal, context.get("language", "auto"), confidence, tuple(missing[:2]), journey,
                  "intent_confirm" if confidence >= 0.6 else "clarify_intent")
