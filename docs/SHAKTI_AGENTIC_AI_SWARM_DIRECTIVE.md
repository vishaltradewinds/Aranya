# SHAKTI Principal Directive PD-01 — Mandatory Agentic AI Swarm Systems

**Status:** Founder-designated mandatory, non-waivable principal directive.  
**Applicability:** Every project, platform, subsystem, phase, engineering activity and operational workflow governed by SHAKTI Standards.

## 1. Non-negotiable requirement

Every SHAKTI-governed system MUST be designed, engineered, tested and operated with a coordinated Agentic AI Swarm architecture. No project, phase, module, team or delivery owner may omit, waive, downgrade or silently defer this requirement.

Project-specific implementation may vary; compliance with the directive may not. If implementation is incomplete, record a SHAKTI non-conformance and block the applicable readiness/release gate. Staged implementation is permitted; exemption is not.

## 2. Minimum agent responsibilities

Every project MUST provide explicit responsibilities for:
- **Orchestrator:** decomposes objectives, delegates work, manages dependencies and coordinates completion.
- **Domain specialists:** execute bounded tasks for the project's actual domain and workflows.
- **Research and evidence:** gathers traceable evidence, evaluates source quality and records uncertainty.
- **Engineering and operations:** supports implementation, testing, maintenance and operational execution.
- **Security, safety and compliance:** checks permissions, threats, statutory requirements and policy boundaries.
- **Quality and verification:** checks outputs against acceptance criteria and evidence, independently where needed.
- **Monitoring and recovery:** detects failures, manages bounded retries/recovery and escalates unresolved risks.
- **Reporting and audit:** preserves decisions, provenance, task history, results and limitations.

These are functional responsibilities, not necessarily separate models or separate services. Roles may share a runtime only where separation does not undermine verification, separation of duties or safety.

## 3. Mandatory controls

Each swarm MUST implement and evidence, proportionate to risk:
1. Defined agent identities, responsibilities, permissions and least-privilege access.
2. An authoritative task state and shared evidence/provenance record.
3. Dependency-aware orchestration, prioritisation, idempotency and duplicate-work controls.
4. Input validation, source trust boundaries and prompt/instruction-injection protection.
5. Independent verification for material, safety-critical, financial, legal or regulated outputs.
6. Bounded retries, timeouts, queue limits, failure isolation and human escalation.
7. Durable audit logs, versioning, traceability and reproducible outcomes.
8. Human approval gates for consequential actions and controlled release.
9. Cost, latency, resource, model and service-availability monitoring.
10. Safe degraded/fallback mode when models, tools, networks or agents are unavailable.
11. Data protection, tenant isolation, secrets handling and retention controls.
12. Continuous evaluation for quality, drift, bias, hallucination, security and operational effectiveness.

## 4. Autonomy and reserved authority

Agents may autonomously perform authorised research, analysis, drafting, internal coordination, code changes and tests within approved environments. Autonomy does not confer approval authority.

Production deployment, destructive data changes, financial commitments, purchases, external legal/regulatory submissions, binding representations, physical actuation, safety-critical control and product/quality release require applicable explicit human, statutory, professional and change-control approvals. Agents must never impersonate approvers or manufacture approval evidence.

## 5. Lifecycle application

The directive applies throughout discovery, context, evidence, compliance, feasibility, validation, design, engineering, testing, approval, certification, deployment, operation, monitoring, measurement and continuous assurance. Reassess the swarm architecture after material changes in scope, risk, data, models, integrations or operating conditions.

## 6. Required evidence and acceptance

Maintain a versioned swarm register containing:
- Agent/role inventory, owner, purpose, tools and permission boundary.
- Orchestration and task/data-flow architecture.
- Human approval and escalation matrix.
- Security, safety, privacy and compliance threat assessment.
- Tests and measured results for normal, adversarial, failure and recovery conditions.
- Independent verification evidence and unresolved defects.
- Cost/resource and availability assessment.
- Monitoring, incident, fallback and change-control runbooks.
- TRL/readiness assessment for technology-bearing swarm components and the integrated system, where applicable.

A proposal, architecture diagram or demo is not an implemented or operational swarm. State status truthfully and support claims with evidence. No project may claim SHAKTI conformance or pass a relevant readiness/release gate while this mandatory architecture or its applicable controls are absent or unverified.

**Principal rule:** ONE SHAKTI STANDARD. MANY PROJECT-SPECIFIC OPERATING SYSTEMS. MANDATORY COORDINATED AGENTIC AI SWARMS THROUGHOUT.
