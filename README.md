# CAT Operator Shift Twin 🚜⚡

> **An Intelligent In-Cab Companion for Heavy Equipment Operators**  
> *Developed for the Caterpillar Hackathon 2026*

---

## 1. Problem Statement

Heavy machine operations across construction, mining, quarrying, and civil infrastructure require continuous vigilance, split-second decision-making, and strict safety compliance under extreme operational friction.

Current machine interfaces are fragmented:
- Telemetry gauges provide raw data without operational context.
- Safety buzzers alert operators after a proximity envelope or seatbelt violation has already occurred.
- Task allocations remain static checklists disconnected from real-time weather and mechanical fatigue.
- Post-shift debriefs arrive hours too late to prevent delays, fuel wastage, or unsafe operation habits.

Machine operators do not need another disconnected dashboard with five tabs. **They need an intelligent companion inside the cab that understands their entire shift in real time.**

---

## 2. Product Vision: CAT Operator Shift Twin

The **CAT Operator Shift Twin** is a living digital companion that runs alongside the operator throughout their shift.

By ingesting continuous multi-modal telemetry from the machine, the operator, the site environment, and scheduled assignments, the Shift Twin maintains an up-to-the-second 7-dimensional representation of:
- **Machine State** (RPM, hydraulic pressure, fuel consumption, diagnostics)
- **Operator State** (seatbelt compliance, fatigue level, shift hours)
- **Current Task** (target volumes, material type, site sector)
- **Environment** (weather, ground saturation, terrain grade friction)
- **Safety State** (proximity warning levels, active zone restrictions)
- **Behaviour State** (idle percentage, swing cycle consistency, maneuver roughness)
- **Productivity State** (pace vs target, cycle completion rate, delay attribution)

From this fused representation, the platform generates proactive **Next-Best-Action recommendations**, **probabilistic task forecasts**, **what-if shift simulations**, **similar-shift benchmarks**, and **closed-loop personalized training recommendations**.

---

## 3. Mandatory Requirements (Challenge Baseline)

The hackathon guidelines specify five foundational capabilities:

1. **Daily Task Dashboard**: Visual tracking of shift tasks, targets, and operational priorities.
2. **Real-Time Safety Features**: Seatbelt compliance tracking, proximity hazard alert envelopes, and audit incident logging.
3. **Operator Training Hub**: Interactive learning modules, simulator scenarios, and mastery tracking.
4. **Detection of Unusual Machine & Operator Behaviour**: Identification of excessive idling, aggressive maneuvers, and unsafe operational patterns.
5. **Task-Time Estimation**: Historical and environment-adjusted task ETA forecasting.

---

## 4. Product Differentiation: The Context / Shift Twin Layer

> ### 💡 Core Innovation Principle
> **"The mandatory capabilities come from the challenge. The Shift Twin / context intelligence layer is our product-level differentiation, not merely connecting five separate pages."**

Generic submissions deliver five disconnected pages linked by a navigation bar. The **CAT Operator Shift Twin** links these domains into a closed loop:

```
Telemetry & Safety Signals
           ↓
+-------------------------------------------------------------+
|               CAT OPERATOR SHIFT TWIN ENGINE                |
|  (Machine + Operator + Task + Environment + Safety +        |
|   Behaviour + Productivity)                                 |
+-------------------------------------------------------------+
    ↓                  ↓                   ↓                ↓
Next-Best-Action   Task Forecast       What-If Shift    Personalized
Recommendations    (Fatigue + Weather) Simulation       Training Modules
```

- When the **Safety Service** flags an unbuckled seatbelt or excessive idle loop, it does not simply record a log: it updates the **Shift Twin state**.
- The updated state recalculates the **Productivity Forecast** and triggers a contextual **Next-Best-Action** on the cab HUD.
- The **Training Service** dynamically queues a targeted 2-minute micro-simulator scenario addressing the exact observed operational issue for the operator's next scheduled break.

---

## 5. System Architecture

The platform uses a modular, decoupled microservices architecture with a unified API Gateway and logical database schema isolation.

