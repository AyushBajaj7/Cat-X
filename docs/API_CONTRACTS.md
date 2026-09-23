# API Contracts & Interface Specifications

This document defines the REST API contract across all microservices and the API Gateway for the **CAT Operator Shift Twin** platform.

All timestamps are formatted according to **ISO 8601** (e.g. `2026-09-23T07:30:00Z`). All endpoints conform to the schemas defined in `/shared/contracts/`.

---

## 1. Safety Service (`http://localhost:8001`)

### `POST /api/v1/safety/telemetry`
Ingest raw telemetry event to evaluate seatbelt status, proximity hazards, and operator behavior anomalies.

- **Request Body**: `TelemetryEvent` (`telemetry.schema.json`)
- **Responses**:
  - `200 OK`: `SafetyStatus` summary of current evaluations.
  - `400 Bad Request`: `ErrorResponse` if validation fails.

### `GET /api/v1/safety/status/{operator_id}`
Retrieve the immediate safety compliance state for a given operator.

- **Path Parameters**: `operator_id` (string, e.g. `OP1001`)
- **Responses**:
  - `200 OK`:
    ```json
    {
      "operator_id": "OP1001",
      "machine_id": "EXC001",
      "timestamp": "2026-09-23T07:30:00Z",
      "seatbelt_fastened": true,
      "seatbelt_compliance_pct": 98.5,
      "proximity_warning_level": "LOW",
      "active_hazard_count": 0,
      "overall_safety_score": 96.0
    }
    ```
  - `404 Not Found`: `ErrorResponse`

### `GET /api/v1/safety/alerts/{operator_id}`
Retrieve active and recent safety alerts triggered during the current shift.

- **Path Parameters**: `operator_id` (string)
- **Query Parameters**: `severity` (optional: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), `limit` (default: 20)
- **Responses**:
  - `200 OK`: Array of `SafetyAlert` (`safety.schema.json`)

### `GET /api/v1/safety/incidents/{operator_id}`
Retrieve formal incident logs logged for audit compliance.

- **Path Parameters**: `operator_id` (string)
- **Responses**:
  - `200 OK`: Array of `Incident` (`safety.schema.json`)

### `GET /api/v1/safety/behaviour/{operator_id}`
Retrieve operator behavior analytics (excessive idling, aggressive maneuvers, cycle consistency).

- **Path Parameters**: `operator_id` (string)
- **Responses**:
  - `200 OK`: `BehaviourAnalysis` (`safety.schema.json`)

---

## 2. Operations Service (`http://localhost:8002`)

### `GET /api/v1/tasks`
List daily assignments for site earthmoving operations.

- **Query Parameters**: `status` (optional: `PENDING`, `IN_PROGRESS`, `COMPLETED`), `operator_id` (optional)
- **Responses**:
  - `200 OK`: Array of `Task` (`task.schema.json`)

### `GET /api/v1/tasks/{task_id}`
Retrieve detailed specifications of a specific task.

- **Path Parameters**: `task_id` (string, e.g. `T002`)
- **Responses**:
  - `200 OK`: `Task` (`task.schema.json`)
  - `404 Not Found`: `ErrorResponse`

### `POST /api/v1/tasks/estimate`
Calculate probabilistic task completion time and ETA using historical telemetry and environmental variables.

- **Request Body**:
  ```json
  {
    "task_id": "T002",
    "operator_id": "OP1001",
    "machine_id": "EXC001",
    "remaining_volume_tons": 450.0,
    "weather_factor": 1.15,
    "terrain_grade_pct": 4.5
  }
  ```
- **Responses**:
  - `200 OK`: `TaskTimeEstimate` (`prediction.schema.json`)

### `POST /api/v1/tasks/what-if`
Run a what-if simulation evaluating how parameter shifts (e.g. idle reduction, weather degradation, alternate haul route) alter the shift outcome.

