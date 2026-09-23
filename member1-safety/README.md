# Member 1 — Safety & Behaviour Intelligence Service

**Owner**: Engineer 1  
**Port**: `8001`  
**Boundary**: Safety & Behaviour Intelligence Only

## Scope & Responsibilities
- Real-time safety compliance evaluation (seatbelt, speed, operating envelopes)
- Proximity hazard monitoring and zone-intrusion alert dispatch
- Operator behaviour anomaly detection (excessive idling, abrupt maneuvers, unsafe speed)
- Incident audit logging and safety event persistence
- **Safety Constraint Signals**: Generates deterministic constraint signals consumed by Engineer 2's Trajectory Consequence Engine to evaluate scenario feasibility.

## Prohibitions
- Does NOT model task scheduling, fleet ETA, or productivity metrics (Owned by Engineer 2).
- Does NOT serve the operator frontend or cockpit UI (Owned by Engineer 3).
