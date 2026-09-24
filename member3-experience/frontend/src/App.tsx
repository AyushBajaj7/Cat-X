import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import {
  fetchDashboard,
  fetchDemoState,
  setDemoStep,
  resetDemo,
  fetchTasks,
  fetchSafetyStatus,
  fetchSafetyAlerts,
  fetchTrainingModules,
  fetchTrainingRecommendations,
  fetchTrainingProgress,
  chooseTrajectory,
  fetchDecisionMemory,
  fetchSimilarTrajectories,
} from './api/client';
import {
  DashboardResponse,
  DecisionMemory,
  DemoState,
  SafetyAlert,
  SafetyStatus,
  SimilarContext,
  Task,
  TrainingModule,
  TrainingProgress,
  TrainingRecommendation,
} from './types';
import { DemoControlBar } from './components/layout/DemoControlBar';
import { CabHeader } from './components/layout/CabHeader';
import { CabFooter } from './components/layout/CabFooter';
import { ShiftCockpit } from './components/shift/ShiftCockpit';
import { TasksScreen } from './components/tasks/TasksScreen';
import { SafetyScreen } from './components/safety/SafetyScreen';
import { MachineScreen } from './components/machine/MachineScreen';
import { InsightsScreen } from './components/insights/InsightsScreen';
import { TrajectoryScreen } from './components/trajectory/TrajectoryScreen';
import { TrainingHubScreen } from './components/training/TrainingHubScreen';
import {
  getFallbackDemoState,
  getFallbackDashboard,
  getFallbackTasks,
  getFallbackSafetyAlerts,
  getFallbackDecisionMemories,
  getFallbackSimilarContext,
} from './api/demoFallback';
import { TrainingScenarioPlayer } from './components/training/TrainingScenarioPlayer';
import { DecisionMemoryScreen } from './components/decisions/DecisionMemoryScreen';
import { WhatIfPage } from './pages/WhatIfPage';