- **Request Body**: `WhatIfRequest` (`prediction.schema.json`)
- **Responses**:
  - `200 OK`: `WhatIfResult` (`prediction.schema.json`)

### `GET /api/v1/operator/{operator_id}/shift`
Retrieve standard metadata and milestones for the operator's current active shift.

- **Path Parameters**: `operator_id` (string)
- **Responses**:
  - `200 OK`: `ShiftContext` (`prediction.schema.json`)

### `GET /api/v1/operator/{operator_id}/shift-twin`
Retrieve the comprehensive canonical **CAT Operator Shift Twin** object.

- **Path Parameters**: `operator_id` (string)
- **Responses**:
  - `200 OK`: `ShiftTwin` (`shift-twin.schema.json`)

### `GET /api/v1/tasks/{task_id}/similar-shifts`
Retrieve historical shift matches with comparable machine, operator experience, and environmental conditions.

- **Path Parameters**: `task_id` (string)
- **Responses**:
  - `200 OK`: Array of `SimilarShiftResult` (`prediction.schema.json`)

---

## 3. Training Service (`http://localhost:8003`)

### `GET /api/v1/training/modules`
List available training hub modules (pre-shift, precision handling, eco-operation, hazard avoidance).

- **Responses**:
  - `200 OK`: Array of `TrainingModule` (`training.schema.json`)

### `GET /api/v1/training/recommendations/{operator_id}`
Retrieve personalized micro-training recommendations dynamically triggered by detected behavior flags or safety incidents.

- **Path Parameters**: `operator_id` (string)
- **Responses**:
  - `200 OK`: Array of `TrainingRecommendation` (`training.schema.json`)

### `GET /api/v1/training/modules/{module_id}`
Retrieve full module syllabus, multimedia instructions, and simulator parameters.

- **Path Parameters**: `module_id` (string, e.g. `MOD-ECO-01`)
- **Responses**:
  - `200 OK`: `TrainingModule` (`training.schema.json`)
  - `404 Not Found`: `ErrorResponse`

### `POST /api/v1/training/attempts`
Record completion of a training exercise or simulator scenario.

- **Request Body**: `TrainingAttempt` (`training.schema.json`)
- **Responses**:
  - `201 Created`: `TrainingAttempt` with calculated score and completion status.

### `GET /api/v1/training/progress/{operator_id}`
Retrieve historical progress, certifications, and mastery levels for an operator.

- **Path Parameters**: `operator_id` (string)
- **Responses**:
  - `200 OK`: `TrainingProgress` (`training.schema.json`)

---

## 4. API Gateway (`http://localhost:8000`)

### `GET /api/v1/health`
Composite health check querying downstream Safety, Operations, and Training services.

- **Responses**:
  - `200 OK`:
    ```json
    {
      "status": "HEALTHY",
      "timestamp": "2026-09-23T07:30:00Z",
      "downstream": {
        "safety_service": "HEALTHY",
        "operations_service": "HEALTHY",
        "training_service": "HEALTHY"
      }
    }
    ```

### `POST /api/v1/telemetry`
Unified ingestion entrypoint that fans out telemetry to Safety and Operations services.

- **Request Body**: `TelemetryEvent` (`telemetry.schema.json`)
- **Responses**:
  - `202 Accepted`: Event queued and acknowledged.

### `GET /api/v1/dashboard/{operator_id}`
Composite endpoint consumed by the frontend cab dashboard. Aggregates:
- Active task details
- Shift Twin state summary
- Recent safety alerts
- Immediate Next-Best-Action recommendations
- Top training recommendation

- **Path Parameters**: `operator_id` (string)
- **Responses**:
  - `200 OK`: Composite dashboard payload

### `GET /api/v1/shift/{operator_id}`
Real-time synchronized representation of the operator's shift twin.

- **Path Parameters**: `operator_id` (string)
- **Responses**:
  - `200 OK`: `ShiftTwin` (`shift-twin.schema.json`)
