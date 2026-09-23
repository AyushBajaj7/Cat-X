# Member 2 — Operations Intelligence, ML, Shift Twin & CAT Trajectory 🚜🧠

> **Service**: `operations-service`  
> **Host Port**: `8002`  
> **Ownership**: Engineer 2 (Senior Data, ML, Operations Intelligence & Consequence Engineer)  
> **Domain Boundaries**: Task Management, ETA Machine Learning, Fuel/Productivity Proxies, Canonical Shift Twin, and the **CAT Trajectory Consequence Engine**.

---

## 1. System Overview & Core Philosophy

Heavy earthmoving and civil construction operations place machine operators under continuous cognitive pressure, demanding rapid tactical decisions while balancing safety limits against productivity quotas. Conventional telematics displays function as **rearview mirrors**—alerting operators only after fuel has been burned at idle, after haul truck platoons have bunched, or after shift completion handoffs have become unrecoverable.

**CAT Trajectory** is an autonomous in-cab **Consequence Engine** and tactical companion that:
1. Algorithmically detects emergent operational decision points before they become compounding traps.
2. Generates candidate alternative operational trajectories (Continue, Re-sequence, Reposition).
3. Applies deterministic safety constraints as **hard gates**—rejecting unsafe trajectories rather than treating safety as a soft productivity penalty.
4. Evaluates cascading multi-order consequences using physics-calibrated ML models.
5. Visualizes a Directed Acyclic Graph (DAG) explaining *why* outcomes diverge.
6. Empowers human-in-the-loop choice without autonomous override.
7. Logs decisions in organizational memory, audits model drift, and surfaces proven precedents when similar contexts recur.

---

## 2. Architecture & Closed-Loop Lifecycle

```
OBSERVE (Real-time Telemetry & Environment)
  │
  ▼
DETECT DECISION POINT (Inflection Point Triggers & Explainable Severity)
  │
  ▼
GENERATE ALTERNATIVES (Continue | Re-sequence | Reposition)
  │
  ▼
APPLY SAFETY CONSTRAINTS (Deterministic Hard Gates: Pass / Warning / Violated)
  │
  ▼
PREDICT CONSEQUENCES (Task ETA, Fuel Proxy, Idle Waste, Schedule Drift)
  │
  ▼
EXPLAIN CONSEQUENCE CHAIN (Directed Acyclic Graph DAG: Decision ➔ Effect ➔ Outcome)
  │
  ▼
OPERATOR CHOOSES (Non-coercive Human-in-the-Loop Tactical Selection)
  │
  ▼
SIMULATE / REPLAY OUTCOME (Simulate Outcome & Audit Prediction Error)
  │
  ▼
RECORD DECISION (Context Signature & Choice Persisted in PostgreSQL)
  │
  ▼
COMPARE PREDICTED VS ACTUAL (Model Drift Detection: actual - predicted)
  │
  ▼
REUSE DECISION MEMORY (NearestNeighbors Precedent Retrieval for Future Shifts)
```

---

## 3. Data Strategy & Dataset Governance

In compliance with `docs/DATA_STRATEGY.md`, the data pipeline enforces strict provenance:

### 3.1 Directory Governance
- `data/raw/raw_operational_tasks.csv`: Challenge reference seed dataset. **Immutable and read-only**. Explicitly labeled with `data_origin: "SOURCE"`.
- `data/processed/clean_tasks.csv`: Cleaned, schema-validated, range-bounded operational dataset.
- `data/synthetic/synthetic_tasks.csv`: Deterministically expanded operational regimes calibrated against published Caterpillar 349 Excavator, 740 GC Articulated Truck, and D8T Dozer spec sheets. Labeled with `data_origin: "SYNTHETIC"`.
- `data/evaluation/`:
  - `train.csv` (70% split)
  - `val.csv` (15% split)
  - `test.csv` (15% split)
  - `edge_cases.csv` (Targeted operational edge cases including "The 17-Minute Trap")
  - `dataset_report.json` (Comprehensive quality report)

