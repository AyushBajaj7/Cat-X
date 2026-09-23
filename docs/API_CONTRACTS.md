# API Contracts & Interface Specifications

This document defines the REST API contract across all microservices and the API Gateway for the **CAT Operator Shift Twin** and **CAT Trajectory Consequence Engine**.

All timestamps are formatted according to **ISO 8601** (e.g. `2026-09-23T07:30:00Z`). All endpoints conform to the schemas defined in `/shared/contracts/`.

---

## 1. Safety Service (`http://localhost:8001`)

### `POST /api/v1/safety/telemetry`
Ingest raw telemetry event to evaluate seatbelt status, proximity hazards, and operator behavior anomalies.
- **Request Body**: `TelemetryEvent` (`telemetry.schema.json`)
- **Responses**:
  - `200 OK`: `SafetyStatus` summary of current evaluations (`safety.schema.json`).

### `GET /api/v1/safety/status/{operator_id}`
Retrieve the immediate safety compliance state for a given operator.
- **Responses**:
  - `200 OK`: `SafetyStatus` (`safety.schema.json`).

### `GET /api/v1/safety/alerts/{operator_id}`
Retrieve active and recent safety alerts triggered during the current shift.
- **Query Parameters**: `severity` (optional), `limit` (default: 20)
- **Responses**:
  - `200 OK`: Array of `SafetyAlert` (`safety.schema.json`).

### `GET /api/v1/safety/incidents/{operator_id}`
Retrieve formal incident logs logged for audit compliance.
- **Responses**:
  - `200 OK`: Array of `Incident` (`safety.schema.json`).

### `GET /api/v1/safety/behaviour/{operator_id}`
Retrieve operator behavior analytics, idling scores, and constraint signals.
- **Responses**:
  - `200 OK`: `BehaviourState` (`behaviour.schema.json`).

---

## 2. Operations Service (`http://localhost:8002`)

### `GET /api/v1/tasks`
List daily assignments for site earthmoving operations.
- **Query Parameters**: `status` (optional), `operator_id` (optional)
- **Responses**:
  - `200 OK`: Array of `Task` (`task.schema.json`).

### `GET /api/v1/tasks/{task_id}`
Retrieve detailed specifications of a specific task.
- **Responses**:
  - `200 OK`: `Task` (`task.schema.json`).
  - `404 Not Found`: `ErrorResponse`.

### `POST /api/v1/tasks/estimate`
Calculate probabilistic task completion time and ETA using historical telemetry and environmental variables.
- **Responses**:
  - `200 OK`: `TaskTimeEstimate` (`prediction.schema.json`).

### `POST /api/v1/tasks/what-if`
Run a what-if simulation evaluating how parameter shifts alter the shift outcome.
- **Responses**:
  - `200 OK`: `WhatIfResult` (`prediction.schema.json`).

### `GET /api/v1/operator/{operator_id}/shift`
Retrieve the current shift context, status, and active task assignment.
- **Responses**:
  - `200 OK`: `ShiftContext` entity.

### `GET /api/v1/operator/{operator_id}/shift-twin`
Retrieve the canonical 7-dimension **Shift Twin** representation.
- **Responses**:
  - `200 OK`: `ShiftTwin` (`shift-twin.schema.json`).

### `GET /api/v1/tasks/{task_id}/similar-shifts`
Query historical completed shifts matching the current task's material, machine, and weather profile.
- **Responses**:
  - `200 OK`: Array of `SimilarShiftResult`.

---

## 3. CAT Trajectory — Consequence Engine (`http://localhost:8002`)

### `GET /api/v1/trajectory/current/{operator_id}`
Retrieve the active decision point and candidate trajectories for an operator.
- **Responses**:
  - `200 OK`: Active decision point, candidate trajectories, and recommended `attention_mode`.

### `POST /api/v1/trajectory/detect`
Evaluate incoming operational signals to detect emergent decision points.
- **Request Body**: Operational telemetry, truck arrival intervals, and queue lengths.
- **Responses**:
  - `200 OK`: `DecisionPoint` (`decision-point.schema.json`).

