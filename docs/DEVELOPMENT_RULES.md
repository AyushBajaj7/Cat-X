# Development Rules & Team Engineering Standards

## 1. Core Engineering Principles

1. **Deterministic & Compilable**: The repository must compile, install, and pass tests on every engineer's machine from a fresh checkout.
2. **Strict Ownership Boundaries**: Engineers must adhere strictly to `docs/WORK_SPLIT.md`. Never edit another engineer's service directory without prior coordination.
3. **No Dead Code or Broken Imports**: Every created Python package must have valid imports and valid AST syntax.
4. **Contract-First**: Any change to API payloads must be updated in `/shared/contracts/*.schema.json` first.
5. **No Frontend / Gateway Intelligence Leakage**:
   - The React frontend strictly displays data delivered by the API Gateway.
   - The API Gateway strictly routes and aggregates without performing business logic calculations.
   - All operational state, predictions, and consequence evaluations originate in the backend services.

---

## 2. Git & Branching Strategy

### Branch Allocation:
- `main`: Production-ready, fully passing CI, clean architecture baseline.
- `feature/member1-safety`: Dedicated feature branch for Engineer 1.
- `feature/member2-operations`: Dedicated feature branch for Engineer 2.
- `feature/member3-training-ui`: Dedicated feature branch for Engineer 3.

### Commit Conventions:
All commits must follow the **Conventional Commits** standard:
- `feat(safety): add seatbelt compliance alert trigger`
- `feat(trajectory): implement decision-point detection algorithm`
- `feat(trajectory): add consequence graph DAG computation`
- `feat(ui): render trajectory comparison cards in cockpit`
- `fix(gateway): resolve timeout on downstream telemetry fan-out`
- `test(operations): add tests for trajectory choose and memory`
- `docs(contracts): update consequence schema with causal node types`
- `chore(repo): update dependencies and lockfiles`

---

## 3. Technology & Coding Guidelines

### Python (Target: Python 3.12+):
- Strict type hints (`str`, `int`, `float`, `list[str]`, `dict[str, Any]`, `datetime`).
- Use **Pydantic v2** (`BaseModel`, `Field`, `SettingsConfigDict`) for request/response validation and settings.
- FastAPI dependency injection (`Depends`) for shared database sessions and clients.
- Asynchronous route handlers (`async def`) for I/O operations and downstream HTTP calls.
- Pin all packages in `requirements.txt` with exact semantic versions.

### Frontend (Target: Node 20 LTS, React 18, TypeScript, Tailwind CSS):
- Strict TypeScript configuration (`"strict": true`).
- Zero business math in React components: UI components only render what the API Gateway delivers.
- Centralized API client module with typed response interfaces.

---

## 4. Local Execution & Testing Commands

### Setup Virtual Environment:
```bash
python -m venv venv
# Windows
.\venv\Scripts\Activate.ps1
# Linux / macOS
source venv/bin/activate
```

### Install Dependencies:
```bash
pip install -r member1-safety/requirements.txt
pip install -r member2-operations/requirements.txt
pip install -r member3-experience/training/requirements.txt
pip install -r member3-experience/gateway/requirements.txt
```

### Running Test Suites:
```bash
# Run all test suites across the monorepo
python -m pytest member1-safety/tests member2-operations/tests member3-experience/training/tests member3-experience/gateway/tests member3-experience/tests integration/tests -v

# Run specific service tests
pytest member1-safety/tests/ -v
pytest member2-operations/tests/ -v
pytest member3-experience/training/tests/ -v
pytest member3-experience/gateway/tests/ -v
pytest integration/tests/ -v
```

### Running Services Locally:
```bash
# Terminal 1: Safety Service (Port 8001)
cd member1-safety && uvicorn app.main:app --port 8001 --reload

# Terminal 2: Operations & Trajectory Service (Port 8002)
cd member2-operations && uvicorn app.main:app --port 8002 --reload

# Terminal 3: Training Service (Port 8003)
cd member3-experience/training && uvicorn app.main:app --port 8003 --reload

# Terminal 4: API Gateway (Port 8080)
cd member3-experience/gateway && uvicorn app.main:app --port 8080 --reload

# Terminal 5: Operator Cockpit Frontend (Port 5173)
cd member3-experience/frontend && npm install && npm run dev
```

### Running via Docker Compose:
```bash
docker-compose up --build
```
