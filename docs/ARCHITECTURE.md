# System Architecture: CAT Operator Shift Twin

## 1. High-Level Architecture Diagram

```
                                  +---------------------------------------------+
                                  |          Frontend (React + Vite + TS)       |
                                  |                   Port 5173                 |
                                  +---------------------------------------------+
                                                         |
                                                         | HTTP / REST & Live Polling
                                                         v
                                  +---------------------------------------------+
                                  |            API Gateway (FastAPI)            |
                                  |                   Port 8000                 |
                                  +---------------------------------------------+
                                       /                 |                 \
                                      /                  |                  \
                                     /                   |                   \
                     (REST)         /             (REST) |                    \  (REST)
                                   v                     v                     v
                +----------------------+   +-----------------------+   +----------------------+
                |    Safety Service    |   |  Operations Service   |   |   Training Service   |
                |      Port 8001       |   |       Port 8002       |   |      Port 8003       |
                |     (Engineer 1)     |   |     (Engineer 2)      |   |     (Engineer 3)     |
                +----------------------+   +-----------------------+   +----------------------+
                           \                         |                         /
                            \                        |                        /
                             \                       |                       /
                              v                      v                      v
                +-----------------------------------------------------------------------------+
                |                               PostgreSQL 16                                 |
                |                                 Port 5432                                   |
                |        (Logical Schema Isolation: safety | operations | training)           |
                +-----------------------------------------------------------------------------+
```

---

## 2. Port Allocations & Protocol Standards

The following ports are strictly fixed across the team. No changes may be made without team-wide consensus.

| Service | Host Port | Protocol | Technology | Ownership |
| :--- | :--- | :--- | :--- | :--- |
| **Frontend** | `5173` | HTTP | React 18, Vite, TypeScript, Tailwind CSS | Engineer 3 |
| **API Gateway** | `8000` | HTTP / REST | FastAPI, Uvicorn, Python 3.12 | Engineer 3 |
| **Safety Service** | `8001` | HTTP / REST | FastAPI, Uvicorn, Python 3.12 | Engineer 1 |
| **Operations Service** | `8002` | HTTP / REST | FastAPI, Uvicorn, Python 3.12, scikit-learn | Engineer 2 |
| **Training Service** | `8003` | HTTP / REST | FastAPI, Uvicorn, Python 3.12 | Engineer 3 |
| **PostgreSQL Database** | `5432` | TCP / PG Wire | PostgreSQL 16 Alpine | Infrastructure (All) |

---

## 3. Communication Patterns

1. **Client to Gateway**:
   - The Frontend communicates exclusively with the **API Gateway** on Port `8000`.
   - The Frontend does not connect directly to Safety, Operations, or Training microservices.
   - Live updates on the cab dashboard are retrieved via high-efficiency REST polling (or server-sent events where telemetry updates are fast), avoiding fragile messaging brokers.

2. **Gateway to Microservices**:
   - The API Gateway executes parallel HTTP requests (using async `httpx`) to Safety, Operations, and Training services.
   - Aggregated views like `/api/v1/dashboard/{operator_id}` compose data from all three backends into a coherent response.

3. **Inter-Service Isolation**:
   - Services communicate via REST APIs, never direct database queries across domains.
   - If Operations needs safety metrics to calculate Shift Twin context, it invokes `GET /api/v1/safety/status/{operator_id}` or receives the safety payload through the telemetry ingestion flow.

4. **Zero Over-Engineering Policy**:
   - No Kafka, RabbitMQ, or message brokers.
   - No Redis or distributed caching layers.
   - No Kubernetes or service mesh (Istio, Envoy).
   - No Vector databases.
   - Clean, testable, deterministic FastAPI services orchestrated via Docker Compose.

---

## 4. Database Schema Isolation

All services share a single PostgreSQL container in development, but enforce strict **logical schema isolation**:

```sql
-- Schema Isolation Setup
CREATE SCHEMA safety_schema;
CREATE SCHEMA operations_schema;
CREATE SCHEMA training_schema;
```

### Isolation Rules:
- `services/safety/` has exclusive read/write access to `safety_schema.*` tables.
- `services/operations/` has exclusive read/write access to `operations_schema.*` tables.
- `services/training/` has exclusive read/write access to `training_schema.*` tables.
- **Rule**: Direct cross-schema joins and foreign keys between services are strictly prohibited. Data cross-referencing must happen at the API layer.

---

## 5. Contract-First Development

All inter-service and client-service data contracts are defined as standard **JSON Schema (Draft-07)** documents located in `/shared/contracts/`.

```
shared/contracts/
├── telemetry.schema.json
├── safety.schema.json
├── task.schema.json
├── prediction.schema.json
├── shift-twin.schema.json
├── training.schema.json
└── error.schema.json
```

- Backend services derive or validate their Pydantic models from these schemas.
- Frontend TypeScript interfaces map directly to these schema entities.
- Automated CI tests validate that JSON schemas compile and samples validate against them.

---

## 6. Error Handling Strategy

All error responses from all endpoints must adhere to `shared/contracts/error.schema.json`:

```json
{
  "error_code": "RESOURCE_NOT_FOUND",
  "message": "Task with ID T002 was not found.",
  "timestamp": "2026-09-23T07:30:00Z",
  "details": {
    "task_id": "T002",
    "service": "operations-service"
  }
}
```

Standard HTTP status codes are enforced:
- `200 OK`: Request succeeded.
- `201 Created`: Resource created.
- `400 Bad Request`: Validation failure or contract violation.
- `404 Not Found`: Target entity does not exist.
- `422 Unprocessable Entity`: Request format valid, but semantic validation failed.
- `500 Internal Server Error`: Unhandled server exception (logged with stack trace).
- `502 Bad Gateway`: Downstream microservice unreachable by the Gateway.