### `POST /api/v1/trajectory/evaluate`
Evaluate candidate operational trajectories against deterministic safety constraints and generate consequence graphs.
- **Request Body**: `decision_point_id`, optional parameter overrides.
- **Responses**:
  - `200 OK`: Evaluated scenarios (`scenario.schema.json`) with consequence graphs (`consequence.schema.json`).

### `POST /api/v1/trajectory/choose`
Record operator trajectory selection into the active operational state and decision memory.
- **Request Body**:
  ```json
  {
    "operator_id": "OP1001",
    "decision_point_id": "DP-BENCH2-HAUL-01",
    "scenario_id": "SCEN-02-RESEQUENCE",
    "operator_reason": "Bypassed haul truck queue before rain onset."
  }
  ```
- **Responses**:
  - `200 OK`: Confirmation and logged `decision_id`.

### `POST /api/v1/trajectory/outcome`
Record actual measured outcome after trajectory execution and compute prediction error.
- **Request Body**: `decision_id`, actual metrics (`actual_eta_minutes`, `actual_fuel_liters`).
- **Responses**:
  - `200 OK`: Calculated prediction errors and model drift indicators.

### `GET /api/v1/trajectory/memory/{operator_id}`
Retrieve historical decision memories recorded for this operator.
- **Responses**:
  - `200 OK`: Array of `DecisionMemory` (`decision-memory.schema.json`).

### `GET /api/v1/trajectory/similar/{operator_id}`
Retrieve historical decision memories matching the current operational context signature.
- **Responses**:
  - `200 OK`: Array of matching historical decisions with actual outcome evidence.

---

## 4. Training Service (`http://localhost:8003`)

### `GET /api/v1/training/modules`
List available operator training modules.
- **Responses**:
  - `200 OK`: Array of `TrainingModule` (`training.schema.json`).

### `GET /api/v1/training/modules/{module_id}`
Retrieve specific module details, learning objectives, and simulator scenarios.
- **Responses**:
  - `200 OK`: `TrainingModule` (`training.schema.json`).

### `GET /api/v1/training/recommendations/{operator_id}`
Retrieve personalized micro-training recommendations triggered by behavioral or operational deviations.
- **Responses**:
  - `200 OK`: Array of `TrainingRecommendation` (`training.schema.json`).

### `POST /api/v1/training/attempts`
Record completion of a micro-module quiz or simulator exercise.
- **Responses**:
  - `201 Created`: `TrainingAttempt` (`training.schema.json`).

### `GET /api/v1/training/progress/{operator_id}`
Retrieve cumulative operator training stats, certifications, and proficiency scores.
- **Responses**:
  - `200 OK`: `TrainingProgress` (`training.schema.json`).

---

## 5. API Gateway (`http://localhost:8080`)

### `GET /api/v1/health`
Composite health check querying all downstream microservices.
- **Responses**:
  - `200 OK`: Status of Gateway and downstream services (`safety`, `operations`, `training`).

### `GET /api/v1/dashboard/{operator_id}`
Aggregate view composing the Shift Twin, immediate safety state, active decision point, trajectory card, and top training recommendation.
- **Responses**:
  - `200 OK`: `DashboardState` (`dashboard.schema.json`).

### `GET /api/v1/shift/{operator_id}`
Proxy endpoint retrieving full canonical Shift Twin object.
- **Responses**:
  - `200 OK`: `ShiftTwin` (`shift-twin.schema.json`).

### `POST /api/v1/telemetry`
Single entry-point telemetry ingestion gateway fanning out events asynchronously to downstream services.
- **Responses**:
  - `202 Accepted`: Telemetry queued for evaluation.

### `POST /api/v1/demo/reset`
Reset operational and simulation state for deterministic demonstration of "The 17-Minute Trap".
- **Responses**:
  - `200 OK`: Reset confirmation.
