/**
 * Frontend TypeScript interfaces conforming to shared contracts and API Gateway specifications.
 */

export type AttentionMode =
  | 'NORMAL'
  | 'SAFETY_FOCUS'
  | 'DECISION_FOCUS'
  | 'PLANNING_FOCUS'
  | 'EFFICIENCY_FOCUS'
  | 'TRAINING_FOCUS';

export interface NextBestAction {
  action_id: string;
  title: string;
  rationale: string;
  category: 'SAFETY' | 'EFFICIENCY' | 'MAINTENANCE' | 'TRAINING';
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'CRITICAL';
  estimated_benefit?: string;
}

export interface ShiftTwin {
  twin_id: string;
  operator_id: string;
  machine_id: string;
  current_task_id?: string | null;
  updated_at: string;
  shift_health_score: number;
  attention_mode?: AttentionMode;
  attention_reason?: string;
  environment: {
    weather_condition: string;
    ambient_temp_c: number;
    ground_saturation_pct: number;
    visibility_level?: string;
  };
  safety: {
    seatbelt_status: boolean;
    seatbelt_compliance_pct: number;
    active_proximity_hazards?: number;
    safety_score: number;
  };
  behaviour: {
    idle_percentage: number;
    aggressive_events_count?: number;
    fatigue_risk_level?: 'LOW' | 'MODERATE' | 'HIGH';
    behaviour_score: number;
  };
  productivity: {
    completed_volume_tons: number;
    target_volume_tons: number;
    pace_percentage: number;
    efficiency_rating?: string;
  };
  prediction: {
    estimated_completion_time: string;
    estimated_remaining_minutes: number;
    delay_probability_pct?: number;
    confidence_score: number;
  };
  next_best_actions: NextBestAction[];
}

export interface SafetyStatus {
  operator_id: string;
  machine_id?: string;
  timestamp: string;
  seatbelt_fastened: boolean;
  seatbelt_compliance_pct: number;
  proximity_warning_level: 'NONE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  active_hazard_count: number;
  overall_safety_score: number;
  status?: string;
  error?: string;
}

export interface SafetyAlert {
  alert_id: string;
  operator_id: string;
  timestamp: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  message: string;
  acknowledged?: boolean;
}

export interface Task {
  task_id: string;
  title: string;
  description?: string;
  site_zone: string;
  target_volume_tons: number;
  completed_volume_tons: number;
  status: 'PENDING' | 'IN_PROGRESS' | 'PAUSED' | 'COMPLETED';
  priority: 'LOW' | 'NORMAL' | 'HIGH' | 'CRITICAL';
  estimated_duration_minutes: number;
  scheduled_duration_minutes?: number;
  actual_duration_minutes?: number | null;
  p10_minutes?: number;
  p90_minutes?: number;
}

export interface TaskEstimate {
  task_id: string;
  estimated_remaining_minutes: number;
  estimated_completion_time: string;
  confidence_score: number;
  p10_minutes?: number;
  p90_minutes?: number;
}

export interface WhatIfResult {
  task_id: string;
  simulated_parameters: Record<string, any>;
  time_saved_minutes: number;
  fuel_saved_liters: number;
  predicted_shift_delay_minutes: number;
  summary: string;
}

export interface ScenarioChoice {
  choice_id: string;
  text: string;
  is_correct: boolean;
  explanation: string;
}

export interface ScenarioStep {
  step_number: number;
  title: string;
  prompt: string;
  choices: ScenarioChoice[];
}

export interface TrainingModule {
  module_id: string;
  title: string;
  description: string;
  objective: string;
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | string;
  estimated_minutes: number;
  skills: string[];
  steps: string[];
  scenario_steps?: ScenarioStep[];
  category?: string;
}

export interface TrainingRecommendation {
  recommendation_id: string;
  operator_id: string;
  module_id: string;
  module_title: string;
  urgency: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  trigger_source: string;
  reason: string;
  recommended_at: string;
  signal?: string;
}

export interface TrainingAttempt {
  attempt_id: string;
  operator_id: string;
  module_id: string;
  started_at: string;
  completed_at: string;
  score: number;
  max_score: number;
  percentage: number;
  mistakes: number;
  passed: boolean;
  status: string;
  feedback?: string;
}

export interface TrainingProgress {
  operator_id: string;
  completed_modules_count: number;
  average_score_pct: number;
  certifications_earned: string[];
  last_activity_at: string;
}

