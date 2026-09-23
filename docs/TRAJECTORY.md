# CAT Trajectory — The Operator Consequence Engine

> **Product Vision**: Moving beyond reactive alerts and static dashboards to provide Caterpillar operators with an intelligent companion that detects emergent operational decision points, forecasts multi-order consequences through causal modeling, respects deterministic safety constraints, and builds a compounding organizational decision memory.

---

## 1. Executive Summary & Core Differentiation

In heavy earthmoving and construction operations, machine operators make dozens of tactical decisions each shift: when to reposition the excavator, how to handle haul truck arrival variance, when to alter dig sequencing as ground saturation increases, and how to balance engine speed with cycle pace.

Traditional telematics dashboards are **rearview mirrors**—they inform the operator after fuel has been wasted, after an idle spike has occurred, or after a deadline is already irrecoverable. Generic "what-if" calculators require manual parameter tweaking that distracted operators in high-tempo cabs will never perform.

**CAT Trajectory** is an autonomous **Consequence Engine** that operates on a continuous closed-loop cycle:

```
                  ┌─────────────────────────────────────┐
                  │               OBSERVE               │
                  │   Real-time Telemetry & Environment │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │        DETECT DECISION POINT        │
                  │   Algorithmic Trigger & Severity    │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │        GENERATE ALTERNATIVES        │
                  │ Continue | Re-sequence | Reposition │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │       APPLY SAFETY CONSTRAINTS      │
                  │  Deterministic Rejection/Validation │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │         PREDICT CONSEQUENCES        │
                  │    ETA, Fuel, Risk & Schedule Drift │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │      EXPLAIN CONSEQUENCE CHAIN      │
                  │      Directed Causal Graph (DAG)    │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │           OPERATOR CHOOSES          │
                  │  Human-in-the-Loop Tactical Action  │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │        SIMULATE / REPLAY OUTCOME    │
                  │   Execute Trajectory in Active State│
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │            RECORD DECISION          │
                  │   Context Signature & Choice Logged │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │     COMPARE PREDICTED VS ACTUAL     │
                  │   Model Drift & Accuracy Feedback   │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │         REUSE DECISION MEMORY       │
                  │ Similar Context Matching for Future │
                  └─────────────────────────────────────┘
```

---

## 2. Core Functional Pillars

### 2.1 Decision Point Detector
Rather than spamming the cab with continuous micro-alerts, the Decision Point Detector identifies **discrete operational inflection points** where an operator's intervention can materially alter shift outcomes.

**Trigger Types**:
- `QUEUE_IMBALANCE`: Haul truck bunching or excessive arrival spacing creating excavator starvation or haul queue idling.
- `SHIFT_DELAY_RISK`: Compounding cycle delays pushing estimated task completion past shift handoff.
- `EFFICIENCY_DEVIATION`: Significant divergence between current bucket fill factor / swing efficiency and machine baseline.
- `ENVIRONMENT_CHANGE`: Sudden rainfall, deteriorating ground saturation, or steepened grade affecting traction.
- `SAFETY_APPROACH`: Machine operating parameters nearing slope stability or perimeter safety thresholds.
- `TASK_TRANSITION`: Natural milestone completion requiring immediate transition to trenching, grading, or stockpile loading.
- `UNUSUAL_OPERATING_PATTERN`: Heavy bucket shock loads, prolonged high-idle pauses, or erratic swing cycles.

### 2.2 Candidate Trajectory Generation
When a decision point is triggered, the engine generates a bounded set of 2 to 4 viable candidate operational trajectories:
1. **CONTINUE (Baseline)**: Maintain current operating pattern and observe baseline degradation.
2. **RESEQUENCE**: Swap immediate sub-task or load sequence (e.g., pivot to bench overburden while truck queue clears).
3. **REPOSITION**: Shift machine physical stance or bench angle (e.g., rotate digging face by 15° to decrease swing arc).

### 2.3 Safety-Constrained Scenario Validation
Safety is not a soft trade-off against productivity. CAT Trajectory treats safety as a **strict deterministic gate**:
- Candidate trajectories pass through the Safety Constraint Validator (consuming safety signals owned by Engineer 1).
- If a candidate trajectory breaches slope limits (grade > 15%), violates proximity zones (support vehicles < 15m), or exceeds safe boom reach envelope, the trajectory is assigned `constraint_status: REJECTED`.
- Infeasible trajectories cannot be recommended or selected as optimal paths.

