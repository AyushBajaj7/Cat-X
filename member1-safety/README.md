# Member 1 — Safety & Behaviour Intelligence Service

**Owner**: Engineer 1 (Senior Safety, Telemetry and Behaviour Intelligence Engineer)  
**Port**: `8001`  
**Boundary**: Safety & Behaviour Intelligence Only  
**Branch**: `feature/member1-safety`

---

## 1. Executive Summary

The **Safety & Behaviour Intelligence Service** is the real-time operational safety core of the **CAT Operator Shift Twin**. It ingests continuous machine, operator, and environmental telemetry, runs deterministic multi-factor hazard detection rules, logs auditable safety incidents with stateful lifecycle management, monitors operational behavior anomalies using unsupervised machine learning, and produces deterministic, explainable **Trajectory Constraint Signals** consumed by Engineer 2's CAT Trajectory engine to prune infeasible operational decisions.

---

## 2. Engineering Standards & Demo Assumptions Disclaimer

> **IMPORTANT DISCLAIMER**:
> 1. **Demo Assumptions**: All numeric thresholds (e.g. 5m/10m proximity buffers, 25/45-minute idle thresholds, 2.0 m/s tramming speed limit) are **heuristic demonstration assumptions** designed for hackathon evaluation and should not be construed as official Caterpillar engineering or equipment specifications.
> 2. **Synthetic Data**: Telemetry streams and demo fixtures represent synthetic simulation data for evaluation purposes.
> 3. **Anomaly Score Interpretation**: The `anomaly_score` in $[0.0, 1.0]$ emitted by the Isolation Forest engine represents a normalized index of statistical deviation from regular operating patterns. It must **NOT** be interpreted as a "probability of equipment failure".
> 4. **No Single Quality Score**: Operator behavioral trajectory is evaluated along distinct, orthogonal axes (fatigue, speed control, seatbelt compliance, and idle efficiency). No single reductive composite score is used to rank or evaluate operators.
> 5. **Idling Classification**: Stationary excessive idling is classified as **behaviour intelligence and fuel efficiency monitoring**, not an acute life-safety violation.

---

## 3. Architecture & Subsystems

```
                                  [ Telemetry Event ]
                                           │
             ┌─────────────────────────────┴─────────────────────────────┐
             ▼                                                           ▼
   [ Rules Subsystem ]                                        [ Behaviour Subsystem ]
   ├─ SeatbeltRule (Kinetic state)                            ├─ FeatureExtractor (12D vector)
   ├─ ProximityRule (4-tier envelope)                         ├─ BaselineManager (running EMA + Z-score)
   ├─ CombinedHazardRule (Compound risk)                      ├─ AnomalyEngine (IsolationForest [0,1])
   └─ IdleRule (Efficiency & fuel waste)                      └─ TrendAnalyzer (Multi-axis trends)
             │                                                           │
             ├───────────────┬───────────────────────────┐               │
             ▼               ▼                           ▼               ▼
      [ Active Alerts ] [ Incidents ]           [ Trajectory Constraints ]
      (CRITICAL/HIGH)  (Deduplication 300s)     (Prune infeasible branches)
             │         (OPEN->ACK->RESOLVED)             │               │
             └───────────────┬───────────────────────────┴───────────────┘
                             ▼
                 [ Persistence Layer ]
                 ├─ safety_events
                 ├─ safety_alerts
                 ├─ safety_incidents
                 ├─ behaviour_metrics
                 └─ behaviour_anomalies
                 (PostgreSQL primary / SQLite fallback)
```

### 3.1. Rules Engine (`app/rules/`)
- **`SeatbeltRule`**: Evaluates physical buckle status against kinetic machine states (`STOPPED`, `IDLE`, `WORKING`, `TRAMMING`) and ground speed. Unbuckled tramming (> 2.0 m/s) escalates to `CRITICAL` severity and `HIGH_RISK` state. Computes rolling seatbelt compliance percentage.
- **`ProximityRule`**: Enforces a 4-tier safety distance envelope:
  - `< 5.0m`: `CRITICAL` proximity breach (near-miss incident + immediate hold constraint).
  - `< 10.0m`: `HIGH` hazard (warning + speed restricted to 1.0 m/s).
  - `< 20.0m`: `MEDIUM` secondary buffer warning.
  - `< 30.0m`: `LOW` outer perimeter information alert.
  - `≥ 30.0m`: `NONE` (clear operational envelope).
