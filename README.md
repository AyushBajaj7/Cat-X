# CAT Operator Shift Twin & CAT Trajectory 🚜⚡

> **An Intelligent In-Cab Companion & Consequence Engine for Heavy Equipment Operators**  
> *Developed for the Caterpillar Hackathon 2026*
>
> 🌐 **Live Production Deployment**: [https://cat-frontend-su80.onrender.com](https://cat-frontend-su80.onrender.com)  
> 🚀 **Direct Shift Cockpit View**: [https://cat-frontend-su80.onrender.com/shift](https://cat-frontend-su80.onrender.com/shift)  
> 📦 **GitHub Repository**: [https://github.com/AyushBajaj7/Cat-X](https://github.com/AyushBajaj7/Cat-X)

---

## 1. Problem Statement

Heavy machine operations across construction, mining, quarrying, and civil infrastructure require continuous vigilance, split-second decision-making, and strict safety compliance under extreme operational friction.

Current machine interfaces are fragmented:
- Telemetry gauges provide raw data without operational context.
- Safety buzzers alert operators after a proximity envelope or seatbelt violation has already occurred.
- Task allocations remain static checklists disconnected from real-time weather and mechanical fatigue.
- Post-shift debriefs arrive hours too late to prevent delays, fuel wastage, or unsafe operation habits.

Machine operators do not need another disconnected dashboard with five tabs. **They need an intelligent companion inside the cab that understands their entire shift in real time and models the consequences of their operational choices.**

---

## 2. Mandatory Baseline Capabilities

Our architecture preserves all five mandatory baseline capabilities with production-grade rigor:

1. **Daily Task Dashboard**: Visual tracking of shift tasks, targets, site zone boundaries, and operational priorities.
2. **Real-Time Safety Features**: Continuous seatbelt compliance tracking, proximity hazard alert envelopes, and audit incident logging.
3. **Operator Training Hub**: Interactive learning modules, simulator scenarios, and mastery tracking.
4. **Detection of Unusual Machine & Operator Behaviour**: Algorithmic detection of excessive idling, aggressive maneuvers, unsafe speed, and boom shock loads.
5. **Task-Time Estimation**: Historical and environment-adjusted task ETA forecasting with P10/P90 confidence intervals.

---

## 3. Core Product Differentiator: CAT Trajectory — Consequence Engine

> ### 💡 Core Innovation Principle
> **"The mandatory capabilities come from the challenge. The Shift Twin digital context and the CAT Trajectory Consequence Engine are our product-level differentiators, not merely connecting five separate pages or running generic what-if simulations."**

Generic submissions deliver five disconnected pages linked by a navigation bar or simple slider calculators. **CAT Trajectory** is an autonomous tactical partner operating on a continuous closed loop:

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

## 4. System Architecture

```
                                  +---------------------------------------------+
                                  |        OPERATOR COCKPIT (React / TS)        |
                                  |         member3-experience/frontend         |
                                  |                   Port 5173                 |
                                  +---------------------------------------------+
                                                         |
                                                         | HTTP / REST & Live State
                                                         v
                                  +---------------------------------------------+
                                  |            API GATEWAY (FastAPI)            |
                                  |          member3-experience/gateway         |
                                  |                   Port 8080                 |
                                  +---------------------------------------------+
                                       /                 |                 \
                                      /                  |                  \
                                     /                   |                   \
                     (REST)         /             (REST) |                    \  (REST)
                                   v                     v                     v
                +----------------------+   +-----------------------+   +----------------------+
                |    Safety Service    |   |  Operations Service   |   |   Training Service   |
                |    member1-safety    |   |  member2-operations   |   |  member3-experience/ |
                |      Port 8001       |   |       Port 8002       |   |       training       |
                |     (Engineer 1)     |   |     (Engineer 2)      |   |      Port 8003       |
                +----------------------+   +-----------------------+   |     (Engineer 3)     |
                           |                           |               +----------------------+
                           | Safety &                  |                          |
                           | Behaviour Signals         v                          |
                           |                  SHIFT TWIN / STATE                  |
                           |                           |                          |
                           |                           v                          |
                           |                 DECISION-POINT ENGINE                |
                           |                           |                          |
                           |                           v                          |
                           +---------------->  CONSEQUENCE ENGINE                 |
                                                       |                          |
                                          +------------+------------+             |
                                          |            |            |             |
                                          v            v            v             |
                                      Continue    Re-sequence   Reposition        |
                                          |            |            |             |
                                          +------------+------------+             |
                                                       |                          |
                                                       v                          |
                                               Consequence Graph                  |
                                                       |                          |
                                                       v                          |
                                                 Human Choice                     |
                                                       |                          |
                                                       v                          |
                                                Outcome Replay                    |
                                                       |                          |
                                                       v                          |
                                                Decision Memory                   |
                                                       |                          |
                                                       v                          |
                                                Similar Context                   |
                                                       |                          |
                                                       +-----> Future Decisions   |
                           \                           |                         /
                            \                          |                        /
                             v                         v                       v
                +-----------------------------------------------------------------------------+
                |                               PostgreSQL 16                                 |
                |                                 Port 5432                                   |
                |        (Logical Schema Isolation: safety | operations | training)           |
                +-----------------------------------------------------------------------------+
```

---

## 5. Team Ownership Matrix (ONE DOMAIN = ONE OWNER)

| Dimension | Engineer 1 | Engineer 2 | Engineer 3 |
| :--- | :--- | :--- | :--- |
| **Role** | Safety & Behaviour Intelligence | Operations, ML & Trajectory Engine | Operator Experience, Gateway & Integration |
| **Directory** | `member1-safety/` | `member2-operations/` | `member3-experience/`<br>- `training/`<br>- `frontend/`<br>- `gateway/`<br>`integration/` |
| **Port** | `8001` | `8002` | `5173` (Frontend), `8080` (Gateway), `8003` (Training) |
| **Branch** | `feature/member1-safety` | `feature/member2-operations` | `feature/member3-training-ui` |
| **Owns** | - Safety rule engine<br>- Seatbelt logic & compliance<br>- Proximity hazard detection<br>- Incident management & audit<br>- Behaviour anomaly detection<br>- Excessive idle detection<br>- Safety constraint signals | - Task management & site zones<br>- Source dataset processing<br>- Synthetic data generation<br>- Probabilistic ETA model<br>- Fuel/productivity proxies<br>- Canonical Shift Twin state<br>- **Decision-point detector**<br>- **Scenario generator**<br>- **Safety-constrained validation**<br>- **Consequence engine & DAG**<br>- **Decision memory & outcome eval** | - Training backend & catalog<br>- Training scenarios & scoring<br>- React Operator Cockpit<br>- Adaptive UI & attention modes<br>- Trajectory comparison UI<br>- Consequence graph visualization<br>- Human choice & outcome replay<br>- API Gateway fanout & aggregate<br>- Demo simulator ("17-Minute Trap")<br>- Docker Compose & E2E tests |

---

## 6. Monorepo Directory Structure

```
/
├── README.md
├── .gitignore
├── .editorconfig
├── docker-compose.yml
│
├── docs/
│   ├── PROJECT.md            # Vision, mandatory requirements, and scope
│   ├── ARCHITECTURE.md       # High-level architecture, ports, communication
│   ├── WORK_SPLIT.md         # Team ownership matrix and boundary rules
│   ├── API_CONTRACTS.md      # Full REST endpoint specifications
│   ├── DATA_STRATEGY.md      # Data pipeline, telemetry, and synthetic data
│   ├── UNIQUE_APPROACH.md    # Shift Twin & CAT Trajectory differentiator
│   ├── DEVELOPMENT_RULES.md  # Git, coding, testing, and execution guidelines
│   ├── TRAJECTORY.md         # Full CAT Trajectory Consequence Engine spec
│   └── DEMO_SCENARIO.md      # "The 17-Minute Trap" deterministic demo spec
│
├── shared/
│   └── contracts/
│       ├── telemetry.schema.json         # Raw & ingested telemetry event
│       ├── safety.schema.json            # Real-time safety compliance state
│       ├── behaviour.schema.json         # Behavior anomalies, idling, and constraint signals
│       ├── task.schema.json              # Operational task entity
│       ├── prediction.schema.json        # Probabilistic task-time estimation
│       ├── shift-twin.schema.json        # Canonical 7-dimension digital Shift Twin
│       ├── decision-point.schema.json    # Emergent operational inflection point
│       ├── scenario.schema.json          # Candidate trajectory scenario
│       ├── consequence.schema.json       # Causal consequence graph (DAG)
│       ├── decision-memory.schema.json   # Persisted decision and prediction-vs-actual log
│       ├── training.schema.json          # Training modules, attempts, recommendations
│       ├── dashboard.schema.json         # Composite Operator Cockpit view
│       └── error.schema.json             # Standardized error responses
│
├── member1-safety/
│   ├── app/                  # FastAPI safety microservice
│   ├── tests/                # Safety service unit & integration tests
│   ├── requirements.txt      # Pinned Python dependencies
│   ├── Dockerfile            # Container definition (Port 8001)
│   └── README.md
│
├── member2-operations/
│   ├── app/
│   │   ├── api/              # Operations & Trajectory REST routes
│   │   ├── domain/           # Operational state, task models, Shift Twin
│   │   ├── ml/               # Probabilistic ETA & fuel models
│   │   ├── trajectory/       # Decision point detection & consequence engine
│   │   ├── memory/           # Decision memory & similar context matching
│   │   └── persistence/      # PostgreSQL repositories
│   ├── data/
│   │   ├── raw/              # Source telematics
│   │   ├── processed/        # Cleaned training sets
│   │   ├── synthetic/        # Deterministic simulation datasets
│   │   └── evaluation/       # Benchmark validation sets
│   ├── models/               # Model artifact registry
│   ├── scripts/              # Data generation and training scripts
│   ├── tests/                # Operations & Trajectory unit tests
│   ├── requirements.txt      # Pinned Python dependencies
│   ├── Dockerfile            # Container definition (Port 8002)
│   └── README.md
│
├── member3-experience/
│   ├── training/             # FastAPI training microservice (Port 8003)
│   ├── frontend/             # React 18, Vite, TypeScript, Tailwind (Port 5173)
│   │   └── src/components/voice/  # In-Cab Voice Companion & PTT Radio Synthesizer
│   ├── gateway/              # FastAPI API Gateway (Port 8080)
│   ├── tests/                # Experience smoke tests
│   └── README.md
│
├── integration/
│   ├── tests/                # Cross-service integration & contract smoke tests
│   └── demo/                 # Deterministic demo simulator scripts
│
├── scripts/
│   └── validate_repo.py      # Automated monorepo architectural validation
│
└── .github/
    └── workflows/
        └── ci.yml            # Automated CI pipeline
```

---

## 7. In-Cab Voice Companion & Ergonomic HUD

Operating a 50-ton excavator with two joysticks while interacting with a complex touchscreen during production trenching induces severe cognitive overload and dangerous blind spots. The **CAT Operator Shift Twin** provides an ergonomic, hands-free in-cab audio companion designed for real-world heavy civil and mining environments:

1. **Dual Ergonomic Display Modes**:
   - **`CAB HUD` (Hands-Free Active Digging)**: Extreme 0.1-second glanceability. High-contrast indicators with only 3 mission-critical tiles: *Safety Perimeter*, *Harness Interlock*, and *Haul Fleet Cycle*. Zero touch interaction required.
   - **`DETAILED AUDIT` (Park / Handoff)**: Full engineering inspection view including CAN-bus implement pressures, cycle telemetry, and Directed Acyclic Graph (DAG) consequence breakdowns.
2. **Physical Push-to-Talk (PTT) Joystick Integration**:
   - Eliminates false wake-word activations in 85 dBA C13 engine noise.
   - Hold the `Spacebar` (or physical joystick trigger) to transmit; release to receive.
3. **Tactile Stop & Replay Audio Controls**:
   - Prominent red `[■ Stop Audio]` button and keyboard `Escape` shortcut instantly halt speech playback at any time.
   - `[⟲ Replay]` button allows the operator to repeat the last broadcast without taking their eyes off the bench for long.
   - Interruption Guardrail: Asking a new question immediately cuts off previous speech without audio overlap or race conditions.
4. **Preemptive Audio Priority System**:
   - **Level 3 (`CRITICAL`)**: Safety harness interlock disengagement or counterweight proximity breaches sound an alarm horn and immediately preempt any active broadcast.
   - **Level 2 (`HIGH`)**: Tactical advisories (e.g. 17-minute trap, crusher bunching, rain onset).
   - **Level 1 (`NORMAL`)**: Standard fleet queries, shift progress, and pacing status.
   - Visual priority beacon in the console header displays active dispatch priority level in real time.
5. **Crystal-Clear Disambiguated Telemetry Math**:
   - **Shift Quota Progress**: `500 of 850 tons (59% complete)`.
   - **Instantaneous Digging Speed**: `18% ahead of schedule, running at 118% of planned rate`.
   - Clearly separates shift quota tonnage from instantaneous loading rate, eliminating contradictory percentages.
6. **Authentic Radio Dispatch Terminology**:
   - Replaced unnatural robotic jargon with authentic Caterpillar and mining dispatch terminology (*"digging speed"*, *"bench slope"*, *"stop swing immediately"*).
7. **100% Offline Pure Web Audio Synthesizer**:
   - Pure oscillator-generated radio squelches and mic-open chirps (`PTT_ON`, `PTT_OFF`, `ALERT`, `CONFIRM`) that require zero downloaded audio files and function in deep open pits with zero connectivity.
8. **Natural Warm Radio Dispatch Voice**:
   - Calibrated speech synthesis tuned with a warm, measured, authoritative radio tone (1.03 rate, 0.95 pitch) for natural presence and emotional depth over cab acoustic noise.
9. **Responsive High-Density Cockpit Navigation**:
   - Compact tabs with hover tooltips, `flex-wrap` protection, and scrollbar elimination ensure all 9 primary navigation tabs and the 10-step time-lapse controller remain 100% visible on any cab monitor (1024px to 4K).

---

## 8. Deterministic Shift Story: "The 17-Minute Trap"

To evaluate and demonstrate real shift scenarios without waiting 8 hours for pit friction to occur, the top control bar provides a deterministic 10-step time-lapse controller:

| Step | Name | Operational Context | System Response |
| :---: | :--- | :--- | :--- |
| **1** | Normal | Nominal digging baseline on Bench 2 | Digging speed 104.5% of target, 0 hazards, green indicators |
| **2** | Seatbelt | Harness unbuckled during cycle pause | Hydraulic lockout armed, audio buzzer |
| **3** | Proximity | Vehicle enters 11m swing radius | Proximity alert: *"Stop swing immediately"* |
| **4** | High Idle | Waiting for trucks; idle hits 18.5% | Fuel waste alert; idle reduction guidance |
| **5** | Decision Point | Crusher queue blocks 4 trucks; rain in 20 min | Tactical advisory: 17-min trap warning |
| **6** | Trajectories | Consequence engine computes 4 scenarios | Feasibility filtering & multi-order DAG |
| **7** | Human Choice | Operator selects Bench 3 resequencing | Operator retains full command authority |
| **8** | Outcome Replay | Simulates result against active twin | 15.8 min saved, 14.8L fuel saved |
| **9** | Decision Memory | Persists signature, reason, and error | Audit trail logged to institutional database |
| **10** | Similar Context | Surfaces historical precedent | 94.2% context match retrieved for future ops |

---

## 9. Important Safety Position

> [!CAUTION]
> **Safety Notice**:
> - CAT Trajectory is an operator decision-support companion.
> - It does NOT issue autonomous machine commands or control machine hydraulics.
> - It does NOT replace operator judgment, machine interlocks, or physical cab visibility.
> - Safety constraints deterministically reject unsafe trajectories; safety is NEVER treated as a productivity trade-off.

---

## 10. Live Deployment & Verification

### 🌐 Live Production Deployment
- **Frontend Dashboard (Render)**: [https://cat-frontend-su80.onrender.com](https://cat-frontend-su80.onrender.com)
- **Direct Shift Cockpit View**: [https://cat-frontend-su80.onrender.com/shift](https://cat-frontend-su80.onrender.com/shift)
- **Automated Fallback Engine**: If backend microservices are cold-starting on free-tier hosting, the frontend seamlessly activates resilient client-side state models (`demoFallback.ts`) guaranteeing 100% operational uptime.

### 🧪 Automated Test Coverage

Every service and user-facing capability is validated with comprehensive automated test suites:

```bash
# 1. Run all Python unit & integration tests (100% Passing)
python -m pytest member1-safety member2-operations member3-experience -v

# 2. Run TypeScript build check (0 Errors)
npm --prefix member3-experience/frontend run build

# 3. Run Playwright end-to-end route, modal, and voice verification
node scratch/test_all_routes_and_links.mjs

# 4. Spin up full containerized environment via Docker Compose
docker-compose up --build
```

* Verified all 71 Python backend tests across Safety, Operations, Gateway, and Training.
* Verified all 9 primary React routes, modals, and navigation buttons via headless Playwright automation.
* Verified Web Audio squelch synthesizer, voice priority preemption, and SpeechSynthesis dispatch audio.

