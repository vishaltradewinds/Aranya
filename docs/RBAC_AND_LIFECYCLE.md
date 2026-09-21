# ARANYA RBAC and Lifecycle Baseline

## Identity hierarchy

User → Organisation → Role → Permission → Jurisdiction

Permissions are explicit and role-scoped. Administrative access is not a substitute for statutory authority.

## Lot lifecycle

DRAFT → ELIGIBILITY_REVIEW → {TRADE_ELIGIBLE | CONDITIONAL | HOLD | RESTRICTED | UNKNOWN}
TRADE_ELIGIBLE / CONDITIONAL → MATCHED → ORDERED → IN_TRANSIT → DELIVERED → SETTLED

A lot on HOLD or UNKNOWN cannot bypass review to become a transaction state.

## Audit rule

Every future state transition must record actor, previous state, target state, reason and timestamp.

The lifecycle is deliberately restrictive: invalid jumps are rejected rather than repaired silently.