export interface ConsequenceNode {
  node_id: string;
  type:
    | 'DECISION'
    | 'MACHINE_EFFECT'
    | 'TASK_EFFECT'
    | 'FUEL_EFFECT'
    | 'IDLE_EFFECT'
    | 'PRODUCTIVITY_EFFECT'
    | 'SAFETY_EFFECT'
    | 'SCHEDULE_EFFECT'
    | 'OUTCOME';
  title: string;
  value: string | number;
  unit: string;
  severity: 'BENEFICIAL' | 'NEUTRAL' | 'WARNING' | 'CRITICAL';
  explanation: string;
}

export interface ConsequenceEdge {
  source: string;
  target: string;
  relationship: string;
  explanation: string;
}

export interface ConsequenceGraph {
  graph_id: string;
  scenario_id: string;
  root_action: string;
  summary: string;
  nodes: ConsequenceNode[];
  edges: ConsequenceEdge[];
}

export interface WhyDecisionTrace {
  signal: string;
  value: string;
  baseline: string;
  interpretation: string;
  source: string;
}

export interface ConstraintDetail {
  constraint: string;
  value: string;
  threshold: string;
  explanation: string;
}

export interface TrajectoryScenario {
  scenario_id: string;
  action_id: string;
  title: string;
  description: string;
  constraint_status: 'FEASIBLE' | 'REJECTED';
  selectable: boolean;
  rejection_reason?: string;
  constraint_detail?: ConstraintDetail;
  predicted_outcome: {
    duration_minutes?: number;
    shift_delay_minutes: number;
    fuel_liters: number;
    idle_minutes?: number;
    productivity_tons_per_hr?: number;
    safety_risk_score: number;
    time_saved_minutes: number;
    fuel_saved_liters: number;
  };
  explanation: string;
  why_trace?: WhyDecisionTrace;
  consequence_graph?: ConsequenceGraph;
}

export interface DecisionPoint {
  decision_point_id: string;
  timestamp: string;
  operator_id: string;
  machine_id: string;
  task_id: string;
  trigger_type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  summary: string;
  evidence: Record<string, any>;
  available_actions: string[];
}

export interface OutcomeReplay {
  decision_id: string;
  chosen_scenario: string;
  predicted_outcome: {
    eta_minutes: number;
    fuel_liters: number;
    idle_minutes: number;
    shift_delay_minutes: number;
  };
  actual_outcome: {
    eta_minutes: number;
    fuel_liters: number;
    idle_minutes: number;
    shift_delay_minutes: number;
  };
  prediction_error: {
    eta_delta_minutes: number;
    fuel_delta_liters: number;
    idle_delta_minutes?: number;
    accuracy_pct?: number;
  };
  drift_status: string;
  is_simulated: boolean;
  simulation_label: string;
}

export interface DecisionMemory {
  decision_id: string;
  operator_id: string;
  machine_id: string;
  task_id: string;
  timestamp: string;
  context_signature: string;
  available_scenarios: string[];
  chosen_scenario: string;
  predicted_outcome: Record<string, any>;
  actual_outcome: Record<string, any> | null;
  prediction_error: Record<string, any> | null;
  operator_reason: string;
  source: string;
}

export interface SimilarContext {
  similar_situation_found: boolean;
  banner: string;
  historical_decision_id: string;
  context_signature: string;
  similarity_score_pct: number;
  previous_context: {
    task: string;
    machine: string;
    weather: string;
    dilemma: string;
  };
  previous_action: string;
  previous_prediction: string;
  actual_result: string;
  key_learning: string;
  operator_in_control_notice: string;
  recommended_training?: {
    module_id: string;
    title: string;
    reason: string;
  };
}

export interface DashboardResponse {
  operator_id: string;
  timestamp: string;
  shift_twin_summary: ShiftTwin;
  immediate_safety_status: SafetyStatus;
  top_training_recommendation?: TrainingRecommendation | null;
  active_alerts_count: number;
  attention_mode: AttentionMode;
  attention_reason: string;
  demo_step?: number;
  demo_step_name?: string;
}

export interface DemoState {
  demo_mode: boolean;
  current_step: number;
  total_steps: number;
  step_name: string;
  title: string;
  summary: string;
  attention_mode: AttentionMode;
  attention_reason: string;
  timestamp: string;
  operator_id: string;
  machine_id: string;
  task_id: string;
  seatbelt_fastened: boolean;
  active_hazard_count: number;
  idle_percentage: number;
  fuel_burn_rate_lph: number;
  safety_score: number;
  behaviour_score: number;
  next_best_action: NextBestAction;
  top_training_recommendation?: {
    module_id: string;
    module_title: string;
    reason: string;
    urgency: string;
  } | null;
  decision_point?: DecisionPoint | null;
  scenarios: TrajectoryScenario[];
  chosen_scenario?: string | null;
  operator_reason?: string | null;
  reason_category?: string | null;
  outcome_replay?: OutcomeReplay | null;
  similar_context?: SimilarContext | null;
}
