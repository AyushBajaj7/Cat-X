# Member 3 — Operator Experience, Training Hub & Monorepo Integration

**Owner**: Engineer 3 (Senior Product, Frontend, Training & Integration Engineer)  
**Ports**: Frontend (`5173`), API Gateway (`8080`), Training Service (`8003`), Operations (`8002`), Safety (`8001`), Postgres (`5432`)  
**Monorepo Boundary**: `member3-experience/` (Frontend, Gateway, Training), `integration/` (E2E Tests), and root `docker-compose.yml`.

---

## 1. Product Mission & Vision

The **CAT Operator Shift Twin** transforms real-time excavator telemetry and operational context into an intelligent, adaptive cab companion. Rather than an administrative dashboard or a compliance monitor, it acts as a human-centered co-pilot that answers the single most important operator question:

> **"Here is what matters to me right now during this shift."**

### Core Differentiator: CAT Trajectory Consequence Engine
When an emergent bottleneck or operational disturbance arises (e.g., "The 17-Minute Trap"), the system does not dictate commands to the machine. Instead, it guides the human operator through an intuitive tactical sequence:
1. **Current Operational State**: Real-time context synthesized across safety, machine telemetry, weather friction, and hauler arrival rates.
2. **Tactical Decision Point**: Early alert identifying impending queue delay before passive overrun occurs.
3. **Alternative Trajectories**: Three viable candidate scenarios (`Continue`, `Resequence`, `Reposition`) plus automated rejection of infeasible options violating geotechnical constraints.
4. **Consequence Graph (DAG)**: Visual multi-order causal effect modeling (`Queue Impact` → `Idle Escalation` → `Productivity Drop` → `Shift Delay`).
5. **Human Decision Commit**: Operator commits trajectory with contextual rationale (`schedule`, `safety concern`, `experience`, `equipment`).
6. **Simulated Outcome Replay**: Transparent predicted vs. actual outcome comparison with prediction error audit.
7. **Decision Memory**: Persisted contextual records accessible for future operational shifts.
8. **Similar Context Reuse**: Automatic surfacing of past proven trajectories with verified savings when similar conditions recur.

---

## 2. Five Mandatory Challenge Capabilities

1. **Daily Task Dashboard**: Assignment tracking, material tonnage volume progress, and probabilistic task-time estimation.
2. **Real-Time Safety Audit**: Seatbelt compliance streak tracking, proximity hazard triggers, and geotechnical slope warnings.
3. **Operator Training Hub**: Contextual micro-learning modules triggered directly by operating signals, with deterministic scoring.
4. **Behavior Analytics**: Excessive idle detection (>12%), maneuver smoothness, and cycle consistency score.
5. **Task-Time Estimation**: Machine learning regression forecasting remaining minutes with confidence intervals and weather friction deltas.

---

## 3. Architecture & Monorepo Structure

```
Cat-X/
├── member1-safety/            # Port 8001 (Engineer 1: Safety & Telemetry)
├── member2-operations/        # Port 8002 (Engineer 2: Task Time & Trajectory Math)
├── member3-experience/        # Engineer 3 Ownership
│   ├── frontend/              # Port 5173 (React, Vite, Tailwind, Lucide, Vitest)
│   │   ├── src/
│   │   │   ├── components/    # Modular Cab Screens, Modals, & Consequence Graph
│   │   │   ├── pages/         # What-If Simulator & Parameter Exploration
│   │   │   ├── api/client.ts  # Zero-math typed API Gateway client
│   │   │   └── types/         # TypeScript contracts matching shared JSON schemas
│   ├── gateway/               # Port 8080 (FastAPI Reverse Proxy & Demo Engine)
│   │   ├── app/
│   │   │   ├── demo.py        # 10-State 'The 17-Minute Trap' deterministic engine
│   │   │   ├── clients.py     # Resilient async HTTP client with degraded fallbacks
│   │   │   └── routes.py      # Aggregated endpoints and telemetry fan-out
│   └── training/              # Port 8003 (FastAPI Deterministic Training Microservice)
│       └── app/
│           ├── models.py      # Strict schema models (no certification pretension)
│           ├── services.py    # 4 interactive procedural modules & scoring
│           └── routes.py      # Training catalog, attempts, and progress APIs
├── integration/               # Integration Layer
│   └── tests/
│       ├── test_e2e_flow.py   # Complete verification of AC-01 through AC-20
│       └── test_integration_smoke.py
├── scripts/
│   └── validate_repo.py       # AST, schemas, port uniqueness, import isolation checks
└── docker-compose.yml         # Containerized local orchestration
```

---

## 4. Frontend Route Structure

| Route | View | Description |
| :--- | :--- | :--- |
| `/` | Shift Cockpit | Primary operational screen: 7-dimension twin, next-best-action, 5 core capabilities |
| `/shift` | Shift Cockpit | Direct alias to Shift Cockpit (with CAB HUD vs DETAILED AUDIT toggle) |
| `/trajectory` | CAT Trajectory | Decision point detection, multi-scenario comparison, consequence DAG, choice commit |
| `/tasks` | Daily Tasks | Earthmoving assignments, material targets, and probabilistic completion intervals |
| `/safety` | Real-Time Safety | Seatbelt compliance, active hazard alerts, incident logs, behavior signals |
| `/machine` | Machine Health | Engine RPM, fuel burn rates, hydraulic pressures, and cycle counts |
| `/insights` | Twin Intelligence | Canonical 7-dimension digital twin context and adaptive attention mode rationale |
| `/decisions` | Decision Memory | Historical decision audit and context signature matching (`Similar Situation Found`) |
| `/what-if` | What-If Simulator | Parameter exploration (weather, operator skill, idle reduction, machine age) |
| `/training` | Training Hub | Contextually recommended modules, catalog, and procedural proficiency tracking |
| `/training/:moduleId` | Scenario Player | Step-by-step interactive simulator with instant feedback and deterministic scoring |

