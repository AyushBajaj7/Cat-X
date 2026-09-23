# CAT Operator Shift Twin - Frontend UI

## Technology Stack
- **Framework**: React 18
- **Build Tool**: Vite
- **Language**: TypeScript (Strict Mode)
- **Styling**: Tailwind CSS
- **Port**: `5173`

## Ownership
- Owned and maintained by **Engineer 3 (Training, UI & Integration)**.

## Architectural Rules
- The Frontend is strictly a **consumer** of backend APIs via the API Gateway (`http://localhost:8000/api/v1`).
- **NO business logic calculations** (such as safety hazard evaluation, ETA machine learning calculations, or training scoring formulas) are permitted within frontend components.
- All data models map to `/shared/contracts/*.schema.json`.

## Running Locally
```bash
cd frontend
npm install
npm run dev
```

## Running Lint / Type Checking
```bash
npm run lint
```
