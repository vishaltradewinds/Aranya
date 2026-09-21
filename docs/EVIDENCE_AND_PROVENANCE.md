# ARANYA Evidence and Provenance Baseline

## Evidence ladder

CLAIMED → DOCUMENTED → REMOTE_VERIFIED → FIELD_VERIFIED → AUTHORITY_VERIFIED → OUTCOME_VERIFIED

The ladder records the strength of evidence; it does not itself create statutory authority.

## Evidence types

Identity, ownership, origin, quantity, quality, harvest, transit, authority and delivery evidence are first-class records.

## Provenance

A lot has an append-only sequence of events. Each event identifies:
- event ID
- lot ID
- event type
- actor
- location where relevant
- quantity where relevant
- supporting evidence IDs
- timestamp
- previous event

The chain must not contain unexplained breaks.

## Safety rules

- UNKNOWN is not LEGAL.
- Missing evidence never becomes positive evidence.
- Historical evidence is never silently overwritten.
- Corrections create new events.
- Statutory determinations remain attributable to the competent authority.
- Evidence hashes provide integrity evidence; they are not a substitute for secure storage, signatures or a production ledger.

## Next production hardening

The baseline must be backed by durable database tables, object storage for source documents/media, access-controlled evidence retrieval, migrations, retention policy, cryptographic signing where required, and tamper-evident audit storage before real pilot onboarding.