### In-Cab Voice Companion & Ergonomic Cockpit
- **Dual Cockpit Ergonomics**:
  - `CAB HUD`: Hands-free high-visibility view for active digging. Only 3 glanceable indicators (Perimeter, Harness, Fleet Cycle).
  - `DETAILED AUDIT`: Comprehensive technical telemetry for shift handoffs and supervisor reviews.
- **Joystick Push-to-Talk (PTT)**: Hold `Spacebar` (or joystick trigger) to speak, eliminating false alarms from 85 dBA engine noise.
- **Pure Web Audio Synthesizer**: Oscillator-generated radio squelches and mic-open chirps (`PTT_ON`, `PTT_OFF`, `ALERT`, `CONFIRM`) with zero asset download overhead.
- **Natural Radio Voice**: Warm, measured authoritative voice (rate 1.03, pitch 0.95) with natural presence and emotional depth.
- **V2V Fleet Telemetry**: Tracks the single cab machine (`EXC-CAT-349D`) and 4 haul fleet cycle trucks, providing early bottleneck warnings before delays occur.

---

## 5. Training Service Modules

The training service implements interactive micro-learning scenarios with zero certification pretension:

1. **`SAFE_START_01` (Safe Start Check)**:
   - Identify startup conditions, confirm safety context, confirm seatbelt, check operating environment, make safe decision.
   - Triggered by: Seatbelt non-compliance signal.
2. **`PROXIMITY_RESPONSE_01` (Proximity Response)**:
   - Identify hazard, assess changing situation, choose appropriate stop/reroute response.
   - Triggered by: Proximity event in excavator swing radius.
3. **`IDLE_EFFICIENCY_01` (Idle Efficiency Response)**:
   - Identify inefficient idle, recognize truck cycle mismatch, choose operational response (eco-mode standby / throttle back).
   - Triggered by: Elevated idle percentage (>12%).
4. **`DECISION_AWARENESS_01` (Decision Awareness)**:
   - Present simplified tactical decision, compare alternatives, select trajectory, evaluate consequence graph.
   - Triggered by: Operational decision-related pattern.

---

## 6. Deterministic Demo Scenario: "The 17-Minute Trap"

The system includes a 10-state progression engine accessible via `POST /api/v1/demo/step` and reset via `POST /api/v1/demo/reset`:

- **State 1**: Normal shift baseline on Bench 2 North.
- **State 2**: Seatbelt violation detected → Attention mode transitions to `SAFETY_FOCUS`.
- **State 3**: Proximity hazard detected in swing radius → Personnel safety hold.
- **State 4**: Elevated idle (>14.5%) observed during crusher queue wait → `EFFICIENCY_FOCUS`.
- **State 5**: Tactical Decision Point Detected → `DECISION_FOCUS` triggered by 18-minute truck cycle gap & incoming rain front.
- **State 6**: Trajectory Alternatives Compared → Consequence DAG visualized; infeasible slope cut rejected.
- **State 7**: Operator Choice Committed → Trajectory B (`Resequence`) selected with reason.
- **State 8**: Outcome Replayed → Simulated actual outcome audited against prediction (error <= 1.5 mins).
- **State 9**: Decision Memory Recorded → Context signature persisted.
- **State 10**: Similar Context Reused → Past decision surfaced in future shift saving 15.8 mins.

---

## 7. Running Verification & Tests

### Python Backend & Integration Tests
```bash
# Validate AST, JSON schema contracts, port uniqueness, import isolation, and YAML
python scripts/validate_repo.py

# Run Training Microservice tests (12 tests)
pytest member3-experience/training/tests -v

# Run API Gateway tests (8 tests)
pytest member3-experience/gateway/tests -v

# Run Full End-to-End Integration Suite (AC-01 through AC-20) (22 tests)
pytest integration/tests -v
```

### Frontend Tests & Production Build
```bash
cd member3-experience/frontend

# Run Vitest component unit tests
npm test

# Verify production build and TypeScript compilation
npm run build
```

### Multi-Service Docker Compose Orchestration
```bash
# Build and run all microservices with health checks
docker compose up --build
```
Services will be accessible at:
- Frontend: `http://localhost:5173`
- API Gateway: `http://localhost:8080`
- Training Service: `http://localhost:8003`
- Operations Service: `http://localhost:8002`
- Safety Service: `http://localhost:8001`
- Postgres Database: `localhost:5432`

---

## 8. Architectural Rules Enforced

- **Zero Business Logic in Frontend / Gateway**: All safety thresholds, ETAs, consequence DAGs, and attention modes originate strictly from downstream domain microservices or the demo engine.
- **Import Isolation**: Verified via AST traversal; no microservice imports internal files from sibling service folders.
- **Degraded Mode Resilience**: If downstream services are temporarily unreachable, the Gateway serves degraded twin context gracefully with no 500 errors.
- **Strict Deterministic Evaluation**: Training scoring is deterministic based on mistakes and answers; explicitly avoids claiming operator certification.
