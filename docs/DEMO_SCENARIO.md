# Demo Scenario: "The 17-Minute Trap"

> **Context**: Bench 2 Deep Trenching & Excavation (Task `T002`)  
> **Machine**: Caterpillar 349 Hydraulic Excavator (`EXC-CAT-001`)  
> **Operator**: Shift Operator OP1001 (Intermediate Tier)  
> **Fleet Context**: 4 x CAT 740 GC Articulated Trucks cycling between Bench 2 and Crusher Stockpile  

---

## 1. Scenario Premise & The Emerging Dilemma

At 10:45 AM (Hour 3.5 into an 8-hour shift), Operator OP1001 is on schedule, having excavated 320 tons of a required 850-ton trench section. 

However, three distinct environmental and operational variables begin compounding simultaneously:

1. **Haul Fleet Cycle Bunching**: A 12-minute bottleneck at the primary crusher has caused all four haul trucks to bunch together on the haul road return leg, creating an impending 20-minute gap followed by a simultaneous 4-truck queue.
2. **Elevated Low-Idle Spikes**: During the truck gap, the excavator remains running at high engine idle (1800 RPM) while waiting, causing unproductive fuel consumption of ~18.5 L/hr.
3. **Approaching Weather Front**: Site weather sensors detect incoming rainfall (cloud ceiling dropping, ambient temperature dropping from 24°C to 18°C, ground saturation rising from 14% to 28% in North Bench).
4. **The Latent Compounding Trap**:
   - If the operator remains passive, the truck bunching will force 17 minutes of dead idle time in the next hour.
   - Ground saturation will degrade the haul ramp grade traction by 11:30 AM, adding 3.5 minutes per return trip.
   - Combined, this guarantees an unrecoverable **17-minute completion delay**, pushing the trench past the 14:00 shift handoff and risking overnight water accumulation in the unsealed trench.

---

## 2. Decision Point Trigger (`DP-BENCH2-HAUL-01`)

The **CAT Trajectory Decision-Point Engine** evaluates incoming telemetry, detects the impending threshold breach, and elevates the Operator Cockpit into **`DECISION_FOCUS` attention mode**:

```json
{
  "decision_point_id": "DP-BENCH2-HAUL-01",
  "timestamp": "2026-09-23T10:45:00Z",
  "operator_id": "OP1001",
  "machine_id": "EXC-CAT-001",
  "task_id": "T002",
  "trigger_type": "QUEUE_IMBALANCE",
  "severity": "HIGH",
  "summary": "Haul fleet cycle mismatch and incoming rain front create a projected 17-minute shift delay trap.",
  "evidence": {
    "truck_gap_projected_minutes": 18.2,
    "truck_queue_on_arrival": 4,
    "current_idle_pct": 14.8,
    "ground_saturation_trend_pct_per_hr": 12.0,
    "baseline_eta_delay_minutes": 17.4
  },
  "available_actions": ["ACT-CONTINUE", "ACT-RESEQUENCE", "ACT-REPOSITION"]
}
```

---

## 3. The Three Candidate Trajectories

CAT Trajectory generates and evaluates three safe candidate trajectories for the operator:

### Trajectory 1: CONTINUE (Baseline Drift)
- **Concept**: The operator maintains current digging position and awaits haul fleet arrival as scheduled.
- **Safety Status**: `FEASIBLE` (No immediate mechanical hazard).
- **Causal Consequence**:
  - `DECISION` ➔ Maintain bench stance.
  - `MACHINE_EFFECT` ➔ Excavator idle continues for 18 minutes; hydraulic pumps churn under low load.
  - `FUEL_EFFECT` ➔ 5.8 liters of fuel wasted at idle with zero material displacement.
  - `SCHEDULE_EFFECT` ➔ 4 haul trucks arrive simultaneously; trucks queue on haul road narrow, creating secondary idle.
  - `ENVIRONMENT_EFFECT` ➔ Rain begins at 11:30 AM while trench floor is still exposed; material slumping increases.
  - `OUTCOME` ➔ **17-minute delay past shift deadline**; +16.2L excess fuel burn; trench unsealed at handoff.

