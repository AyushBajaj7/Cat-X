# Development Rules & Team Engineering Standards

## 1. Core Engineering Principles

1. **Deterministic & Compilable**: The repository must compile, install, and pass tests on every engineer's machine from a fresh checkout.
2. **Strict Ownership Boundaries**: Engineers must adhere strictly to `docs/WORK_SPLIT.md`. Never edit another engineer's service directory without prior coordination.
3. **No Dead Code or Fake Imports**: Every created Python package must have valid imports. No empty mocks or fake syntax.
4. **Contract-First**: Any change to API payloads must be updated in `/shared/contracts/*.schema.json` first.

---

## 2. Git & Branching Strategy

### Branch Allocation:
- `main`: Production-ready, fully passing CI, clean baseline.
- `feature/member1-safety`: Dedicated feature branch for Engineer 1.
- `feature/member2-operations`: Dedicated feature branch for Engineer 2.
- `feature/member3-training-ui`: Dedicated feature branch for Engineer 3.

### Commit Conventions:
All commits must follow the **Conventional Commits** standard:
- `feat(safety): add seatbelt compliance alert trigger`
- `feat(operations): implement XGBoost task ETA regression model`
- `feat(training): render micro-module simulator in frontend`
- `fix(gateway): resolve timeout on downstream telemetry fan-out`
- `test(operations): add unit tests for what-if simulation engine`
- `docs(contracts): update shift-twin schema with terrain grade factor`
- `chore(repo): update dependencies and lockfiles`

---

## 3. Technology & Coding Guidelines

### Python (Target: Python 3.12+):
- Use strict type hints (`str`, `int`, `float`, `list[str]`, `dict[str, Any]`, `datetime`).
- Use **Pydantic v2** (`BaseModel`, `Field`) for request/response serialization and validation.
- FastAPI dependency injection (`Depends`) for shared database sessions and clients.
- Use asynchronous route handlers (`async def`) for I/O operations and downstream HTTP calls.
- Pin all packages in `requirements.txt` with exact semantic versions.

### Frontend (Target: Node 20 LTS, React 18, TypeScript, Tailwind CSS):
- Strict TypeScript configuration (`"strict": true`).
- Modular UI components with clean Tailwind CSS utility classes.
- Zero business math in React components: UI components only render what the API Gateway delivers.
- Centralized API client module with typed response interfaces.

---

## 4. Local Execution & Testing Commands

### Setup Virtual Environment (Root or per Service):
```bash
# Using Python 3.12+
python -m venv venv
# On Windows
.\venv\Scripts\Activate.ps1
# On Linux/macOS
source venv/bin/activate
```

### Install Dependencies:
```bash
# Safety Service
pip install -r services/safety/requirements.txt

# Operations Service
pip install -r services/operations/requirements.txt

# Training Service
pip install -r services/training/requirements.txt

# Gateway & Integration
pip install -r integration/gateway/requirements.txt
```

### Running Test Suites:
```bash
# Run all tests across the monorepo
pytest services/safety/tests services/operations/tests services/training/tests integration/gateway/tests

# Run specific service tests
pytest services/safety/tests/ -v
pytest services/operations/tests/ -v
pytest services/training/tests/ -v
pytest integration/gateway/tests/ -v
```

### Running Services Locally:
```bash
# Terminal 1: Safety Service (Port 8001)
uvicorn services.safety.app.main:app --port 8001 --reload

# Terminal 2: Operations Service (Port 8002)
uvicorn services.operations.app.main:app --port 8002 --reload

# Terminal 3: Training Service (Port 8003)
uvicorn services.training.app.main:app --port 8003 --reload

# Terminal 4: API Gateway (Port 8000)
uvicorn integration.gateway.app.main:app --port 8000 --reload

# Terminal 5: Frontend UI (Port 5173)
cd frontend && npm install && npm run dev
```

### Running via Docker Compose:
```bash
# Build and start all services and PostgreSQL
docker-compose up --build

# Run in background
docker-compose up -d

# Check service logs
docker-compose logs -f
```
