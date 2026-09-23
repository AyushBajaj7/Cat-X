# Project Overview: CAT Operator Shift Twin & CAT Trajectory

## 1. Executive Summary & Problem Statement

Heavy machine operations across construction, quarrying, and mining environments involve extreme operational pressures, hazardous proximity risks, fluctuating site and weather conditions, and strict production schedules. Machine operators navigate continuous cognitive demands while balancing safety protocols with productivity targets.

Conventional cab systems provide fragmented instrumentation: disconnected telematics, audible alarms without context, static task checklists, and post-shift debrief reports delivered hours after mistakes occurred. Operators lack an integrated, proactive partner inside the cab that understands the whole picture of their shift as it unfolds.

**The Caterpillar hackathon challenges us to build a multi-functional operator interface and explicitly urges us to go beyond a passive tool to create an intelligent companion.**

---

## 2. Mandatory Baseline Capabilities

The hackathon defines five mandatory capabilities that serve as our operational foundation and are strictly preserved:

1. **Daily Task Dashboard**: Clear overview of scheduled, in-progress, and completed tasks with operational metadata.
2. **Real-Time Safety Features**: Continuous seatbelt compliance tracking, proximity hazard alert triggers, and structured incident logging.
3. **Operator Training Hub**: Interactive modules for pre-shift prep, micro-learning, and skill certification.
4. **Unusual Machine & Operator Behavior Detection**: Automated identification of excessive idling, aggressive maneuvers, unsafe speed, and irregular operating cycles.
5. **Task-Time Estimation**: Probabilistic task completion forecasting using historical baseline data combined with environmental adjustments.

---

## 3. Product-Level Differentiator: CAT Trajectory — Consequence Engine

> **Critical Architecture Principle**:
> *"The mandatory capabilities come from the challenge. The CAT Trajectory Consequence Engine and canonical Shift Twin represent our true product-level innovation—not merely connecting five separate pages or running generic what-if simulations."*

### The CAT Trajectory Closed Loop:
Rather than offering passive retrospective charts or manual what-if sliders, CAT Trajectory acts as an active tactical partner:

```
OBSERVE
  │  (Real-time Telemetry & Site Conditions)
  ▼
DETECT DECISION POINT
  │  (Algorithmically identifies tactical inflection points: queues, delays, weather)
  ▼
GENERATE ALTERNATIVES
  │  (Generates candidate paths: Continue | Re-sequence | Reposition)
  ▼
APPLY SAFETY CONSTRAINTS
  │  (Deterministic validation: rejects options violating slope or proximity limits)
  ▼
PREDICT CONSEQUENCES
  │  (Quantifies multi-order effects: ETA drift, fuel burn, safety risk)
  ▼
EXPLAIN CONSEQUENCE CHAIN
  │  (Visualizes Directed Acyclic Graph: Decision ➔ Effect ➔ Outcome)
  ▼
OPERATOR CHOOSES
  │  (Human-in-the-loop tactical decision without autonomous override)
  ▼
SIMULATE / REPLAY OUTCOME
  │  (Executes trajectory against active Shift Twin state)
  ▼
RECORD DECISION
  │  (Stores context signature, choice, and operator rationale in Decision Memory)
  ▼
COMPARE PREDICTED VS ACTUAL
  │  (Audits real-world results post-shift to evaluate model drift)
  ▼
REUSE DECISION MEMORY
     (Retrieves past successful choices when similar contexts recur)
```

---

## 4. Architectural Boundaries & Safety Positioning

- **Advisory Prototype**: CAT Trajectory provides intelligent decision support. It does not issue autonomous machine control commands or override machine interlocks.
- **Safety First**: Safety constraints reject unsafe trajectories; safety is never treated as a productivity trade-off.
- **Modularity**: Strict ownership isolation across 3 engineers (`member1-safety`, `member2-operations`, `member3-experience`).
- **No Leaky Intelligence**: The frontend strictly renders; the gateway strictly routes and aggregates. All calculations reside in authoritative backend domains.
