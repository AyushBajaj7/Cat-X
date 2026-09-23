/**
 * Centralized API client connecting Frontend to API Gateway (Port 8000).
 * Adheres to rule: Frontend is strictly a consumer of backend services.
 */

import { DashboardResponse, ShiftTwin, Task } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export async function fetchDashboard(operatorId: string = 'OP1001'): Promise<DashboardResponse> {
  const res = await fetch(`${API_BASE_URL}/dashboard/${operatorId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch dashboard: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchShiftTwin(operatorId: string = 'OP1001'): Promise<ShiftTwin> {
  const res = await fetch(`${API_BASE_URL}/shift/${operatorId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch shift twin: ${res.statusText}`);
  }
  return res.json();
}

export async function sendTelemetry(event: Record<string, unknown>): Promise<{ status: string }> {
  const res = await fetch(`${API_BASE_URL}/telemetry`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(event),
  });
  if (!res.ok) {
    throw new Error(`Failed to send telemetry: ${res.statusText}`);
  }
  return res.json();
}