```
                            +---------------------------------------------+
                            |          Frontend (React + Vite + TS)       |
                            |                   Port 5173                 |
                            +---------------------------------------------+
                                                   | HTTP / REST
                                                   v
                            +---------------------------------------------+
                            |            API Gateway (FastAPI)            |
                            |                   Port 8000                 |
                            +---------------------------------------------+
                                 /                 |                 \
                                /                  |                  \
                               v                   v                   v
                     +------------------+ +-----------------+ +------------------+
                     |  Safety Service  | |Operations Serv. | | Training Service |
                     |    Port 8001     | |    Port 8002    | |    Port 8003     |
                     |   (Engineer 1)   | |  (Engineer 2)   | |   (Engineer 3)   |
                     +------------------+ +-----------------+ +------------------+
                               \                   |                   /
                                \                  |                  /
                                 v                 v                 v
                     +-----------------------------------------------------------+
                     |                       PostgreSQL 16                       |
                     |                         Port 5432                         |
                     +-----------------------------------------------------------+
```

### Zero Over-Engineering Policy
- REST APIs for deterministic service communication.
- No Kafka, Kubernetes, Redis, service-mesh proxies, or vector databases.
- Maximum reliability, high demonstrability, and rapid developer velocity.

---

## 6. Three-Engineer Ownership Matrix

| Dimension | Engineer 1 | Engineer 2 | Engineer 3 |
| :--- | :--- | :--- | :--- |
| **Role** | Safety & Behavior Systems | Operations Intelligence & ML | Integration, Training & UI |
| **Codebases** | `services/safety/` | `services/operations/`<br>`data/` | `services/training/`<br>`frontend/`<br>`integration/` |
| **Git Branch** | `feature/member1-safety` | `feature/member2-operations` | `feature/member3-training-ui` |
| **Ports** | `8001` (Safety) | `8002` (Operations) | `5173` (UI), `8000` (Gateway), `8003` (Training) |
| **Scope** | Seatbelt, proximity, incidents, behavior scoring, idle detection | Task management, ETA prediction, Shift Twin context model, what-if simulator | Training hub, recommendations, cab UI, gateway routing, Docker orchestration |

### Strict No-Overlap Rule:
- Engineer 1 **never** implements ETA predictions.
- Engineer 2 **never** implements safety threshold rules.
- Engineer 3 **never** duplicates safety or ETA calculations in the frontend.
- Frontend is strictly a **consumer** of backend APIs.
- No service imports another service's private code.
- Each service owns its database schema (`safety_schema`, `operations_schema`, `training_schema`).

---

## 7. Service Port Standards

| Service | Port | Description |
| :--- | :--- | :--- |
| **Frontend** | `5173` | React 18 / Vite / Tailwind in-cab operator interface |
| **API Gateway** | `8000` | Central router & aggregator |
| **Safety Service** | `8001` | Safety compliance & behavior analytics microservice |
| **Operations Service** | `8002` | Operations intelligence & Shift Twin engine |
| **Training Service** | `8003` | Training hub & simulator microservice |
| **PostgreSQL** | `5432` | Relational database (schema per service) |

---

## 8. Local Setup & Running Services

### Prerequisites
- Python 3.12+
- Node.js 20 LTS
- Docker & Docker Compose (optional for containerized run)

### Setup Environment
```bash
# Clone the repository
git clone <repo-url>
cd catx

# Copy environment template
cp .env.example .env
```

### Running Services Independently

#### Terminal 1: Safety Service (Port 8001)
```bash
python -m pip install -r services/safety/requirements.txt
uvicorn services.safety.app.main:app --port 8001 --reload
```

#### Terminal 2: Operations Service (Port 8002)
```bash
python -m pip install -r services/operations/requirements.txt
uvicorn services.operations.app.main:app --port 8002 --reload
```

#### Terminal 3: Training Service (Port 8003)
```bash
python -m pip install -r services/training/requirements.txt
uvicorn services.training.app.main:app --port 8003 --reload
```

#### Terminal 4: API Gateway (Port 8000)
```bash
python -m pip install -r integration/gateway/requirements.txt
uvicorn integration.gateway.app.main:app --port 8000 --reload
```

#### Terminal 5: Frontend UI (Port 5173)
```bash
cd frontend
npm install
npm run dev
```

---

## 9. Docker Compose Orchestration

