# ARANYA Production Execution

## Production vertical slice

ARANYA is being built around one executable loop:

**Ordinary phone → voice/text/photo → intent → journey → next question → network match → evidence → workflow → outcome**

### Production boundaries

- AI interprets; it does not grant authority or certify claims.
- Public intent interpretation is rate-limited and input-bounded.
- Authenticated operations remain protected by RBAC.
- Evidence is append-only; verification creates a new evidence state.
- Regulatory gates remain explicit and attributable.
- PostgreSQL is the production persistence target; SQLite is local development only.
- No production secrets are committed to Git.

### Current executable slice

1. Mobile/PWA entry experience.
2. Browser voice capture where supported.
3. Photo capture and offline task indication.
4. Local-first AI gateway through Ollama/Gemma.
5. Deterministic structured intent extraction before AI response.
6. Journey identification from intent.
7. Existing lot/evidence/regulatory workflow foundation.

### Next build gates

1. Persistent network registry + N2N matching.
2. Journey state persistence and task queue.
3. Real evidence file/object storage.
4. Identity/onboarding and network membership workflows.
5. Transaction/order/settlement records.
6. Production AI runtime for public users or an explicitly provisioned on-prem/edge gateway.
7. End-to-end Jabalpur pilot.

Production means these gates are implemented and verified, not merely documented.
