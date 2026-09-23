# Member 2 — Operations Intelligence, ML, Shift Twin & CAT Trajectory

**Owner**: Engineer 2  
**Port**: `8002`  
**Boundary**: Operational State, ML Forecasting & CAT Trajectory Consequence Engine

## Scope & Responsibilities
- Task state management, progress tracking, and site zoning
- Probabilistic task-time estimation (ETA model with P10/P90 confidence bounds)
- Fuel and productivity proxy modeling
- Canonical Shift Twin 7-dimension state composition and attention mode determination
- **CAT Trajectory Consequence Engine**:
  - Decision point detection (`QUEUE_IMBALANCE`, `SHIFT_DELAY_RISK`, `EFFICIENCY_DEVIATION`, etc.)
  - Safe and feasible candidate scenario generation (`CONTINUE`, `RESEQUENCE`, `REPOSITION`)
  - Safety-constrained scenario validation (consuming constraint signals from Engineer 1)
  - Causal consequence engine & consequence graph computation
  - Counterfactual what-if simulation and shift forecast
  - Historical similar-shift matching
  - Decision memory recording and prediction-vs-actual evaluation
  - Next-best-action logic and decision trace

## Prohibitions
- Does NOT render UI components or visualize graphs in React (Owned by Engineer 3).
- Does NOT invent safety thresholds or override safety violation records (Owned by Engineer 1).