- **`CombinedHazardRule`**: Detects correlated compound hazards (e.g. unbuckled operator inside an active proximity buffer, high-speed tramming near personnel, or unbuckled with elevated fatigue). Emits `CRITICAL` alert and requires supervisor intervention.
- **`IdleRule`**: Evaluates stationary engine runtime against 25-minute (warning) and 45-minute (critical) thresholds. Computes estimated wasted fuel in liters: $\text{Fuel Wasted (L)} = \text{idle\_minutes} \times \left(\frac{\text{fuel\_rate\_lph}}{60}\right)$.
- **`ConstraintGenerator`**: Emits explainable `ConstraintSignal` objects containing evidence and pruned trajectory branches for Engineer 2's Trajectory engine.

### 3.2. Incident Lifecycle Subsystem (`app/incidents/`)
- **Deduplication Engine**: Automatically suppresses duplicate incidents of the same `(operator_id, machine_id, incident_type)` occurring within a 300-second (5-minute) sliding window to prevent telemetry storms.
- **Audit Lifecycle**: Full state transitions:
  $$\text{OPEN} \xrightarrow{\text{acknowledge}} \text{ACKNOWLEDGED} \xrightarrow{\text{resolve}} \text{RESOLVED}$$
  Captures supervisor identity, ISO 8601 timestamps, and resolution audit notes.

### 3.3. Behaviour Intelligence Subsystem (`app/behaviour/`)
- **`FeatureExtractor`**: Extracts a 12-dimensional multivariate behavioral vector from windowed telemetry (mean/max speed, speed variance, engine RPM, fuel rate, idle ratio, fatigue, seatbelt compliance %, aggressive throttle jumps, unsafe speeds, and cycle consistency).
- **`BaselineManager`**: Maintains running exponential moving averages and standard deviations per operator. Emits `BehaviourSignal` items for statistical outliers ($|z| \ge 2.0$).
- **`AnomalyEngine`**: Leverages scikit-learn `IsolationForest` to compute a smooth normalized outlier index in $[0.0, 1.0]$. Flags operational pattern shifts without claiming mechanical failure prediction.
- **`TrendAnalyzer`**: Computes directional trajectory (`IMPROVING`, `STABLE`, `DEGRADING`) along four independent orthogonal axes: Fatigue, Speed Control, Seatbelt Compliance, and Idle Efficiency.

### 3.4. Persistence Layer (`app/database.py`, `app/db_models.py`)
- SQLAlchemy 2.0 ORM with 5 dedicated entity models:
  1. `safety_events`: Complete telemetry event audit trail.
  2. `safety_alerts`: Active and historical safety alerts.
  3. `safety_incidents`: Stateful incident audit records.
  4. `behaviour_metrics`: Aggregated behavioral snapshot indices.
  5. `behaviour_anomalies`: Multivariate operational anomaly events.
- **Resilient Engine**: Connects to primary PostgreSQL (`DATABASE_URL`), falling back to local SQLite (`sqlite:///./safety.db`) if the remote database is unavailable.

---

## 4. API Endpoints Reference