To run the complete ecosystem (PostgreSQL, 3 microservices, API Gateway, and Frontend UI) with a single command:

```bash
# Build and launch all containers
docker-compose up --build

# Run in background
docker-compose up -d

# Check live health status across all services
curl http://localhost:8000/api/v1/health
```

---

## 10. Testing & Verification

Run the comprehensive validation script and all pytest test suites:

```bash
# 1. Architectural & Schema Validation
python scripts/validate_repo.py

# 2. Run all backend test suites
pytest services/safety/tests/ -v
pytest services/operations/tests/ -v
pytest services/training/tests/ -v
pytest integration/gateway/tests/ -v
pytest integration/tests/ -v

# 3. Frontend type checking
cd frontend && npm run lint
```

---

## 11. Git Branching Strategy

- **`main`**: Protected, compilable, fully passing CI. Contains monorepo baseline and merged features.
- **`feature/member1-safety`**: Engineer 1's isolated workspace.
- **`feature/member2-operations`**: Engineer 2's isolated workspace.
- **`feature/member3-training-ui`**: Engineer 3's isolated workspace.

---

## 12. API Contract Overview

Complete OpenAPI documentation and JSON Schemas are specified in [`docs/API_CONTRACTS.md`](docs/API_CONTRACTS.md) and [`shared/contracts/`](shared/contracts/).

| Service | Method | Path | Summary |
| :--- | :--- | :--- | :--- |
| **Safety** | `POST` | `/api/v1/safety/telemetry` | Ingest telemetry for safety evaluation |
| **Safety** | `GET` | `/api/v1/safety/status/{operator_id}` | Real-time safety status |
| **Safety** | `GET` | `/api/v1/safety/alerts/{operator_id}` | Active safety alerts |
| **Safety** | `GET` | `/api/v1/safety/incidents/{operator_id}` | Incident audit logs |
| **Safety** | `GET` | `/api/v1/safety/behaviour/{operator_id}` | Operator behavior analysis |
| **Operations**| `GET` | `/api/v1/tasks` | List daily tasks |
| **Operations**| `GET` | `/api/v1/tasks/{task_id}` | Single task details |
| **Operations**| `POST`| `/api/v1/tasks/estimate` | Probabilistic ETA calculation |
| **Operations**| `POST`| `/api/v1/tasks/what-if` | What-if shift simulation |
| **Operations**| `GET` | `/api/v1/operator/{operator_id}/shift` | Shift context metadata |
| **Operations**| `GET` | `/api/v1/operator/{operator_id}/shift-twin` | **Canonical Shift Twin object** |
| **Operations**| `GET` | `/api/v1/tasks/{task_id}/similar-shifts` | Historical shift matches |
| **Training** | `GET` | `/api/v1/training/modules` | Training hub modules |
| **Training** | `GET` | `/api/v1/training/recommendations/{operator_id}` | Personalized recommendations |
| **Training** | `GET` | `/api/v1/training/modules/{module_id}` | Module details & simulator parameters |
| **Training** | `POST`| `/api/v1/training/attempts` | Record training simulation attempt |
| **Training** | `GET` | `/api/v1/training/progress/{operator_id}` | Cumulative progress & certificates |
| **Gateway** | `GET` | `/api/v1/health` | Downstream composite health rollup |
| **Gateway** | `POST`| `/api/v1/telemetry` | Unified telemetry fan-out ingestion |
| **Gateway** | `GET` | `/api/v1/dashboard/{operator_id}` | Composite cab dashboard payload |
| **Gateway** | `GET` | `/api/v1/shift/{operator_id}` | Synchronized Shift Twin representation |

---

## 13. Data Strategy & Governance

Detailed in [`docs/DATA_STRATEGY.md`](docs/DATA_STRATEGY.md):
- **`data/raw/`**: Untouched, immutable source challenge data.
- **`data/processed/`**: Cleaned, standardized, schema-validated datasets.
- **`data/synthetic/`**: Deterministic, physics-informed synthetic telemetry for edge cases (abrupt unbuckling, thermal runaway, proximity breaches).
- **`data/evaluation/`**: Benchmark train/val/test and edge-case validation splits.
- *Policy*: Never claim production ML accuracy from small hackathon sample data.