### 3.2 Data Quality Report (`dataset_report.json`)
The pipeline runs automated validation auditing:
- Total row count & split sizes (Train=210, Val=45, Test=45, Edge=5).
- Zero missing values and zero duplicate task records.
- Range enforcement: Slope $\le 15^\circ$, payload capacity, engine loads, and cycle times.
- Categorical distributions: Task types (`EXCAVATION`, `TRENCHING`, `LOADING`, `GRADING`, `OVERBURDEN`), operator tiers (`NOVICE`, `INTERMEDIATE`, `EXPERT`, `MASTER`), and weather (`CLEAR`, `OVERCAST`, `RAIN`, `MUD`, `FOG`).

---

## 4. Feature Engineering Pipeline

The shared transformer `OperationalFeaturePipeline` in `app/ml/features.py` enforces **zero training/serving mismatch**:
- Categorical one-hot encoding for task types and weather conditions.
- Ordinal skill mapping (`NOVICE`=1.0 to `MASTER`=4.0) and visibility scores.
- Engineered features:
  - $\text{cycles\_per\_hour} = \frac{3600}{\max(10, \text{cycle\_time\_sec})}$
  - $\text{queue\_pressure} = \text{queue\_length} \times \text{truck\_arrival\_interval\_min}$
  - Terrain grade and ground saturation resistance adjustments.
- Identical transformation pipeline applied during model training, test evaluation, real-time API prediction, and counterfactual trajectory evaluations.

---

## 5. Machine Learning Models & Operational Proxies

### 5.1 Probabilistic Task ETA Model (`app/ml/eta_model.py`)
- **Baseline Heuristic**: Historical median task completion duration.
- **Candidate Models Evaluated**:
  - `MedianBaselineRegressor`: MAE = 21.35 min, $R^2 = -0.12$
  - `LinearRegression`: MAE = 17.56 min, RMSE = 33.07 min, $R^2 = 0.397$
  - `RandomForestRegressor`: MAE = 21.45 min, RMSE = 43.10 min
  - `GradientBoostingRegressor`: MAE = 18.04 min, RMSE = 41.56 min
- **Prototype Prediction Intervals**:
  - Derived empirically from individual decision tree estimators in `RandomForestRegressor`.
  - Calculates 10th percentile (`lower_minutes`) and 90th percentile (`upper_minutes`).
  - Labeled explicitly as **`prototype prediction interval`** (never claimed as formal statistical confidence intervals).

### 5.2 Fuel & Productivity Operational Proxies (`app/ml/operational_proxies.py`)
- **Fuel Consumption Proxy (`fuel_litres`)**: Ridge regressor and physics-calibrated model estimating diesel consumption across active hydraulic digging curves (~34-38 L/hr for CAT 349D at load) and high/low idle standstill (13.5 L/hr).
- **Idle Impact Proxy (`idle_minutes`)**: Models unproductive low/high idle driven by haul truck bunching and arrival intervals.
- **Productivity Proxy**: Computes productive output proxy tonnage, tons per hour, pace percentage, and efficiency ratings (`OPTIMAL`, `HIGH`, `MODERATE`, `DEGRADED`).

### 5.3 Context Similarity Engine (`app/ml/similarity.py`)
- Powered by `StandardScaler` + `NearestNeighbors(n_neighbors=5, metric='euclidean')`.
- Zero external vector database dependencies.
- Vectorizes operational context (machine age, temperature, saturation, slope, truck gap, queue length, cycle time, payload, duration, task type, weather, operator skill).
- Converts distance metrics into normalized similarity score percentages ($50\% - 99.5\%$).

---

## 6. Canonical Operational State & Shift Twin