| Method | Path | Description | Schema / Contract |
|---|---|---|---|
| `POST` | `/api/v1/safety/telemetry` | Ingest real-time telemetry (supports nested & flat formats) | Returns `SafetyStatusModel` |
| `GET` | `/api/v1/safety/status/{operator_id}` | Retrieve real-time safety status, compliance %, and hazards | `safety.schema.json` |
| `GET` | `/api/v1/safety/alerts/{operator_id}` | List active alerts (optional `?severity=CRITICAL`) | `safety.schema.json` |
| `GET` | `/api/v1/safety/incidents/{operator_id}` | List incident audit logs (optional `?status=OPEN`) | `safety.schema.json` |
| `POST` | `/api/v1/safety/incidents/{incident_id}/acknowledge` | Acknowledge incident | Returns updated `IncidentModel` |
| `POST` | `/api/v1/safety/incidents/{incident_id}/resolve` | Resolve incident with supervisor notes | Returns updated `IncidentModel` |
| `GET` | `/api/v1/safety/behaviour/{operator_id}` | Retrieve behavior score, idle metrics, and anomaly flags | `behaviour.schema.json` |
| `GET` | `/api/v1/safety/constraints/{operator_id}` | Retrieve active Trajectory constraint signals | List of `ConstraintSignal` |
| `GET` | `/api/v1/health` | Service health check | Status `HEALTHY`, port `8001` |

---

## 5. Deterministic Demo Scenarios (`app/demo_fixtures.py`)

1. **`NORMAL_OPERATION`**:
   - Telemetry: Buckled seatbelt, clear proximity (42m), speed 1.5 m/s, low fatigue (18.0).
   - Outcome: `SafetyState.SAFE`, Safety score 98.0, 0 active hazards.
2. **`UNBUCKLED_TRAMMING`**:
   - Telemetry: Unbuckled operator, machine tramming at 3.2 m/s (> 2.0 m/s threshold).
   - Outcome: `CRITICAL` alert (`SEATBELT_UNBUCKLED`), audit incident logged, `HIGH_RISK` state, `OPERATOR_PAUSE` constraint pruning tramming actions.
3. **`CRITICAL_PROXIMITY`**:
   - Telemetry: Proximity distance 3.4m (< 5.0m danger envelope) in fog.
   - Outcome: `CRITICAL` alert (`PROXIMITY_HAZARD`), near-miss incident logged, `SPEED_LIMIT = 0.0 m/s` (Hold Position) constraint.
4. **`COMBINED_HAZARD`**:
   - Telemetry: Operator unbuckled AND proximity breach (7.2m < 10m) while moving at 1.8 m/s in rain.
   - Outcome: `CRITICAL` alert (`COMBINED_HAZARD`), `SUPERVISOR_INTERVENTION` constraint pruning all autonomous actions.
5. **`EXCESSIVE_IDLE`**:
   - Telemetry: 52 minutes stationary low-idle engine run (> 45 min threshold).
   - Outcome: `MEDIUM` alert (`EXCESSIVE_IDLE`), fuel waste calculation (~12.6L), `TASK_HOLD` constraint.
6. **`BEHAVIOURAL_DRIFT`**:
   - Telemetry: 15-event sequence showing escalating fatigue (30 $\to$ 88), erratic throttle spikes, and unbuckling.
   - Outcome: IsolationForest triggers `anomaly_detected = True`, normalized `anomaly_score > 0.65`, degrading trend directions on fatigue and speed control.

---

## 6. How to Run Locally

### Prerequisites
- Python 3.12+
- Dependencies installed from `requirements.txt`

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Launch Service
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```
Interactive OpenAPI documentation will be available at: `http://localhost:8001/docs`.

### Run Test Suite
```bash
python -m pytest tests/test_safety_api.py -v
```

---

## 7. Monorepo Integration & Boundaries

- **Upstream**: Ingests telemetry from field gateways or simulator pipelines.
- **Downstream Consumers**:
  - **Engineer 2 (Operations & Trajectory)**: Consumes `GET /api/v1/safety/status/{operator_id}`, `GET /api/v1/safety/behaviour/{operator_id}`, and active constraints to prune invalid alternative paths.
  - **Engineer 3 (Gateway & Cockpit UI)**: Aggregates real-time alerts, incident audit views, and operator compliance telemetry for presentation.
- **Isolation Guarantee**: Strictly zero cross-service imports. Communicates exclusively via HTTP REST conforming to contracts in `shared/contracts/`.
