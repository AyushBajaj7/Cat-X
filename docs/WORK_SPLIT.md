# Work Split & Team Ownership Matrix

## 1. Overview & Core Philosophy

To maximize velocity during the Caterpillar Hackathon and eliminate merge collisions, code duplication, and architectural drift, the monorepo enforces a strict **ONE DOMAIN = ONE OWNER** boundary rule.

- **Engineer 1** produces safety, behaviour, and physical constraint signals.
- **Engineer 2** consumes those signals and owns all operational intelligence, ML models, the canonical Shift Twin, and the CAT Trajectory Consequence Engine.
- **Engineer 3** consumes backend intelligence to create the operator experience across the cab cockpit, training hub, API gateway, and demo simulation.

The frontend **NEVER** calculates safety thresholds, anomaly scores, ETAs, fuel consumption, consequence graphs, or attention modes. The API Gateway **NEVER** acts as a secondary intelligence engine.

---

## 2. Engineer Ownership Matrix

| Dimension | Engineer 1 | Engineer 2 | Engineer 3 |
| :--- | :--- | :--- | :--- |
| **Name / Role** | Safety & Behaviour Intelligence | Operations Intelligence, ML & Trajectory | Operator Experience, Gateway & Integration |
| **Codebases Owned** | `member1-safety/` | `member2-operations/` | `member3-experience/`<br>- `training/`<br>- `frontend/`<br>- `gateway/`<br>`integration/` |
| **Ports Owned** | `8001` (Safety) | `8002` (Operations) | `5173` (Frontend)<br>`8080` (Gateway)<br>`8003` (Training) |
| **Core Responsibilities** | - Safety rule engine<br>- Seatbelt logic & compliance<br>- Proximity hazard detection<br>- Incident management & audit<br>- Behaviour anomaly detection<br>- Excessive idle detection<br>- Unsafe speed & swing signals<br>- **Safety constraint signals** consumed by Trajectory | - Task management & site zones<br>- Source dataset processing<br>- Synthetic data generation<br>- Probabilistic ETA model (P10/P90)<br>- Fuel/productivity proxy models<br>- Canonical Shift Twin state<br>- **Decision-point detector**<br>- **Candidate scenario generator**<br>- **Safety-constrained validation**<br>- **Consequence engine & DAG**<br>- What-if counterfactual engine<br>- Shift forecast & similar shifts<br>- **Decision memory & outcome eval**<br>- Next-best-action logic & trace | - Training backend & catalog<br>- Training scenarios & scoring<br>- Training history & certifications<br>- React Operator Cockpit<br>- Adaptive UI & attention modes<br>- Decision-point prompt UI<br>- Trajectory comparison UI<br>- Consequence graph visualization<br>- Human choice & outcome replay<br>- Decision memory exploration<br>- API Gateway fanout & aggregation<br>- Demo simulator ("17-Minute Trap")<br>- Docker Compose & E2E tests |

---

## 3. Strict Non-Responsibilities & No-Overlap Rule

### Engineer 1 (Safety):
- **MUST NEVER** model task scheduling, ETA, fuel consumption, or fleet queues (Owned by Engineer 2).
- **MUST NEVER** generate candidate operational trajectories or consequence graphs (Owned by Engineer 2).
- **MUST NEVER** implement training module workflows or UI components (Owned by Engineer 3).
- **MUST NEVER** access or modify tables in `operations_schema` or `training_schema`.

### Engineer 2 (Operations & Trajectory):
- **MUST NEVER** invent safety thresholds or override safety violation records (Owned by Engineer 1).
- **MUST NEVER** render UI components or visualize graphs in React (Owned by Engineer 3).
- **MUST NEVER** implement training attempt scoring or module catalogs (Owned by Engineer 3).
- **MUST NEVER** access or modify tables in `safety_schema` or `training_schema`.

### Engineer 3 (Experience, Gateway & Integration):
- **MUST NEVER** calculate safety thresholds, proximity margins, or seatbelt compliance in the frontend or gateway.
- **MUST NEVER** compute ETAs, fuel burn predictions, or scenario consequences in the frontend or gateway.
- **MUST NEVER** determine the `attention_mode` in the frontend (it is strictly derived by Engineer 2's backend intelligence).
- The frontend is strictly a **presentation consumer** of Gateway and service REST endpoints.

---

## 4. Handover Contracts & Inter-Service Dependencies

```
[ Engineer 1: Safety Service ]
       │
       │ (SafetyStatus, BehaviourAnalysis & Constraint Signals)
       ▼
[ Engineer 2: Operations & Trajectory Service ]
       │
       │ (ShiftTwin, DecisionPoint, Scenarios, ConsequenceGraph, DecisionMemory)
       ▼
[ Engineer 3: API Gateway & Operator Cockpit ]
       │
       │ (Composed Dashboard, Cockpit Rendering, Adaptive Focus Modes)
       ▼
  Operator (Human-in-the-Loop Choice)
```

### Handover Contract 1: Safety -> Operations / Trajectory
- **Endpoints**: `GET /api/v1/safety/status/{operator_id}`, `GET /api/v1/safety/behaviour/{operator_id}`
- **Schemas**: `shared/contracts/safety.schema.json`, `shared/contracts/behaviour.schema.json`
- **Data Provided**: Proximity hazard count, seatbelt status, fatigue score, excessive idling metrics, aggressive maneuver flags, and deterministic `constraint_flags`.
- **Usage**: Engineer 2 uses these signals to validate candidate trajectories. If a trajectory breaches a safety constraint, its status is marked `REJECTED`.

### Handover Contract 2: Safety & Operations -> Training
- **Endpoints**: `GET /api/v1/safety/behaviour/{operator_id}`, `GET /api/v1/operator/{operator_id}/shift-twin`
- **Usage**: Engineer 3 consumes behavioral flags (e.g., `excessive_idling_flag`, `boom_shock_detected`) to dynamically serve personalized training recommendations via `GET /api/v1/training/recommendations/{operator_id}`.

### Handover Contract 3: Operations & Trajectory -> Gateway / Cockpit
- **Endpoints**: 
  - `GET /api/v1/operator/{operator_id}/shift-twin`
  - `GET /api/v1/trajectory/current/{operator_id}`
  - `POST /api/v1/trajectory/evaluate`
  - `POST /api/v1/trajectory/choose`
  - `GET /api/v1/trajectory/memory/{operator_id}`
- **Schemas**: `shared/contracts/shift-twin.schema.json`, `shared/contracts/decision-point.schema.json`, `shared/contracts/scenario.schema.json`, `shared/contracts/consequence.schema.json`, `shared/contracts/decision-memory.schema.json`
- **Usage**: Engineer 3 exposes these endpoints through the API Gateway on Port `8080` and visualizes them on the Operator Cockpit interface.

---

## 5. Conflict Resolution & Branching Rules

1. **Shared Contracts Freeze**: Any modification to `shared/contracts/*.schema.json` requires explicit review and agreement among all three engineers before changes are made.
2. **Feature Branching**:
   - `git checkout feature/member1-safety` for Engineer 1.
   - `git checkout feature/member2-operations` for Engineer 2.
   - `git checkout feature/member3-training-ui` for Engineer 3.
3. **Continuous Integration**: PRs must pass automated syntax, schema validation, import boundary checks, and pytest suites.