### 6.1 Canonical Operational State (`app/domain/operational_state.py`)
A unified 13-dimension Pydantic model representing the active in-cab reality:
1. `timestamp`
2. `operator` (ID, name, experience tier, total operating hours)
3. `machine` (model, category, payload rating, operating hours, age)
4. `current_task` (target volume, completed volume, priority, scheduled duration)
5. `task_progress` (percent complete, volume remaining, elapsed minutes, pace ratio)
6. `environment` (weather, ambient temp, saturation, visibility, slope)
7. `queue_state` (queue length, truck arrival interval, trucks in transit, bottleneck severity)
8. `machine_state` (RPM, engine load, hydraulic pressure, swing angle, fuel rate)
9. `idle_state` (idle minutes, idle percentage, high idle flag, wasted fuel)
10. `productivity_state` (tons/hr, cycle time, bucket fill factor, efficiency rating)
11. `safety_signals` (seatbelt status, compliance pct, active hazards, safety score, constraint flags)
12. `behaviour_signals` (excessive idle score, aggressive maneuver count, cycle consistency, anomaly flags)
13. `prediction_state` (remaining minutes, completion time, delay probability, confidence score)

### 6.2 Canonical 7-Dimension Shift Twin (`app/domain/shift_twin.py`)
Conforms strictly to `shared/contracts/shift-twin.schema.json`. Fuses:
- `environment`, `safety`, `behaviour`, `productivity`, `prediction`
- Dynamic `shift_health_score` (0-100 composite)
- `shift_forecast` (projected completion, delay minutes, weather risk, fuel forecast)
- `attention_mode`
- `next_best_actions`
- `decision_point` & `trajectory_options`
- `decision_trace` & `similar_contexts`
- `latest_decision_memory`

---

## 7. CAT Trajectory Consequence Engine

### 7.1 Decision-Point Detector (`app/trajectory/decision_detector.py`)
Monitors the operational state for inflection points where intervention has maximum leverage:
- `QUEUE_IMBALANCE`: Truck queue length $\ge 3$ or arrival gap $\ge 12.0$ min.
- `SHIFT_DELAY_RISK`: Projected completion delay $\ge 10.0$ min past handoff.
- `EFFICIENCY_DEVIATION`: Low idle percentage $\ge 15.0\%$.
- `ENVIRONMENT_CHANGE`: Rainfall or mud ground saturation $\ge 25.0\%$.
- `SAFETY_APPROACH`: Terrain slope $\ge 12.0^\circ$ or proximity warning.
- `TASK_TRANSITION`: Milestone completion $\ge 95.0\%$.
- `UNUSUAL_OPERATING_PATTERN`: Aggressive maneuvers or cycle inconsistency.

**Explainable Severity Assignment**:
- `CRITICAL`: Safety approach or severe mechanical/proximity hazard.
- `HIGH`: Significant shift delay ($\ge 15$ min) or heavy haul queue imbalance.
- `MEDIUM`: Moderate efficiency deviation or environment transition.
- `LOW`: Routine milestone completion or nominal variance.

### 7.2 Safety Constraint Engine (`app/trajectory/safety_constraints.py`)
> [!IMPORTANT]
> **Safety is a constraint, NOT a productivity penalty.**
> We never compute `productivity - risk` as a single trade-off score. Hard constraints are evaluated first.

**Deterministic Physical Constraints**:
- `CST-SLOPE-01` (Hard): Grade stability limit $\le 15.0^\circ$ (Warning at $12.0^\circ$).
- `CST-PROXIMITY-01` (Hard): Proximity exclusion zone $\ge 10.0$m (Warning at $15.0$m).
- `CST-HIGHWALL-01` (Hard): Highwall crest setback $\ge 4.0$m (Warning at $5.5$m).
- `CST-SEATBELT-01` (Hard): Operator seatbelt compliance interlock.

**Feasibility Determination**:
- If any hard constraint is breached $\rightarrow$ **`constraint_status: REJECTED`**.
- Rejection is absolute; unsafe scenarios cannot be recommended or selected as optimal paths.

