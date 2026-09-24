/**
 * Centralized API client connecting Frontend strictly to API Gateway (Port 8080).
 * Rule: Zero business math in React; frontend strictly renders gateway responses.
 */

import {
  DashboardResponse,
  DecisionMemory,
  DemoState,
  OutcomeReplay,
  SafetyAlert,
  SafetyStatus,
  ShiftTwin,
  SimilarContext,
  Task,
  TaskEstimate,
  TrainingAttempt,
  TrainingModule,
  TrainingProgress,
  TrainingRecommendation,
  TrajectoryScenario,
  WhatIfResult,
} from '../types';

const getApiBaseUrl = (): string => {
  const envUrl = (import.meta as any).env?.VITE_API_BASE_URL;
  if (envUrl && typeof envUrl === 'string' && envUrl.startsWith('http')) {
    return envUrl;
  }
  // If hosted on Render, Vercel, or any remote domain, point to the live Render gateway
  if (
    typeof window !== 'undefined' &&
    window.location.hostname !== 'localhost' &&
    window.location.hostname !== '127.0.0.1'
  ) {
    return 'https://cat-gateway.onrender.com/api/v1';
  }
  // Local development fallback
  return 'http://localhost:8080/api/v1';
};

const API_BASE_URL = getApiBaseUrl();

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), 6000);
  try {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    });
    clearTimeout(id);
    if (!res.ok) {
      const errorBody = await res.json().catch(() => ({}));
      throw new Error(errorBody.detail || `Request failed with status ${res.status}`);
    }
    return res.json();
  } catch (err: any) {
    clearTimeout(id);
    if (err.name === 'AbortError') {
      throw new Error(`Gateway timeout connecting to ${endpoint}`);
    }
    throw err;
  }
}

// ----------------------------------------------------------------------
// Dashboard & Shift Twin
// ----------------------------------------------------------------------

export async function fetchDashboard(operatorId: string = 'OP1001'): Promise<DashboardResponse> {
  return request<DashboardResponse>(`/dashboard/${operatorId}`);
}

export async function fetchShiftTwin(operatorId: string = 'OP1001'): Promise<ShiftTwin> {
  return request<ShiftTwin>(`/shift/${operatorId}`);
}

export async function sendTelemetry(event: Record<string, unknown>): Promise<{ status: string }> {
  return request<{ status: string }>('/telemetry', {
    method: 'POST',
    body: JSON.stringify(event),
  });
}

// ----------------------------------------------------------------------
// Tasks & What-If
// ----------------------------------------------------------------------

export async function fetchTasks(): Promise<Task[]> {
  return request<Task[]>('/tasks');
}

export async function fetchTask(taskId: string): Promise<Task> {
  return request<Task>(`/tasks/${taskId}`);
}

export async function estimateTask(payload: Record<string, any>): Promise<TaskEstimate> {
  return request<TaskEstimate>('/tasks/estimate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function simulateWhatIf(payload: Record<string, any>): Promise<WhatIfResult> {
  return request<WhatIfResult>('/tasks/what-if', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// ----------------------------------------------------------------------
// Safety
// ----------------------------------------------------------------------

export async function fetchSafetyStatus(operatorId: string = 'OP1001'): Promise<SafetyStatus> {
  return request<SafetyStatus>(`/safety/status/${operatorId}`);
}

export async function fetchSafetyAlerts(operatorId: string = 'OP1001'): Promise<SafetyAlert[]> {
  return request<SafetyAlert[]>(`/safety/alerts/${operatorId}`);
}

export async function fetchSafetyIncidents(operatorId: string = 'OP1001'): Promise<any[]> {
  return request<any[]>(`/safety/incidents/${operatorId}`);
}

export async function fetchSafetyBehaviour(operatorId: string = 'OP1001'): Promise<any> {
  return request<any>(`/safety/behaviour/${operatorId}`);
}

// ----------------------------------------------------------------------
// Training
// ----------------------------------------------------------------------

export async function fetchTrainingModules(): Promise<TrainingModule[]> {
  return request<TrainingModule[]>('/training/modules');
}

export async function fetchTrainingModule(moduleId: string): Promise<TrainingModule> {
  return request<TrainingModule>(`/training/modules/${moduleId}`);
}

export async function fetchTrainingRecommendations(
  operatorId: string = 'OP1001',
  signal?: string
): Promise<TrainingRecommendation[]> {
  const query = signal ? `?signal=${encodeURIComponent(signal)}` : '';
  return request<TrainingRecommendation[]>(`/training/recommendations/${operatorId}${query}`);
}

export async function submitTrainingAttempt(payload: Record<string, any>): Promise<TrainingAttempt> {
  return request<TrainingAttempt>('/training/attempts', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchTrainingProgress(operatorId: string = 'OP1001'): Promise<TrainingProgress> {
  return request<TrainingProgress>(`/training/progress/${operatorId}`);
}

// ----------------------------------------------------------------------
// CAT Trajectory & Decision Memory
// ----------------------------------------------------------------------

export async function fetchCurrentTrajectory(operatorId: string = 'OP1001'): Promise<any> {
  return request<any>(`/trajectory/current/${operatorId}`);
}

export async function detectDecisionPoint(payload: Record<string, any>): Promise<any> {
  return request<any>('/trajectory/detect', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function evaluateTrajectories(payload: Record<string, any>): Promise<{ scenarios: TrajectoryScenario[] }> {
  return request<{ scenarios: TrajectoryScenario[] }>('/trajectory/evaluate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function chooseTrajectory(payload: {
  operator_id: string;
  scenario_id: string;
  operator_reason?: string;
  reason_category?: string;
}): Promise<any> {
  return request<any>('/trajectory/choose', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function recordOutcome(payload: Record<string, any>): Promise<OutcomeReplay> {
  return request<OutcomeReplay>('/trajectory/outcome', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchDecisionMemory(operatorId: string = 'OP1001'): Promise<DecisionMemory[]> {
  return request<DecisionMemory[]>(`/trajectory/memory/${operatorId}`);
}

export async function fetchSimilarTrajectories(operatorId: string = 'OP1001'): Promise<SimilarContext[]> {
  return request<SimilarContext[]>(`/trajectory/similar/${operatorId}`);
}

// ----------------------------------------------------------------------
// Deterministic Demo Controls ("The 17-Minute Trap")
// ----------------------------------------------------------------------

export async function resetDemo(): Promise<any> {
  return request<any>('/demo/reset', { method: 'POST' });
}

export async function fetchDemoState(): Promise<DemoState> {
  return request<DemoState>('/demo/state');
}

export async function setDemoStep(step?: number): Promise<DemoState> {
  return request<DemoState>('/demo/step', {
    method: 'POST',
    body: JSON.stringify(step !== undefined ? { step } : {}),
  });
}

export async function sendVoiceCommand(payload: {
  operator_id?: string;
  query_text: string;
}): Promise<any> {
  return request<any>('/voice/command', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export const apiClient = {
  getSafetyIncidents: fetchSafetyIncidents,
  sendVoiceCommand,
};

