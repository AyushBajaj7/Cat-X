# Work Split & Team Ownership Matrix

## 1. Overview & Core Philosophy

To maximize velocity during the hackathon and eliminate merge collisions, code duplication, and architectural drift, the CAT Operator Shift Twin monorepo is divided strictly among three engineers.

Each engineer has total end-to-end ownership of their service boundaries, including:
- Data modeling and database tables
- Business logic algorithms
- REST API implementation
- Unit and integration tests
- Dockerfile maintenance

---

## 2. Engineer Ownership Matrix

| Dimension | Engineer 1 | Engineer 2 | Engineer 3 |
| :--- | :--- | :--- | :--- |
| **Name / Role** | Safety & Behavior Engineer | Operations Intelligence & ML Engineer | Integration, Training & UI Engineer |
| **Codebases Owned** | `services/safety/` | `services/operations/`<br>`data/` | `services/training/`<br>`frontend/`<br>`integration/` |
| **Git Feature Branch**| `feature/member1-safety` | `feature/member2-operations` | `feature/member3-training-ui` |
| **Port Owned** | `8001` (Safety) | `8002` (Operations) | `5173` (Frontend)<br>`8000` (Gateway)<br>`8003` (Training) |
| **Core Responsibilities** | - Seatbelt compliance engine<br>- Proximity hazard detection<br>- Real-time safety alerting<br>- Incident logging & audit<br>- Unusual behavior detection<br>- Excessive idling calculation<br>- Unsafe operation scoring<br>- Safety status REST API | - Daily task management<br>- Dataset preprocessing<br>- Synthetic dataset expansion<br>- ML ETA prediction model<br>- Model evaluation & metrics<br>- **Shift Twin Context Engine**<br>- Similar-shift retrieval<br>- What-if shift simulation<br>- Productivity analytics | - Training Hub modules<br>- Module recommendation consumer<br>- Training simulator & scoring<br>- React + Vite cab UI<br>- API Gateway routing & aggregation<br>- End-to-end integration tests<br>- Docker orchestration |

---

## 3. Strict Non-Responsibilities & No-Overlap Rule

To maintain clean architectural boundaries:

### Engineer 1 (Safety):
- **MUST NEVER** implement task scheduling, ETA prediction, or what-if simulation.
- **MUST NEVER** implement training module workflows.
- **MUST NEVER** access or alter tables in `operations_schema` or `training_schema`.

### Engineer 2 (Operations):
- **MUST NEVER** implement safety hazard threshold evaluation or seatbelt rules.
- **MUST NEVER** implement training attempt scoring.
- **MUST NEVER** access or alter tables in `safety_schema` or `training_schema`.

### Engineer 3 (Training & Frontend):
- **MUST NEVER** duplicate safety, behavior, or ETA calculations inside the React frontend.
- **MUST NEVER** implement raw safety rules inside the API Gateway.
- The frontend is strictly a **consumer** of gateway and service APIs.
- Any calculated field (e.g. ETA, risk score, recommended action) must originate from the authoritative backend service.

---

## 4. Handover Contracts & Inter-Service Dependencies

```
[ Engineer 1: Safety Service ]
       | (Produces SafetyStatus & BehaviorAnalysis)
       v
[ Engineer 2: Operations Service ]
       | (Ingests Safety & Telemetry to compute Shift Twin)
       v
[ Engineer 3: API Gateway & Frontend ]
       | (Fetches Shift Twin, Dashboard, Training & Displays to Operator)
```

### Handover Contract 1: Safety -> Operations
- **Endpoint**: `GET /api/v1/safety/status/{operator_id}`
- **Schema**: `shared/contracts/safety.schema.json`
- **Data Provided**: Proximity alert count, seatbelt status, current behavior score, active hazard list.
- **Usage**: Engineer 2 incorporates these metrics directly into the `ShiftTwin.safety` and `ShiftTwin.behaviour` state blocks.

### Handover Contract 2: Safety & Operations -> Training
- **Endpoint**: `GET /api/v1/safety/behaviour/{operator_id}`
- **Schema**: `shared/contracts/safety.schema.json`
- **Usage**: Engineer 3 consumes behavior flags (e.g., `excessive_idling_flag`, `harsh_swing_detected`) to dynamically suggest personalized training modules via `GET /api/v1/training/recommendations/{operator_id}`.

### Handover Contract 3: Operations -> Gateway / Frontend
- **Endpoint**: `GET /api/v1/operator/{operator_id}/shift-twin`
- **Schema**: `shared/contracts/shift-twin.schema.json`
- **Usage**: Engineer 3 exposes this via the Gateway `GET /api/v1/dashboard/{operator_id}` and renders the living digital twin widget on the cab screen.

---

## 5. Conflict Resolution & Branching Rules

1. **Shared Contracts are Frozen during Sprint Start**: Any modification to `shared/contracts/*.schema.json` requires explicit review and agreement among all three engineers before changes are made.
2. **Independent Branches**:
   - `git checkout feature/member1-safety` for Engineer 1.
   - `git checkout feature/member2-operations` for Engineer 2.
   - `git checkout feature/member3-training-ui` for Engineer 3.
3. **No Direct Commits to Main**: All code is developed on feature branches and merged into `main` via Pull Requests with all CI checks passing.