### 7.3 Trajectory Scenario Generator (`app/trajectory/scenario_generator.py`)
Generates 3 candidate trajectories via transparent transformations on cloned state:
1. **`ACT-CONTINUE` (Baseline Drift)**: Maintain current bench stance; idle continues accumulating; queue delay compounds.
2. **`ACT-RESEQUENCE` (Overburden Pre-Stripping)**: Pivot excavator immediately to pre-strip 180 tons of soft overburden on Upper Bench 3; zero idle waiting; clears truck backlog smoothly upon arrival.
3. **`ACT-REPOSITION` (Geometric Optimization)**: Walk machine 12m West; realign digging face by 15° to shorten boom swing arc from 48° to 32°, shaving ~6s per bucket cycle.

### 7.4 Consequence Graph (DAG) (`app/trajectory/consequence_graph.py`)
Constructs a Directed Acyclic Graph conforming to `shared/contracts/consequence.schema.json`:
- **Nodes**: `DECISION`, `MACHINE_EFFECT`, `TASK_EFFECT`, `FUEL_EFFECT`, `IDLE_EFFECT`, `PRODUCTIVITY_EFFECT`, `SAFETY_EFFECT`, `SCHEDULE_EFFECT`, `OUTCOME`.
- **Edges**: `CAUSES`, `INCREASES`, `DECREASES`, `CONTRIBUTES_TO`, `LEADS_TO`, `REDUCES`, `INCREASES_RISK`.
- **Explainability**: Every edge contains a physical or operational explanation.

---

## 8. Adaptive Cockpit Intelligence

### 8.1 Adaptive Attention Modes (`app/domain/attention.py`)
Dynamic focus mode based on transparent priority hierarchy:
1. Critical Safety condition $\rightarrow$ **`SAFETY_FOCUS`**
2. Decision Point active $\rightarrow$ **`DECISION_FOCUS`**
3. Shift Delay Risk $\rightarrow$ **`PLANNING_FOCUS`**
4. Idle / Fuel Waste $\rightarrow$ **`EFFICIENCY_FOCUS`**
5. Skill / Technique Gap $\rightarrow$ **`TRAINING_FOCUS`**
6. Nominal operations $\rightarrow$ **`NORMAL`**

### 8.2 Next-Best-Action Engine (`app/domain/next_best_action.py`)
Generates up to 3 prioritized actions:
- `REVIEW_SAFETY` (Always outranks productivity)
- `COMPARE_TRAJECTORIES`
- `REDUCE_IDLE`
- `REVIEW_SHIFT_FORECAST`
- `REVIEW_SIMILAR_DECISION`

### 8.3 Decision Trace (`app/domain/decision_trace.py`)
Traces step-by-step signals, observed values, baselines, and deductions leading to the recommendation.

---

## 9. Decision Memory & Prediction-vs-Actual Closed Loop

- **`POST /api/v1/trajectory/choose`**: Persists operator choice, context signature (`SIG-TRENCHING-RAIN-INTERMEDIATE-HIQUEUE`), candidate alternatives, predicted metrics, and operator rationale into PostgreSQL (`decision_memory`).
- **`POST /api/v1/trajectory/outcome`**: Records actual measured metrics (`actual_duration_minutes`, `actual_fuel_litres`, `actual_idle_minutes`), computes prediction error (`actual - predicted`), and audits model drift (`WITHIN_TOLERANCE` vs `DRIFT_DETECTED`).
- **`GET /api/v1/trajectory/similar/{operator_id}`**: Retrieves matching historical decision precedents showing actual historical time and fuel saved.

---

## 10. Demo Fixture: "The 17-Minute Trap"

Implements deterministic operational context matching `docs/DEMO_SCENARIO.md`:
- **Task**: Bench 2 Deep Trenching (`T002`), 850 tons target, 320 tons completed.
- **Machine**: Caterpillar 349 Excavator (`EXC-CAT-001`).
- **Operator**: OP1001 (Intermediate).
- **Emerging Dilemma**:
  1. 4 haul trucks bunched at primary crusher $\rightarrow$ 18.2-minute return gap.
  2. Standstill high idle at 1800 RPM wastes 5.8L diesel.
  3. Approaching rain front elevates ground saturation to 28%.
  4. Passive waiting guarantees a **17.4-minute completion delay**, missing shift handoff.
