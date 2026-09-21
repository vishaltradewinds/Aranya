# ARANYA Implementation Baseline

This repository now contains the first executable hardening slice.

## Working path

Health → create lot → immutable audit event → retrieve lot → retrieve audit history.

## Safety defaults

- New lots begin with evidence state CLAIMED.
- New lots begin with regulatory status UNKNOWN.
- UNKNOWN is never treated as legal/eligible.
- Historical audit events are append-only in the application model.
- Statutory decisions are not simulated by the platform.

## Current limitation

The persistence layer is intentionally minimal for the first executable slice. Before real onboarding it must be replaced with durable storage, authentication/RBAC, transactional consistency, state-transition controls, evidence storage, regulatory rule packs, observability, backups and production security controls.

## Hardening order

1. Durable persistence and migrations.
2. Identity, organisations and RBAC.
3. Canonical domain entities and lifecycle/state machine.
4. Evidence/provenance service.
5. Rules engine with versioned MP configuration.
6. Matching/order/movement/delivery/settlement.
7. End-to-end transaction tests.
8. Production security, observability and recovery.
9. Pilot readiness gate.
