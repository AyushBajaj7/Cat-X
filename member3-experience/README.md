# Member 3 — Operator Experience, Training Hub & Integration

**Owner**: Engineer 3  
**Ports**: Frontend (`5173`), API Gateway (`8080`), Training Service (`8003`)  
**Boundary**: Cockpit UI, Training Hub, API Gateway, Docker & E2E Integration

## Scope & Responsibilities
- **Training Service (`member3-experience/training`)**:
  - Training catalog, simulator scenarios, assessment scoring, and operator progress tracking.
- **Operator Cockpit (`member3-experience/frontend`)**:
  - React/Vite/Tailwind operator interface.
  - Adaptive UI rendering according to backend `attention_mode` (`NORMAL`, `SAFETY_FOCUS`, `DECISION_FOCUS`, etc.).
  - Decision-point prompt, trajectory alternative comparison, consequence graph visualization, operator choice modal, outcome replay, and decision memory exploration.
- **API Gateway (`member3-experience/gateway`)**:
  - Reverse proxy, telemetry ingestion fanout, and aggregate dashboard composition.
- **Integration & Demo**:
  - Deterministic demo scenario simulator ("The 17-Minute Trap"), Docker Compose environment, end-to-end integration tests.

## Prohibitions
- Does NOT calculate safety scores, ETAs, consequence predictions, or attention modes in the frontend or gateway.
- Strictly acts as the presentation and orchestration layer for backend intelligence.
