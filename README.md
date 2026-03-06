# Ops Decision Layer

A decision intelligence platform that captures the *reasoning* behind operational decisions — not just the outcomes.

---

## The Problem

Companies make thousands of operational decisions daily. The outcome lands in a ticket or a dashboard. The *why* — the context, the constraints, the alternatives considered, the judgment applied — evaporates. When people leave, it goes with them.

Existing tools don't solve this. Palantir captures system state. Notion captures documentation after the fact. CRMs capture customer interactions. Nobody captures the decision-making process itself as a structured, retrievable data object.

---

## What This Is

A **decision logging layer** that sits across a company's existing operational stack.

Every time a meaningful decision gets made, the platform captures a structured record:
- The context and constraints at decision time
- The options considered and why alternatives were rejected
- The final choice and reasoning chain
- The outcome over time
- Who made it, in what role, in what domain

Decisions are captured *where they already happen* — Slack threads, Jira tickets, email chains, meeting transcripts — so there's no new workflow to adopt.

---

## Why Now

The near-term value is operational: institutional knowledge preservation, audit trails, decision consistency, onboarding acceleration.

The long-term value: structured decision corpora become training data for the next generation of enterprise agents. Whoever captures real-world operational reasoning at scale owns a data asset that can't be synthesized or replicated.

---

## Status

Early-stage. Building toward design partner validation in DevOps / incident response.

---

## Structure

```
/
├── README.md           # You are here
├── docs/               # Architecture, schema spec, integration notes
├── src/                # Core application code
│   ├── ingestion/      # Source connectors (Slack, Jira, Linear, ...)
│   ├── extraction/     # LLM-powered decision extraction pipeline
│   ├── schema/         # Decision object schema + versioning
│   ├── api/            # Backend API
│   └── ui/             # Annotation + repository interface
└── infra/              # Infrastructure config
```

---

## Decision Object Schema (v0.1)

The core data primitive. Every feature populates or queries these fields.

```json
{
  "schema_version": "0.1",
  "id": "<uuid>",
  "source": {
    "type": "slack_thread | jira_ticket | email | transcript",
    "reference": "<url or id>",
    "captured_at": "<iso8601>"
  },
  "context": {
    "situation": "<what was known at decision time>",
    "constraints": ["<constraint_1>", "..."],
    "urgency": "low | medium | high | critical"
  },
  "options_considered": [
    {
      "option": "<description>",
      "rejected_because": "<reasoning>"
    }
  ],
  "decision": {
    "choice": "<what was decided>",
    "reasoning": "<why this option>",
    "made_by": {
      "role": "<job function>",
      "domain": "<devops | procurement | finance | ...>"
    }
  },
  "outcome": {
    "status": "pending | confirmed | reversed",
    "notes": "<what actually happened>"
  },
  "annotation": {
    "reviewed": false,
    "corrections": []
  },
  "metadata": {
    "tags": [],
    "vertical": "<devops | procurement | finops | ...>"
  }
}
```

---

## Roadmap

**Phase 1 — Design Partner Sprint (0–90 days)**
- [ ] Slack ingestion + Jira ingestion
- [ ] LLM extraction pipeline (decision detection + field extraction)
- [ ] Annotation UI (confirm / correct extracted decisions)
- [ ] 3–5 design partners running on real incident data

**Phase 2 — Early Product (3–9 months)**
- [ ] Production-quality extraction pipeline
- [ ] Decision repository with search + filtering
- [ ] Outcome tracking loop
- [ ] First paying customers (DevOps vertical)

**Phase 3 — Data Asset (9–24 months)**
- [ ] Anonymization + aggregation infrastructure
- [ ] Cross-customer corpus
- [ ] Data governance model
- [ ] Lab conversations

---

## Contributing

Not open for external contributions yet. Reach out directly if you want to be a design partner.