### 2.4 Causal Consequence Engine & Consequence Graph
For each feasible trajectory, the engine computes a **Directed Acyclic Graph (DAG)** representing the multi-order physical, logistical, and economic consequence chain:

```
[ DECISION: Reposition Face 15° West ]
                 │
                 ▼
[ MACHINE_EFFECT: Boom Swing Arc Reduced 48° ➔ 32° ]
                 │
                 ├──────────────────────────────────────┐
                 ▼                                      ▼
[ TASK_EFFECT: Cycle Time Cuts 28s ➔ 22s ]     [ FUEL_EFFECT: Hydraulic Load Drops 12% ]
                 │                                      │
                 ▼                                      ▼
[ PRODUCTIVITY_EFFECT: +18 Tons/Hour ]         [ FUEL_SAVED: 6.4 Liters / Remaining Task ]
                 │                                      │
                 └──────────────────┬───────────────────┘
                                    │
                                    ▼
       [ OUTCOME: Task Finishes 14 Min Early; Zero Queue Idling ]
```

**Node Types**:
- `DECISION`: The root tactical choice.
- `MACHINE_EFFECT`: Immediate physical response (engine RPM, swing angle, hydraulic pressure).
- `TASK_EFFECT`: Cycle time, volume rate, truck exchange interval.
- `FUEL_EFFECT`: Instantaneous and cumulative fuel burn rate.
- `IDLE_EFFECT`: Reduction or increase in low/high idle time.
- `PRODUCTIVITY_EFFECT`: Tons moved per hour, truck fill efficiency.
- `SAFETY_EFFECT`: Stability margin, proximity buffer, fatigue impact.
- `SCHEDULE_EFFECT`: Task ETA, shift buffer, handoff alignment.
- `OUTCOME`: Final composite shift impact.

### 2.5 Human-in-the-Loop Design Principle
- **Advisory Prototype**: CAT Trajectory is strictly an operator decision-support companion.
- **No Autonomous Machine Control**: It never issues direct CAN-bus steering, boom, or throttle commands.
- **Non-Coercive**: The operator retains 100% authority to accept, decline, or choose an alternate path.
- **Explanatory Transparency**: Every recommendation exposes its full causal chain ("why") rather than acting as a black-box oracle.

### 2.6 Decision Memory & Prediction-vs-Actual Closed Loop
When an operator commits to a trajectory:
1. **Signature Hashing**: The operational context (machine model, operator experience tier, ground saturation, grade, weather, task type) is encoded into a deterministic `context_signature`.
2. **Memory Persistence**: The chosen scenario, predicted metrics, and operator rationale are stored in PostgreSQL.
3. **Outcome Auditing**: Upon task completion, real-world metrics are captured, and `prediction_error` is evaluated (`predicted_eta - actual_eta`, `predicted_fuel - actual_fuel`).
4. **Context Retrieval**: Future shifts matching the same context signature can retrieve proven decisions, displaying historical actual savings to build compounding operator trust.

---

## 3. Important Safety & Operational Positioning

> [!CAUTION]
> **Safety Boundary Notice**:
> - CAT Trajectory is a decision-support prototype built for demonstration.
> - It does NOT interface with machine safety interlocks, emergency stop circuits, or autonomous hydraulic control units.
> - Safety constraint violations trigger immediate scenario rejection (`constraint_status: REJECTED`) and are NEVER traded off against productivity or fuel savings.
> - Operator vigilance, cab visibility, and site safety protocols always supersede companion suggestions.

---

## 4. Synthetic Data Strategy & Limitations

Because high-frequency CAN-bus excavator data with labeled decision events is scarce in public hackathon environments:
- **Baseline Physics Calibration**: Telemetry is calibrated to published Caterpillar 349 Excavator and 740 GC Articulated Truck spec sheets (fuel burn at idle vs. high-load, swing cycle mechanics).
- **Synthetic Distribution Generators**: Deterministic stochastic generators simulate truck arrival variance (Poisson processes), ground saturation degradation (linear slope response), and operator fatigue curves.
- **Known Limitations**: Synthetic generators do not capture unpredictable geological anomalies, mechanical component wear, or complex multi-machine radio miscommunications. Real-world deployment requires continuous calibration against CAT Product Link™ feeds.