### Trajectory 2: RESEQUENCE (Overburden Pre-Stripping)
- **Concept**: While the haul trucks are delayed at the crusher, the operator switches immediately from truck-loading to pre-stripping 180 tons of soft overburden from Upper Bench 3 into a temporary bench stock. When the truck fleet arrives, high-volume direct loading can resume at maximum pace.
- **Safety Status**: `FEASIBLE` (Upper bench slope validated at 8° grade, well below the 15° safety limit).
- **Causal Consequence**:
  - `DECISION` ➔ Re-sequence to Upper Bench 3 overburden cut for 18 minutes.
  - `MACHINE_EFFECT` ➔ Engine operates at optimal power band; 0% wasted idle.
  - `TASK_EFFECT` ➔ 180 tons of overburden cleared ahead of schedule; bench ready for rapid trenching.
  - `SCHEDULE_EFFECT` ➔ When truck platoon arrives, excavator is in position with pre-loosened soil, cutting truck load time by 35 seconds per truck.
  - `ENVIRONMENT_EFFECT` ➔ Critical trench section completed before heavy rainfall onset at 11:30 AM.
  - `OUTCOME` ➔ **Task completed 12 minutes ahead of deadline**; 14.8L net fuel saved; zero queue congestion.

### Trajectory 3: REPOSITION (Face Angle & Truck Spotting Optimization)
- **Concept**: The operator spends 4 minutes walking the excavator 12 meters along Bench 2 to realign the digging face by 15° West and re-marks the truck spotting cone with the bucket tip.
- **Safety Status**: `FEASIBLE` (Distance to highwall edge maintained at 6.5m, above the 4.0m minimum safety margin).
- **Causal Consequence**:
  - `DECISION` ➔ Walk machine 12m West and pivot digging face 15°.
  - `MACHINE_EFFECT` ➔ Swing angle reduced from 48° to 32°; slew motor hydraulic pressure drops 14%.
  - `TASK_EFFECT` ➔ Dig-and-dump cycle time reduced from 28.5s to 22.0s per bucket pass.
  - `FUEL_EFFECT` ➔ Reduced hydraulic strain saves ~4.2L per remaining 500 tons.
  - `SCHEDULE_EFFECT` ➔ Faster cycles absorb the truck platoon with minimal wait time per truck.
  - `OUTCOME` ➔ **Task completed 8 minutes ahead of deadline**; 11.2L net fuel saved; reduced operator fatigue.

---

## 4. Operator Interaction & Closed-Loop Memory Recording

1. **Cockpit Presentation**:
   - The Operator Cockpit shifts to `DECISION_FOCUS`.
   - The three trajectories appear as interactive comparison cards displaying forecasted ETA, fuel savings, and safety risk scores.
   - The operator clicks "Inspect Consequence Graph" to view the causal chain explaining how idle waste turns into shift delay.
2. **Operator Choice**:
   - Operator OP1001 selects **Trajectory 2: RESEQUENCE**.
   - A single-touch confirmation commits the selection.
3. **Execution & Telemetry Tracking**:
   - The task dashboard dynamically updates active target sub-task to "Bench 3 Overburden Pre-strip".
   - Telemetry tracks continuous engine load and bucket volume.
4. **Decision Memory Logged**:
   - The choice, context signature (`SIG-BENCH2-WET-TRENCH`), predicted metrics, and actual measured outcomes are stored in Decision Memory.
   - If another operator faces an excavator-truck queue mismatch on Bench 2 under wet conditions, CAT Trajectory will reference this recorded shift memory: *"Operator OP1001 saved 17 minutes and 14.8L fuel by re-sequencing to Bench 3 overburden."*
