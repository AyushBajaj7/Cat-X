# System Architecture: CAT Operator Shift Twin & CAT Trajectory

## 1. High-Level Architecture Diagram

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

## 2. Port Allocations & Protocol Standards

The following ports are strictly fixed across the team. No changes may be made without team-wide consensus.

| Service | Host Port | Protocol | Technology | Ownership | Directory |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Frontend** | `5173` | HTTP | React 18, Vite, TypeScript, Tailwind CSS | Engineer 3 | `member3-experience/frontend` |
| **API Gateway** | `8080` | HTTP / REST | FastAPI, Uvicorn, Python 3.12 | Engineer 3 | `member3-experience/gateway` |
| **Safety Service** | `8001` | HTTP / REST | FastAPI, Uvicorn, Python 3.12 | Engineer 1 | `member1-safety` |
| **Operations Service** | `8002` | HTTP / REST | FastAPI, Uvicorn, Python 3.12, scikit-learn | Engineer 2 | `member2-operations` |
| **Training Service** | `8003` | HTTP / REST | FastAPI, Uvicorn, Python 3.12 | Engineer 3 | `member3-experience/training` |
| **PostgreSQL Database** | `5432` | TCP / PG Wire | PostgreSQL 16 Alpine | Infrastructure (All) | Containerized |

---

## 3. Communication Patterns

1. **Client to Gateway**:
   - The Frontend communicates exclusively with the **API Gateway** on Port `8080`.
   - The Frontend does not connect directly to Safety, Operations, or Training microservices.
   - The frontend acts strictly as a consumer/renderer and performs no business logic calculations.

2. **Gateway to Microservices**:
   - The API Gateway executes parallel HTTP requests (using async `httpx`) to Safety, Operations, and Training services.
   - Aggregated views like `/api/v1/dashboard/{operator_id}` compose data from all three backends into a coherent response.
   - The gateway never becomes a second intelligence engine; it merely routes, fans out, and aggregates.

3. **Inter-Service Isolation & Signal Flow**:
   - Services communicate via REST APIs, never direct database queries across domains.
   - **Safety Constraints to Trajectory**: Engineer 1's safety service produces safety status, anomaly signals, and physical constraint flags (`GET /api/v1/safety/status/{operator_id}`, `GET /api/v1/safety/behaviour/{operator_id}`). Engineer 2's operations service consumes these signals to reject infeasible trajectory scenarios.

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
- `member1-safety/` has exclusive read/write access to `safety_schema.*` tables.
- `member2-operations/` has exclusive read/write access to `operations_schema.*` tables (tasks, shifts, trajectories, decision memory).
- `member3-experience/training/` has exclusive read/write access to `training_schema.*` tables.
- **Rule**: Direct cross-schema joins and foreign keys between services are strictly prohibited. Data cross-referencing must happen at the API layer.

---

## 5. Contract-First Development

All inter-service and client-service data contracts are defined as standard **JSON Schema (Draft-07)** documents located in `/shared/contracts/`:

```
shared/contracts/
├── telemetry.schema.json         # Raw & ingested telemetry event
├── safety.schema.json            # Real-time safety compliance state
├── behaviour.schema.json         # Behavior anomalies, idling, and constraint signals
├── task.schema.json              # Operational task entity
├── prediction.schema.json        # Probabilistic task-time estimation
├── shift-twin.schema.json        # Canonical 7-dimension digital Shift Twin
├── decision-point.schema.json    # Emergent operational inflection point
├── scenario.schema.json          # Candidate trajectory scenario
├── consequence.schema.json       # Causal consequence graph (DAG)
├── decision-memory.schema.json   # Persisted decision and prediction-vs-actual log
├── training.schema.json          # Training modules, attempts, recommendations
├── dashboard.schema.json         # Composite Operator Cockpit view
└── error.schema.json             # Standardized error responses
```

---

## 6. Important Safety Position

> [!CAUTION]
> **Decision-Support Boundary**:
> - CAT Trajectory is a decision-support prototype.
> - It does NOT control machinery or issue autonomous machine commands.
> - It does NOT replace operator judgment or machine interlocks.
> - Safety constraints are used strictly to reject or flag infeasible candidate trajectories.
> - Safety must NEVER be treated as a simple productivity trade-off.
