/**
 * Frontend TypeScript interfaces conforming to /shared/contracts/*.schema.json
 */

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
  machine_id: string;
  timestamp: string;
  seatbelt_fastened: boolean;
  seatbelt_compliance_pct: number;
  proximity_warning_level: 'NONE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  active_hazard_count: number;
  overall_safety_score: number;
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
}

export interface DashboardResponse {
  operator_id: string;
  timestamp: string;
  shift_twin_summary: ShiftTwin;
  immediate_safety_status: SafetyStatus;
  top_training_recommendation?: TrainingRecommendation | null;
  active_alerts_count: number;
}