export const App: React.FC = () => {
  const [demoState, setDemoState] = useState<DemoState>(() => getFallbackDemoState(1));
  const [dashboard, setDashboard] = useState<DashboardResponse>(() => getFallbackDashboard(1));
  const [tasks, setTasks] = useState<Task[]>(() => getFallbackTasks());
  const [safety, setSafety] = useState<SafetyStatus | null>(() => getFallbackDashboard(1).immediate_safety_status);
  const [alerts, setAlerts] = useState<SafetyAlert[]>([]);
  const [modules, setModules] = useState<TrainingModule[]>([]);
  const [recommendations, setRecommendations] = useState<TrainingRecommendation[]>([]);
  const [progress, setProgress] = useState<TrainingProgress | null>(null);
  const [memories, setMemories] = useState<DecisionMemory[]>(() => getFallbackDecisionMemories());
  const [similarContext, setSimilarContext] = useState<SimilarContext | null>(() => getFallbackSimilarContext());
  const [loading, setLoading] = useState<boolean>(false);

  const loadData = useCallback(async () => {
    try {
      const [
        demoRes,
        dashRes,
        tasksRes,
        safetyRes,
        alertsRes,
        modRes,
        recRes,
        progRes,
        memRes,
        simRes,
      ] = await Promise.allSettled([
        fetchDemoState(),
        fetchDashboard('OP1001'),
        fetchTasks(),
        fetchSafetyStatus('OP1001'),
        fetchSafetyAlerts('OP1001'),
        fetchTrainingModules(),
        fetchTrainingRecommendations('OP1001'),
        fetchTrainingProgress('OP1001'),
        fetchDecisionMemory('OP1001'),
        fetchSimilarTrajectories('OP1001'),
      ]);

      if (demoRes.status === 'fulfilled' && demoRes.value) setDemoState(demoRes.value);
      if (dashRes.status === 'fulfilled' && dashRes.value) setDashboard(dashRes.value);
      if (tasksRes.status === 'fulfilled' && tasksRes.value?.length) setTasks(tasksRes.value);
      if (safetyRes.status === 'fulfilled' && safetyRes.value) setSafety(safetyRes.value);
      if (alertsRes.status === 'fulfilled' && alertsRes.value) setAlerts(alertsRes.value);
      if (modRes.status === 'fulfilled' && modRes.value) setModules(modRes.value);
      if (recRes.status === 'fulfilled' && recRes.value) setRecommendations(recRes.value);
      if (progRes.status === 'fulfilled' && progRes.value) setProgress(progRes.value);
      if (memRes.status === 'fulfilled' && memRes.value?.length) setMemories(memRes.value);
      if (simRes.status === 'fulfilled' && simRes.value?.length > 0) {
        setSimilarContext(simRes.value[0]);
      }
    } catch {
      // Degraded/offline fallback already initialized
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleStepChange = async (step: number) => {
    // 1. Instant optimistic update so UI transitions with 0ms lag
    const optimisticDemo = getFallbackDemoState(step, demoState?.chosen_scenario || undefined);
    setDemoState(optimisticDemo);
    const optimisticDash = getFallbackDashboard(step, demoState?.chosen_scenario || undefined);
    setDashboard(optimisticDash);
    setSafety(optimisticDash.immediate_safety_status);
    setAlerts(getFallbackSafetyAlerts(step));
    if (step >= 7) {
      setMemories(getFallbackDecisionMemories());
    }
    if (step === 10) {
      setSimilarContext(getFallbackSimilarContext());
    }

    // 2. Background sync with live API Gateway
    try {
      setLoading(true);
      const updated = await setDemoStep(step);
      if (updated && updated.current_step === step) {
        setDemoState(updated);
      }
      await loadData();
    } catch {
      // Offline / cold start tolerance — optimistic state remains active
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    // 1. Instant optimistic reset to Step 1
    const resetDemoState = getFallbackDemoState(1);
    setDemoState(resetDemoState);
    const resetDash = getFallbackDashboard(1);
    setDashboard(resetDash);
    setSafety(resetDash.immediate_safety_status);
    setAlerts([]);

    // 2. Dispatch reset to backend
    try {
      setLoading(true);
      await resetDemo();
      await loadData();
    } catch {
      // Handled
    } finally {
      setLoading(false);
    }
  };

  const handleChooseTrajectory = async (
    scenarioId: string,
    reason: string,
    reasonCategory: string
  ) => {
    // Optimistic choice recording
    const chosenDemo = getFallbackDemoState(7, scenarioId);
    chosenDemo.operator_reason = reason;
    chosenDemo.reason_category = reasonCategory;
    setDemoState(chosenDemo);

    try {
      setLoading(true);
      await chooseTrajectory({
        operator_id: 'OP1001',
        scenario_id: scenarioId,
        operator_reason: reason,
        reason_category: reasonCategory,
      });
      await loadData();
    } catch {
      // Handled
    } finally {
      setLoading(false);
    }
  };

  const attentionMode = dashboard?.attention_mode || demoState?.attention_mode || 'NORMAL';
  const attentionReason = dashboard?.attention_reason || demoState?.attention_reason || 'Nominal operating state.';

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-[#111111] text-[#E5E5E5] flex flex-col font-sans selection:bg-[#FFCD11] selection:text-black">
        {/* Sticky Demo Controller */}
        <DemoControlBar
          demoState={demoState}
          onStepChange={handleStepChange}
          onReset={handleReset}
          loading={loading}
        />

        {/* Industrial Cab Companion Header */}
        <CabHeader
          attentionMode={attentionMode}
          attentionReason={attentionReason}
          operatorId="OP1001"
          machineId="EXC-CAT-349D"
        />

        {/* Main Routed Content Area */}
        <main className="flex-1 p-4 sm:p-6 max-w-7xl mx-auto w-full">
          <Routes>
            <Route
              path="/"
              element={
                <ShiftCockpit
                  dashboard={dashboard}
                  demoState={demoState}
                  loading={loading}
                />
              }
            />
            <Route
              path="/shift"
              element={
                <ShiftCockpit
                  dashboard={dashboard}
                  demoState={demoState}
                  loading={loading}
                />
              }
            />
            <Route
              path="/trajectory"
              element={
                <TrajectoryScreen
                  demoState={demoState}
                  onChooseTrajectory={handleChooseTrajectory}
                  loading={loading}
                />
              }
            />
            <Route
              path="/tasks"
              element={<TasksScreen tasks={tasks} loading={loading} />}
            />
            <Route
              path="/safety"
              element={
                <SafetyScreen
                  safety={safety}
                  alerts={alerts}
                  behaviour={demoState}
                  loading={loading}
                />
              }
            />
            <Route
              path="/machine"
              element={<MachineScreen demoState={demoState} />}
            />
            <Route
              path="/insights"
              element={
                <InsightsScreen
                  dashboard={dashboard}
                  demoState={demoState}
                />
              }
            />
            <Route
              path="/decisions"
              element={
                <DecisionMemoryScreen
                  memories={memories}
                  similarContext={similarContext}
                />
              }
            />
            <Route path="/what-if" element={<WhatIfPage />} />
            <Route
              path="/training"
              element={
                <TrainingHubScreen
                  modules={modules}
                  recommendations={recommendations}
                  progress={progress}
                  loading={loading}
                />
              }
            />
            <Route
              path="/training/:moduleId"
              element={<TrainingScenarioPlayer />}
            />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        {/* Cab Monorepo Port Footer */}
        <CabFooter />
      </div>
    </BrowserRouter>
  );
};
