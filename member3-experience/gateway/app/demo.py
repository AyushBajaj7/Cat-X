"""Deterministic Telemetry & Demo Engine for 'The 17-Minute Trap' (States 1 to 10)."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class DemoEngine:
    """Deterministic scenario runner for the CAT Operator Shift Twin demo."""

    def __init__(self):
        self.reset()

    def reset(self) -> Dict[str, Any]:
        """Reset the demo state to State 1 (Normal)."""
        self.current_step = 1
        self.operator_id = "OP1001"
        self.machine_id = "EXC-CAT-349D"
        self.task_id = "T002"
        self.chosen_scenario: Optional[str] = None
        self.operator_reason: Optional[str] = None
        self.reason_category: Optional[str] = None
        self.decision_committed_at: Optional[str] = None
        self.history: List[Dict[str, Any]] = []

        return {
            "status": "RESET_SUCCESSFUL",
            "scenario": "THE_17_MINUTE_TRAP",
            "current_step": 1,
            "step_name": "STATE 1: NORMAL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": "Demo state reset to State 1: Bench 2 normal shift baseline.",
        }

    def set_step(self, step_number: int) -> Dict[str, Any]:
        """Jump to a specific demo state (1-10)."""
        if step_number < 1 or step_number > 10:
            raise ValueError(f"Step number must be between 1 and 10, got {step_number}")
        self.current_step = step_number
        if step_number >= 7 and not self.chosen_scenario:
            self.chosen_scenario = "SCEN-02-RESEQUENCE"
            self.operator_reason = "Bypassed haul truck queue before rain onset."
            self.reason_category = "schedule"
            self.decision_committed_at = datetime.now(timezone.utc).isoformat()
        return self.get_current_state()

    def advance_step(self) -> Dict[str, Any]:
        """Advance to next demo step."""
        next_step = min(10, self.current_step + 1)
        return self.set_step(next_step)

    def record_choice(self, scenario_id: str, reason: str = "", reason_category: str = "schedule") -> Dict[str, Any]:
        """Record operator trajectory choice."""
        self.chosen_scenario = scenario_id
        self.operator_reason = reason or "Operator selected optimal recovery trajectory."
        self.reason_category = reason_category
        self.decision_committed_at = datetime.now(timezone.utc).isoformat()
        self.current_step = max(self.current_step, 7)
        return {
            "status": "RECORDED",
            "decision_id": f"DEC-{self.operator_id}-001",
            "scenario_id": self.chosen_scenario,
            "chosen_scenario": self.chosen_scenario,
            "operator_reason": self.operator_reason,
            "reason_category": self.reason_category,
            "timestamp": self.decision_committed_at,
            "message": "Trajectory choice committed to decision memory.",
        }

    def get_current_state(self) -> Dict[str, Any]:
        """Return full state representation for current demo step."""
        step = self.current_step
        now = datetime.now(timezone.utc).isoformat()

        # Step metadata definitions
        step_definitions = {
            1: {
                "name": "STATE 1: NORMAL",
                "title": "Normal Shift Baseline",
                "attention_mode": "NORMAL",
                "attention_reason": "Nominal operating parameters.",
                "summary": "Shift running smoothly on Bench 2. Seatbelt fastened, 0 proximity hazards, normal 9.8% idle, target pace 104.5%.",
                "seatbelt": True,
                "proximity_hazards": 0,
                "idle_pct": 9.8,
                "fuel_burn_rate_lph": 14.2,
                "safety_score": 98.0,
                "behaviour_score": 94.0,
                "decision_point_active": False,
                "top_action": {
                    "action_id": "NBA-01",
                    "title": "Maintain Production Pace",
                    "rationale": "Digging speed is 4.5% above baseline. Trench grade on schedule.",
                    "estimated_benefit": "On schedule for 14:00 shift handoff",
                    "priority": "NORMAL",
                },
                "training_rec": None,
            },
            2: {
                "name": "STATE 2: SEATBELT EVENT",
                "title": "Seatbelt Compliance Event",
                "attention_mode": "SAFETY_FOCUS",
                "attention_reason": "Seatbelt unfastened during machine operation.",
                "summary": "Operator unbuckled harness while adjusting seat during cycle pause. Visual alert illuminated.",
                "seatbelt": False,
                "proximity_hazards": 0,
                "idle_pct": 10.0,
                "fuel_burn_rate_lph": 14.2,
                "safety_score": 72.0,
                "behaviour_score": 88.0,
                "decision_point_active": False,
                "top_action": {
                    "action_id": "NBA-SAFE-01",
                    "title": "Fasten 3-Point Safety Harness",
                    "rationale": "Cab interlock detected unbuckled seatbelt during engine engagement.",
                    "estimated_benefit": "Restores full compliance streak",
                    "priority": "CRITICAL",
                },
                "training_rec": {
                    "module_id": "SAFE_START_01",
                    "module_title": "Safe Start Check",
                    "reason": "Seatbelt non-compliance detected. Review safe operating procedures and startup sequence before continuing.",
                    "urgency": "HIGH",
                },
            },
            3: {
                "name": "STATE 3: PROXIMITY EVENT",
                "title": "Proximity Hazard Trigger",
                "attention_mode": "SAFETY_FOCUS",
                "attention_reason": "Support vehicle within dynamic swing radius (14m < 15m threshold).",
                "summary": "Support utility vehicle approaches within 14m perimeter on blind counterweight side.",
                "seatbelt": True,
                "proximity_hazards": 1,
                "idle_pct": 10.2,
                "fuel_burn_rate_lph": 14.2,
                "safety_score": 68.0,
                "behaviour_score": 90.0,
                "decision_point_active": False,
                "top_action": {
                    "action_id": "NBA-PROX-01",
                    "title": "Halt Swing and Ground Bucket",
                    "rationale": "Support utility vehicle inside 15m exclusion boundary.",
                    "estimated_benefit": "Neutralizes collision hazard",
                    "priority": "CRITICAL",
                },
                "training_rec": {
                    "module_id": "PROXIMITY_RESPONSE_01",
                    "module_title": "Proximity Response",
                    "reason": "Proximity boundary alert triggered. Review site hazard identification and response guidelines.",
                    "urgency": "HIGH",
                },
            },
            4: {
                "name": "STATE 4: QUEUE IMBALANCE / HIGH IDLE",
                "title": "Haul Fleet Cycle Bunching & High Idle Spike",
                "attention_mode": "EFFICIENCY_FOCUS",
                "attention_reason": "Low-idle fuel burn spiking due to haul fleet cycle mismatch.",
                "summary": "Crusher bottleneck creates 18-minute haul truck arrival gap. Excavator idling at 1800 RPM (14.8% idle spike).",
                "seatbelt": True,
                "proximity_hazards": 0,
                "idle_pct": 14.8,
                "fuel_burn_rate_lph": 18.5,
                "safety_score": 96.0,
                "behaviour_score": 76.0,
                "decision_point_active": False,
                "top_action": {
                    "action_id": "NBA-IDLE-01",
                    "title": "Engage Auto-Idle Control or Pre-strip Overburden",
                    "rationale": "Truck gap at crusher is causing unproductive 18.5 L/hr fuel burn.",
                    "estimated_benefit": "Saves 18.5 L/hr fuel waste",
                    "priority": "HIGH",
                },
                "training_rec": {
                    "module_id": "IDLE_EFFICIENCY_01",
                    "module_title": "Idle Efficiency Response",
                    "reason": "Excessive low-idle operation observed. Review engine power management and queue mitigation techniques.",
                    "urgency": "MEDIUM",
                },
            },
            5: {
                "name": "STATE 5: DECISION POINT",
                "title": "Decision Point Detected: The 17-Minute Trap",
                "attention_mode": "DECISION_FOCUS",
                "attention_reason": "Haul fleet queue mismatch and rain front create compounding 17-minute delay trap.",
                "summary": "18-minute truck gap compounding with incoming rain front at 11:30 AM. Passive continuation guarantees a 17-minute shift overrun.",
                "seatbelt": True,
                "proximity_hazards": 0,
                "idle_pct": 14.8,
                "fuel_burn_rate_lph": 18.5,
                "safety_score": 98.0,
                "behaviour_score": 78.0,
                "decision_point_active": True,
                "top_action": {
                    "action_id": "ACT-EVAL-TRAJECTORY",
                    "title": "Compare Available Recovery Trajectories",
                    "rationale": "Current queue imbalance and incoming rain are projected to delay shift completion.",
                    "estimated_benefit": "Recover 17 minutes and avoid trench water accumulation",
                    "priority": "HIGH",
                },
                "training_rec": {
                    "module_id": "DECISION_AWARENESS_01",
                    "module_title": "Decision Awareness",
                    "reason": "Emergent tactical decision point encountered. Review consequence graphs and trajectory trade-offs.",
                    "urgency": "MEDIUM",
                },
            },
            6: {
                "name": "STATE 6: TRAJECTORY COMPARISON",
                "title": "Trajectory Alternatives & Consequence Graph",
                "attention_mode": "DECISION_FOCUS",
                "attention_reason": "Compare candidate trajectories: Continue, Resequence, or Reposition.",
                "summary": "Three candidate trajectories evaluated against safety constraints. Consequence graph visualizes causal chain.",
                "seatbelt": True,
                "proximity_hazards": 0,
                "idle_pct": 14.8,
                "fuel_burn_rate_lph": 18.5,
                "safety_score": 98.0,
                "behaviour_score": 78.0,
                "decision_point_active": True,
                "top_action": {
                    "action_id": "ACT-CHOOSE-TRAJECTORY",
                    "title": "Select Tactical Trajectory",
                    "rationale": "Trajectory B (Resequence) saves 17 min and 14.8L fuel with validated 8° slope safety.",
                    "estimated_benefit": "Finish 12 min early before rain onset",
                    "priority": "HIGH",
                },
                "training_rec": {
                    "module_id": "DECISION_AWARENESS_01",
                    "module_title": "Decision Awareness",
                    "reason": "Review alternative trajectories and understand consequence flows.",
                    "urgency": "MEDIUM",
                },
            },
            7: {
                "name": "STATE 7: OPERATOR CHOICE",
                "title": "Operator Decision Committed",
                "attention_mode": "PLANNING_FOCUS",
                "attention_reason": "Operator committed Trajectory B (Resequence to Upper Bench 3). Active task updated.",
                "summary": "Operator chose Trajectory B (RESEQUENCE). Rationale recorded: 'Bypassed haul truck queue before rain onset'.",
                "seatbelt": True,
                "proximity_hazards": 0,
                "idle_pct": 8.5,
                "fuel_burn_rate_lph": 16.0,
                "safety_score": 98.0,
                "behaviour_score": 92.0,
                "decision_point_active": False,
                "top_action": {
                    "action_id": "ACT-EXECUTE-BENCH3",
                    "title": "Execute Bench 3 Overburden Cut",
                    "rationale": "Pre-stripping 180 tons of soft soil into temporary stockpile.",
                    "estimated_benefit": "Soil pre-loosened before truck arrival",
                    "priority": "NORMAL",
                },
                "training_rec": None,
            },
            8: {
                "name": "STATE 8: OUTCOME REPLAY",
                "title": "Outcome Replay & Prediction Audit",
                "attention_mode": "NORMAL",
                "attention_reason": "Trajectory executed. Predicted outcome audited against simulated actual outcome.",
                "summary": "Simulation advances: 180 tons moved, trucks loaded at rapid pace. Predicted vs. simulated outcome shows high model accuracy.",
                "seatbelt": True,
                "proximity_hazards": 0,
                "idle_pct": 5.2,
                "fuel_burn_rate_lph": 15.1,
                "safety_score": 99.0,
                "behaviour_score": 95.0,
                "decision_point_active": False,
                "top_action": {
                    "action_id": "ACT-COMPLETE-STAGE",
                    "title": "Trench Ready for Final Handoff",
                    "rationale": "Overburden cleared, trucks dispatched, trench sealed before rain front.",
                    "estimated_benefit": "15.8 min actual time saved",
                    "priority": "NORMAL",
                },
                "training_rec": None,
            },
            9: {
                "name": "STATE 9: DECISION MEMORY",
                "title": "Decision Memory Stored",
                "attention_mode": "NORMAL",
                "attention_reason": "Decision context and validated outcome saved to organizational memory.",
                "summary": "Decision DEC-OP1001-001 with context signature SIG-BENCH2-WET-TRENCH saved in PostgreSQL decision store.",
                "seatbelt": True,
                "proximity_hazards": 0,
                "idle_pct": 5.2,
                "fuel_burn_rate_lph": 14.8,
                "safety_score": 99.0,
                "behaviour_score": 96.0,
                "decision_point_active": False,
                "top_action": {
                    "action_id": "ACT-REVIEW-MEMORY",
                    "title": "Decision Stored in Shift Twin Memory",
                    "rationale": "Historical evidence available for future similar context match.",
                    "estimated_benefit": "Organizational knowledge preserved",
                    "priority": "NORMAL",
                },
                "training_rec": None,
            },
            10: {
                "name": "STATE 10: SIMILAR CONTEXT",
                "title": "Similar Context Reuse in Future Shift",
                "attention_mode": "DECISION_FOCUS",
                "attention_reason": "Historical similar decision context detected: SIG-BENCH2-WET-TRENCH (94% match).",
                "summary": "In an upcoming shift, an operator encounters an excavator-truck mismatch under wet conditions. Past decision surfaced: Operator OP1001 saved 15.8 mins.",
                "seatbelt": True,
                "proximity_hazards": 0,
                "idle_pct": 13.5,
                "fuel_burn_rate_lph": 17.8,
                "safety_score": 98.0,
                "behaviour_score": 82.0,
                "decision_point_active": True,
                "top_action": {
                    "action_id": "ACT-REUSE-RESEQUENCE",
                    "title": "Apply Proven Trajectory B (Resequence)",
                    "rationale": "Similar historical shift DEC-OP1001-001 achieved 15.8 mins savings under identical wet conditions.",
                    "estimated_benefit": "Proven 15.8 min savings & 15.6L fuel reduction",
                    "priority": "HIGH",
                },
                "training_rec": {
                    "module_id": "DECISION_AWARENESS_01",
                    "module_title": "Decision Awareness",
                    "reason": "Similar decision pattern detected. Review the consequence mechanics before committing.",
                    "urgency": "MEDIUM",
                },
            },
        }

        info = step_definitions[step]

        # Trajectory Scenarios Data (for steps 5, 6, 7, 8, 9, 10)
        scenarios = self._get_scenarios_data()

        # Decision Point Data
        decision_point = {
            "decision_point_id": "DP-BENCH2-HAUL-01",
            "timestamp": "2026-09-23T10:45:00Z",
            "operator_id": self.operator_id,
            "machine_id": self.machine_id,
            "task_id": self.task_id,
            "trigger_type": "QUEUE_IMBALANCE",
            "severity": "HIGH",
            "summary": "Haul fleet cycle mismatch and incoming rain front create a projected 17-minute shift delay trap.",
            "evidence": {
                "truck_gap_projected_minutes": 18.2,
                "truck_queue_on_arrival": 4,
                "current_idle_pct": info["idle_pct"],
                "ground_saturation_trend_pct_per_hr": 12.0,
                "baseline_eta_delay_minutes": 17.4,
                "weather_alert": "Rain arriving at 11:30 AM (North Bench traction loss)",
            },
            "available_actions": ["ACT-CONTINUE", "ACT-RESEQUENCE", "ACT-REPOSITION"],
        } if info["decision_point_active"] or step in (5, 6, 7, 8, 9, 10) else None

        # Replay outcome data
        outcome_replay = {
            "status": "SIMULATED_COMPLETE",
            "decision_id": f"DEC-{self.operator_id}-001",
            "chosen_scenario": self.chosen_scenario or "SCEN-02-RESEQUENCE",
            "predicted_outcome": {
                "eta_minutes": 145.0,
                "fuel_liters": 168.0,
                "idle_minutes": 0.0,
                "shift_delay_minutes": -17.0,
            },
            "actual_outcome": {
                "eta_minutes": 146.5,
                "fuel_liters": 167.2,
                "idle_minutes": 1.2,
                "shift_delay_minutes": -15.8,
            },
            "simulated_actual_outcome": {
                "eta_minutes": 146.5,
                "fuel_liters": 167.2,
                "idle_minutes": 1.2,
                "shift_delay_minutes": -15.8,
            },
            "prediction_error": {
                "eta_delta_minutes": 1.5,
                "fuel_delta_liters": -0.8,
                "idle_delta_minutes": 1.2,
                "accuracy_pct": 98.9,
            },
            "error_audit": {
                "duration_error_minutes": 1.5,
                "fuel_delta_liters": -0.8,
                "accuracy_pct": 98.9,
            },
            "drift_status": "WITHIN_TOLERANCE",
            "is_simulated": True,
            "simulation_label": "SIMULATED OUTCOME — PROJECTION AUDITED",
        } if step >= 7 else None

        return {
            "demo_mode": True,
            "current_step": step,
            "total_steps": 10,
            "step_name": info["name"],
            "title": info["title"],
            "summary": info["summary"],
            "attention_mode": info["attention_mode"],
            "attention_reason": info["attention_reason"],
            "timestamp": now,
            "operator_id": self.operator_id,
            "machine_id": self.machine_id,
            "task_id": self.task_id,
            "seatbelt_fastened": info["seatbelt"],
            "active_hazard_count": info["proximity_hazards"],
            "idle_percentage": info["idle_pct"],
            "fuel_burn_rate_lph": info["fuel_burn_rate_lph"],
            "safety_score": info["safety_score"],
            "behaviour_score": info["behaviour_score"],
            "next_best_action": info["top_action"],
            "top_training_recommendation": info["training_rec"],
            "decision_point": decision_point,
            "scenarios": scenarios,
            "chosen_scenario": self.chosen_scenario,
            "operator_reason": self.operator_reason,
            "reason_category": self.reason_category,
            "outcome_replay": outcome_replay,
            "similar_context": self._get_similar_context_data() if step == 10 else None,
        }

    def _get_scenarios_data(self) -> List[Dict[str, Any]]:
        """Return the 3 candidate scenarios plus the safety-rejected constraint demonstration."""
        return [
            {
                "scenario_id": "SCEN-01-CONTINUE",
                "action_id": "ACT-CONTINUE",
                "title": "Trajectory A: CONTINUE (Baseline Drift)",
                "description": "Maintain bench stance and wait for delayed haul fleet at current excavator location.",
                "constraint_status": "FEASIBLE",
                "selectable": True,
                "predicted_outcome": {
                    "duration_minutes": 162.0,
                    "shift_delay_minutes": 17.0,
                    "fuel_liters": 184.0,
                    "idle_minutes": 18.0,
                    "productivity_tons_per_hr": 92.0,
                    "safety_risk_score": 18.0,
                    "time_saved_minutes": 0.0,
                    "fuel_saved_liters": 0.0,
                },
                "explanation": "Passive path; accumulates 18 min dead idle, rain arrives at 11:30 AM before trench seal, incurring 17 min handoff delay.",
                "why_trace": {
                    "signal": "Haul Fleet Delay at Crusher",
                    "value": "18.2 min gap",
                    "baseline": "4.5 min scheduled return",
                    "interpretation": "Waiting without re-sequencing forces 18 min dead idle at 1800 RPM.",
                    "source": "Haul Fleet GPS & Crusher Queue Telemetry",
                },
                "consequence_graph": {
                    "graph_id": "CG-CONTINUE-01",
                    "scenario_id": "SCEN-01-CONTINUE",
                    "root_action": "Maintain Bench Stance",
                    "summary": "Idle delay accumulates into unrecoverable 17-minute completion delay as rain degrades haul ramp traction.",
                    "nodes": [
                        {"node_id": "N1", "type": "DECISION", "title": "Maintain Stance", "value": "Awaiting trucks", "unit": "mode", "severity": "NEUTRAL", "explanation": "Operator remains passive on Bench 2."},
                        {"node_id": "N2", "type": "IDLE_EFFECT", "title": "Idle Spike", "value": "+18.2", "unit": "min", "severity": "WARNING", "explanation": "Engine idles at 1800 RPM awaiting trucks."},
                        {"node_id": "N3", "type": "FUEL_EFFECT", "title": "Fuel Waste", "value": "+5.8", "unit": "L", "severity": "WARNING", "explanation": "Hydraulic pumps churn with zero material displacement."},
                        {"node_id": "N4", "type": "SCHEDULE_EFFECT", "title": "Truck Platoon Queue", "value": "4 trucks", "unit": "queue", "severity": "WARNING", "explanation": "All 4 trucks arrive at once, causing haul road bottleneck."},
                        {"node_id": "N5", "type": "OUTCOME", "title": "Shift Delay", "value": "+17.0", "unit": "min", "severity": "CRITICAL", "explanation": "Trench floor unsealed when rain hits; misses 14:00 shift handoff."},
                    ],
                    "edges": [
                        {"source": "N1", "target": "N2", "relationship": "CAUSES", "explanation": "Truck delay forces excavator into prolonged standby."},
                        {"source": "N2", "target": "N3", "relationship": "INCREASES", "explanation": "High idle consumes fuel unproductively."},
                        {"source": "N2", "target": "N4", "relationship": "TRIGGERS", "explanation": "Platoon bunches on haul road entry narrow."},
                        {"source": "N4", "target": "N5", "relationship": "CAUSES", "explanation": "Compounded queue delays breach 14:00 deadline."},
                    ],
                },
            },
            {
                "scenario_id": "SCEN-02-RESEQUENCE",
                "action_id": "ACT-RESEQUENCE",
                "title": "Trajectory B: RESEQUENCE (Overburden Pre-Stripping)",
                "description": "Switch immediately to pre-stripping 180t overburden on Upper Bench 3; direct load trucks on return.",
                "constraint_status": "FEASIBLE",
                "selectable": True,
                "predicted_outcome": {
                    "duration_minutes": 145.0,
                    "shift_delay_minutes": -17.0,
                    "fuel_liters": 168.0,
                    "idle_minutes": 0.0,
                    "productivity_tons_per_hr": 118.0,
                    "safety_risk_score": 12.0,
                    "time_saved_minutes": 17.0,
                    "fuel_saved_liters": 14.8,
                },
                "explanation": "Clears 180t overburden during truck gap; soil loosened in advance cuts truck load time by 35s per truck; seals trench 12 min early.",
                "why_trace": {
                    "signal": "Upper Bench 3 Overburden Readiness",
                    "value": "8.0° slope grade",
                    "baseline": "15.0° max safety limit",
                    "interpretation": "Slope is validated safe; pre-stripping consumes zero dead idle and preps soil.",
                    "source": "Safety Slope Sensor & Operations Task Dispatch",
                },
                "consequence_graph": {
                    "graph_id": "CG-RESEQUENCE-01",
                    "scenario_id": "SCEN-02-RESEQUENCE",
                    "root_action": "Re-sequence to Bench 3 Cut",
                    "summary": "Pre-stripping eliminates idle waste, loosens bench soil in advance, and allows rapid truck clearance before rain.",
                    "nodes": [
                        {"node_id": "N1", "type": "DECISION", "title": "Pivot to Bench 3 Cut", "value": "180 tons", "unit": "tons", "severity": "BENEFICIAL", "explanation": "Operator shifts to Upper Bench 3 overburden cut."},
                        {"node_id": "N2", "type": "MACHINE_EFFECT", "title": "Optimal Power Band", "value": "100%", "unit": "load", "severity": "BENEFICIAL", "explanation": "Engine operates at peak hydraulic efficiency with zero dead idle."},
                        {"node_id": "N3", "type": "TASK_EFFECT", "title": "Soil Pre-loosened", "value": "-35", "unit": "sec/truck", "severity": "BENEFICIAL", "explanation": "Truck loading cycle cuts 35 seconds per bucket load."},
                        {"node_id": "N4", "type": "FUEL_EFFECT", "title": "Fuel Saved", "value": "-14.8", "unit": "L", "severity": "BENEFICIAL", "explanation": "Net fuel burn reduced across remaining shift tons."},
                        {"node_id": "N5", "type": "OUTCOME", "title": "Early Shift Completion", "value": "-12.0", "unit": "min", "severity": "BENEFICIAL", "explanation": "Trench sealed and completed 12 mins before rain onset."},
                    ],
                    "edges": [
                        {"source": "N1", "target": "N2", "relationship": "CAUSES", "explanation": "Shifting work keeps machine in continuous productive load."},
                        {"source": "N2", "target": "N3", "relationship": "ENABLES", "explanation": "Pre-loosened soil reduces bucket breakout resistance."},
                        {"source": "N3", "target": "N4", "relationship": "REDUCES", "explanation": "Faster truck filling cuts overall engine running time."},
                        {"source": "N4", "target": "N5", "relationship": "CAUSES", "explanation": "Absorbs truck queue and finishes before rain front arrives."},
                    ],
                },
            },
            {
                "scenario_id": "SCEN-03-REPOSITION",
                "action_id": "ACT-REPOSITION",
                "title": "Trajectory C: REPOSITION (Face Angle Optimization)",
                "description": "Walk machine 12m West along Bench 2 to reduce bucket swing arc from 48° to 32° and remark truck spotting cone.",
                "constraint_status": "FEASIBLE",
                "selectable": True,
                "predicted_outcome": {
                    "duration_minutes": 149.0,
                    "shift_delay_minutes": -13.0,
                    "fuel_liters": 172.0,
                    "idle_minutes": 4.0,
                    "productivity_tons_per_hr": 112.0,
                    "safety_risk_score": 14.0,
                    "time_saved_minutes": 13.0,
                    "fuel_saved_liters": 11.2,
                },
                "explanation": "4 min walk time; reduces swing arc by 16°; hydraulic slew pressure drops 14%; cycle time drops from 28.5s to 22.0s per pass.",
                "why_trace": {
                    "signal": "Highwall Edge Proximity",
                    "value": "6.5m standoff",
                    "baseline": "4.0m minimum safety margin",
                    "interpretation": "Reposition stance maintains safe highwall standoff while improving swing geometry.",
                    "source": "LiDAR Terrain & Proximity Sensor",
                },
                "consequence_graph": {
                    "graph_id": "CG-REPOSITION-01",
                    "scenario_id": "SCEN-03-REPOSITION",
                    "root_action": "Walk Machine 12m West",
                    "summary": "Reduced boom swing arc cuts cycle time by 6.5s per pass, absorbing the haul fleet queue.",
                    "nodes": [
                        {"node_id": "N1", "type": "DECISION", "title": "Walk 12m West", "value": "4 min walk", "unit": "min", "severity": "NEUTRAL", "explanation": "Operator re-aligns digging face by 15 degrees."},
                        {"node_id": "N2", "type": "MACHINE_EFFECT", "title": "Swing Arc Reduced", "value": "48° ➔ 32°", "unit": "deg", "severity": "BENEFICIAL", "explanation": "Slew motor hydraulic pressure drops 14%."},
                        {"node_id": "N3", "type": "TASK_EFFECT", "title": "Cycle Time Cut", "value": "28.5s ➔ 22.0s", "unit": "sec", "severity": "BENEFICIAL", "explanation": "Shaves 6.5s off every bucket pass."},
                        {"node_id": "N4", "type": "FUEL_EFFECT", "title": "Hydraulic Fuel Saved", "value": "-11.2", "unit": "L", "severity": "BENEFICIAL", "explanation": "Lower hydraulic strain across remaining 500 tons."},
                        {"node_id": "N5", "type": "OUTCOME", "title": "8 Min Early Finish", "value": "-8.0", "unit": "min", "severity": "BENEFICIAL", "explanation": "Faster truck turnaround clears queue before rain arrives."},
                    ],
                    "edges": [
                        {"source": "N1", "target": "N2", "relationship": "CAUSES", "explanation": "Repositioning face geometry tightens machine-to-truck swing arc."},
                        {"source": "N2", "target": "N3", "relationship": "SPEEDS_UP", "explanation": "Shorter swing path directly reduces cycle duration."},
                        {"source": "N3", "target": "N4", "relationship": "REDUCES", "explanation": "Faster cycles decrease total hydraulic pumping energy."},
                        {"source": "N4", "target": "N5", "relationship": "CAUSES", "explanation": "Platoon queue absorbed without shift delay."},
                    ],
                },
            },
            {
                "scenario_id": "SCEN-04-STEEP-CUT",
                "action_id": "ACT-STEEP-CUT",
                "title": "Trajectory D: STEEP CUT (Highwall Over-cut)",
                "description": "Attempt aggressive shortcut cut along North highwall crest to shorten haul distance.",
                "constraint_status": "REJECTED",
                "selectable": False,
                "rejection_reason": "REJECTED — SAFETY/OPERATIONAL CONSTRAINT",
                "constraint_detail": {
                    "constraint": "SLOPE_STABILITY_GRADE_LIMIT",
                    "value": "18.5° slope grade",
                    "threshold": "15.0° maximum permissible grade",
                    "explanation": "Cut geometry produces an 18.5° grade exceeding geotechnical slope stability threshold (15.0° max). Unsafe option rejected by safety constraint validator.",
                },
                "predicted_outcome": {
                    "duration_minutes": 140.0,
                    "shift_delay_minutes": -22.0,
                    "fuel_liters": 162.0,
                    "idle_minutes": 0.0,
                    "productivity_tons_per_hr": 125.0,
                    "safety_risk_score": 85.0,
                    "time_saved_minutes": 22.0,
                    "fuel_saved_liters": 22.0,
                },
                "explanation": "REJECTED — SAFETY/OPERATIONAL CONSTRAINT: Violates highwall stability limit. Safety constraints reject this trajectory deterministically; safety is never traded off for productivity.",
                "why_trace": {
                    "signal": "Highwall Slope Stability Model",
                    "value": "18.5° slope",
                    "baseline": "15.0° max stability limit",
                    "interpretation": "Slope instability breach triggers mandatory deterministic rejection.",
                    "source": "Safety Service Physical Constraint Engine",
                },
                "consequence_graph": {
                    "graph_id": "CG-STEEP-01",
                    "scenario_id": "SCEN-04-STEEP-CUT",
                    "root_action": "Steep Cut Shortcut",
                    "summary": "Candidate trajectory rejected by safety constraints.",
                    "nodes": [
                        {"node_id": "N1", "type": "DECISION", "title": "Steep Cut", "value": "18.5° cut", "unit": "deg", "severity": "CRITICAL", "explanation": "Attempted steep cut."},
                        {"node_id": "N2", "type": "SAFETY_EFFECT", "title": "Slope Failure Risk", "value": "BREACH", "unit": "status", "severity": "CRITICAL", "explanation": "Highwall slump risk exceeds threshold."},
                        {"node_id": "N3", "type": "OUTCOME", "title": "Rejected", "value": "REJECTED", "unit": "gate", "severity": "CRITICAL", "explanation": "Deterministic safety gate blocks recommendation."},
                    ],
                    "edges": [
                        {"source": "N1", "target": "N2", "relationship": "TRIGGERS", "explanation": "Exceeds 15° geotechnical limit."},
                        {"source": "N2", "target": "N3", "relationship": "REJECTS", "explanation": "Safety validator rejects candidate path."},
                    ],
                },
            },
        ]

    def _get_similar_context_data(self) -> Dict[str, Any]:
        """Return similar context matching data for State 10."""
        return {
            "similar_situation_found": True,
            "banner": "SIMILAR SITUATION FOUND",
            "historical_decision_id": "DEC-OP1001-001",
            "context_signature": "SIG-BENCH2-WET-TRENCH",
            "similarity_score_pct": 94.2,
            "previous_context": {
                "task": "Bench 2 Trenching & Excavation",
                "machine": "Caterpillar 349 Excavator",
                "weather": "Pre-rain front, ground saturation 24%",
                "dilemma": "4-truck queue bottleneck at primary crusher",
            },
            "previous_action": "RESEQUENCE — Pre-stripped 180t overburden on Upper Bench 3",
            "previous_prediction": "17 min saved, 14.8L fuel saved",
            "actual_result": "15.8 min actual time saved, 15.6L fuel saved, zero deadline delay",
            "key_learning": "Operator OP1001 saved 15.8 minutes and avoided rain flooding by pre-stripping Bench 3 overburden.",
            "operator_in_control_notice": "Advisory recommendation only. The operator remains in full control.",
            "recommended_training": {
                "module_id": "DECISION_AWARENESS_01",
                "title": "Decision Awareness",
                "reason": "Review historical consequence flows to validate tactical trajectory.",
            },
        }

    def get_shift_twin(self, operator_id: str = "OP1001") -> Dict[str, Any]:
        """Generate canonical 7-dimension Shift Twin conforming to shift-twin.schema.json."""
        info = self.get_current_state()
        return {
            "twin_id": f"TWIN-{operator_id}-LIVE",
            "operator_id": operator_id,
            "machine_id": self.machine_id,
            "current_task_id": self.task_id,
            "updated_at": info["timestamp"],
            "shift_health_score": round((info["safety_score"] + info["behaviour_score"]) / 2, 1),
            "attention_mode": info["attention_mode"],
            "attention_reason": info["attention_reason"],
            "environment": {
                "weather_condition": "RAIN_APPROACHING" if self.current_step >= 5 else "CLEAR",
                "ambient_temp_c": 18.0 if self.current_step >= 5 else 23.5,
                "ground_saturation_pct": 28.0 if self.current_step >= 5 else 12.0,
                "visibility_level": "MODERATE" if self.current_step >= 5 else "OPTIMAL",
            },
            "safety": {
                "seatbelt_status": info["seatbelt_fastened"],
                "seatbelt_compliance_pct": 72.0 if not info["seatbelt_fastened"] else 99.4,
                "active_proximity_hazards": info["active_hazard_count"],
                "safety_score": info["safety_score"],
            },
            "behaviour": {
                "idle_percentage": info["idle_percentage"],
                "aggressive_events_count": 0,
                "fatigue_risk_level": "LOW",
                "behaviour_score": info["behaviour_score"],
            },
            "productivity": {
                "completed_volume_tons": 500.0 if self.current_step >= 7 else 320.0,
                "target_volume_tons": 850.0,
                "pace_percentage": 118.0 if self.current_step >= 7 else 104.5,
                "efficiency_rating": "OPTIMAL" if self.current_step >= 7 else "NOMINAL",
            },
            "prediction": {
                "estimated_completion_time": "2026-09-23T13:48:00Z" if self.current_step >= 7 else "2026-09-23T14:17:00Z",
                "estimated_remaining_minutes": 145.0 if self.current_step >= 7 else 162.0,
                "delay_probability_pct": 8.0 if self.current_step >= 7 else 82.0,
                "confidence_score": 0.94,
            },
            "next_best_actions": [
                {
                    "action_id": info["next_best_action"]["action_id"],
                    "title": info["next_best_action"]["title"],
                    "rationale": info["next_best_action"]["rationale"],
                    "category": "EFFICIENCY" if "Idle" in info["next_best_action"]["title"] or "Trajectory" in info["next_best_action"]["title"] else "SAFETY",
                    "priority": info["next_best_action"].get("priority", "HIGH"),
                    "estimated_benefit": info["next_best_action"].get("estimated_benefit", "Optimizes shift completion"),
                }
            ],
        }


demo_engine = DemoEngine()
