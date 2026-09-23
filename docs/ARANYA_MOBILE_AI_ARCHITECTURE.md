# ARANYA Mobile-First AI Architecture

## Decision

ARANYA must work for stakeholders using ordinary mobile phones. The stakeholder device must **not** be required to run an LLM.

The default AI deployment is therefore:

**Mobile web/PWA → ARANYA API → model-agnostic AI Gateway → Ollama → open-weight model**

The initial reference model is **Gemma 3 4B**. The gateway keeps the model replaceable.

## Zero paid AI API dependency

ARANYA does not depend on a paid proprietary AI API.

Default development/pilot configuration:

- ARANYA_AI_PROVIDER=ollama
- OLLAMA_BASE_URL=http://127.0.0.1:11434
- OLLAMA_MODEL=gemma3:4b

Running inference on controlled hardware avoids per-token API charges. Infrastructure and connectivity costs are separate from model/API licensing.

## Device principle

The phone is a **thin work interface**, not the AI server.

It should support Android browser, installable PWA, low-bandwidth operation, voice input, text input, photo capture, assisted workflows, and offline capture with later synchronisation.

Where a capable device eventually supports local inference, ARANYA may use it, but that is an optimization rather than a requirement.

## AI Gateway contract

All AI calls pass through one ARANYA gateway. The gateway owns provider selection, model selection, timeout/failure handling, context injection, safe system instructions and response normalization.

Journey code must not call Ollama or a specific model directly.

## Safety boundary

AI can interpret and orchestrate. It must not grant statutory authority, certify a resource, convert a claim into verified fact, invent regulatory approval, silently override rules, or decide matters reserved for competent authorities.

## Current implementation

- backend/app/ai_gateway.py provides the local Ollama gateway.
- POST /api/v1/ai/interpret exposes interpretation to the mobile experience.
- The frontend provides a lightweight mobile input path.
- manifest.webmanifest makes the frontend installable.
- sw.js provides an initial offline shell cache.

## Next hardening

1. deployment configuration for the API URL;
2. authenticated AI permissions distinct from lot permissions;
3. rate limits and request-size limits;
4. structured intent output;
5. voice capture/transcription;
6. photo input;
7. offline task queue and synchronisation;
8. model health checks;
9. model-router policy and fallback models;
10. benchmarks on low-cost hardware and ordinary Android devices.

## Target

> **Any stakeholder. Ordinary phone. Simple interaction. No paid AI API dependency.**