- **Evaluated Trajectories**:
  - `CONTINUE`: 17.4 min delay, +16.2L fuel wasted.
  - `RESEQUENCE`: 17.0 min recovered, 14.8L fuel saved, completes ahead of rain.
  - `REPOSITION`: 13.0 min recovered, 11.2L fuel saved via 16° swing angle reduction.

---

## 11. Database Persistence & Schema Isolation

- **Tables Owned in `operations_schema`**:
  `operations_tasks`, `operations_predictions`, `shift_contexts`, `shift_forecasts`, `decision_points`, `trajectory_scenarios`, `trajectory_outcomes`, `decision_memory`, `similar_contexts`.
- **Database Engine**: SQLAlchemy with PostgreSQL 16 support. Includes automatic in-memory SQLite fallback with `StaticPool` during local testing.

---

## 12. REST API Reference

All 14 endpoints exposed on Port 8002:

| Method | Endpoint | Description | Contract Schema |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health status | Standard health |
| `GET` | `/api/v1/tasks` | List operational tasks (filter by status/operator) | `task.schema.json` |
| `GET` | `/api/v1/tasks/{task_id}` | Retrieve single task specifications | `task.schema.json` |
| `POST` | `/api/v1/tasks/estimate` | Probabilistic task ETA with P10/P90 bounds | `prediction.schema.json` |
| `POST` | `/api/v1/tasks/what-if` | Counterfactual shift parameter simulation | `prediction.schema.json` |
| `GET` | `/api/v1/operator/{operator_id}/shift` | Active shift metadata & progress | `prediction.schema.json` |
| `GET` | `/api/v1/operator/{operator_id}/shift-twin` | Canonical 7-dimension Shift Twin representation | `shift-twin.schema.json` |
| `GET` | `/api/v1/tasks/{task_id}/similar-shifts` | Benchmark shifts matching task profile | `prediction.schema.json` |
| `GET` | `/api/v1/trajectory/current/{operator_id}` | Active decision point & evaluated trajectories | `decision-point.schema.json` |
| `POST` | `/api/v1/trajectory/detect` | Evaluate signals to detect decision points | `decision-point.schema.json` |
| `POST` | `/api/v1/trajectory/evaluate` | Evaluate candidate scenarios & generate DAGs | `scenario.schema.json` & `consequence.schema.json` |
| `POST` | `/api/v1/trajectory/choose` | Record operator trajectory choice | `decision-memory.schema.json` |
| `POST` | `/api/v1/trajectory/outcome` | Record actual outcome & audit prediction error | `decision-memory.schema.json` |
| `GET` | `/api/v1/trajectory/memory/{operator_id}` | Retrieve historical decision memories | `decision-memory.schema.json` |
| `GET` | `/api/v1/trajectory/similar/{operator_id}` | Retrieve matching decision precedents | `decision-memory.schema.json` |

---

## 13. Running, Testing & Verification

### Running the Service:
```bash
cd member2-operations
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### Running Test Suite:
```bash
python -m unittest discover -s member2-operations/tests -p "test_*.py"
```

### Running Monorepo Architectural Validation:
```bash
python scripts/validate_repo.py
```

---

## 14. Assumptions & Known Limitations

1. **Synthetic Data Boundaries**: Because public hackathon datasets lack high-frequency CAN-bus excavator hydraulic events, operational cycles are calibrated against published Caterpillar spec sheets. Unpredictable geological anomalies and machine wear are simplified.
2. **Advisory Prototype Positioning**: CAT Trajectory is strictly an operator decision-support companion. It does **NOT** issue autonomous machine control commands or override machine interlocks.
3. **Production Path**: In live commercial deployments, the feature pipeline is designed to calibrate continuously against Caterpillar Product Link™ telemetry streams.
