import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Shield,
  Compass,
  AlertTriangle,
  Clock,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Activity,
  CheckCircle2,
  BookOpen,
  Sliders,
  HelpCircle,
  Layers,
  ArrowUpRight,
  Eye,
  LayoutGrid,
  Truck,
  Check,
  Volume2,
  Radio,
  Gauge,
  CheckCircle,
} from 'lucide-react';
import { DashboardResponse, DemoState } from '../../types';

interface ShiftCockpitProps {
  dashboard: DashboardResponse | null;
  demoState: DemoState | null;
  loading?: boolean;
}

export const ShiftCockpit: React.FC<ShiftCockpitProps> = ({ dashboard, demoState, loading }) => {
  const navigate = useNavigate();

  const twin = dashboard?.shift_twin_summary;
  const safety = dashboard?.immediate_safety_status;
  const attentionMode = dashboard?.attention_mode || demoState?.attention_mode || 'NORMAL';
  const attentionReason = dashboard?.attention_reason || demoState?.attention_reason || 'Nominal shift state.';
  const nextAction = twin?.next_best_actions?.[0] || demoState?.next_best_action;
  const activeDecisionPoint = demoState?.decision_point || (attentionMode === 'DECISION_FOCUS');
  const trainingRec = dashboard?.top_training_recommendation || demoState?.top_training_recommendation;

  const isSafetyFocus = attentionMode === 'SAFETY_FOCUS';
  const isDecisionFocus = attentionMode === 'DECISION_FOCUS';
  const isEfficiencyFocus = attentionMode === 'EFFICIENCY_FOCUS';
  const isPlanningFocus = attentionMode === 'PLANNING_FOCUS';
  const isTrainingFocus = attentionMode === 'TRAINING_FOCUS';

  const [viewMode, setViewMode] = useState<'CAB_HUD' | 'DETAILED'>('CAB_HUD');

  return (
    <div className="space-y-6">
      {/* Cockpit Mode Switcher Header */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-[#1B1B1B] border border-[#2E2E2E] p-2.5 rounded-xl shadow-md">
        <div className="flex items-center space-x-2.5">
          <span className="text-[11px] font-black text-[#FFCD11] uppercase tracking-wider">In-Cab Mode:</span>
          <div className="flex items-center p-1 bg-black/60 rounded-lg border border-[#333333]">
            <button
              type="button"
              onClick={() => setViewMode('CAB_HUD')}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-xs font-black transition cursor-pointer ${
                viewMode === 'CAB_HUD'
                  ? 'bg-[#FFCD11] text-black shadow-md'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              <span>CAB HUD (Hands-Free Active Digging)</span>
            </button>
            <button
              type="button"
              onClick={() => setViewMode('DETAILED')}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-md text-xs font-black transition cursor-pointer ${
                viewMode === 'DETAILED'
                  ? 'bg-[#FFCD11] text-black shadow-md'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <LayoutGrid className="w-3.5 h-3.5" />
              <span>DETAILED AUDIT (Break & Pre-Shift)</span>
            </button>
          </div>
        </div>
        <div className="text-[11px] text-gray-400 flex items-center space-x-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping mr-1"></span>
          <span>Zero screen interaction required while operating joysticks</span>
        </div>
      </div>

      {/* CAB HUD MODE (Glanceable, Low-Stress In-Cab Display) */}
      {viewMode === 'CAB_HUD' && (
        <div className="space-y-6 animate-fadeIn">
          {/* 1. Giant Cab Status Hero Display (Glanceable in 0.1s) */}
          <div
            className={`p-6 sm:p-8 rounded-2xl border-2 shadow-2xl transition-all ${
              isSafetyFocus
                ? 'bg-rose-950/80 border-rose-500 text-white animate-pulse'
                : isDecisionFocus
                ? 'bg-[#241A05] border-[#FFCD11] text-white'
                : 'bg-[#121A14] border-emerald-500/80 text-white'
            }`}
          >
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="flex items-start sm:items-center space-x-5">
                <div
                  className={`p-4 rounded-2xl ${
                    isSafetyFocus
                      ? 'bg-rose-600/30 text-rose-400'
                      : isDecisionFocus
                      ? 'bg-[#FFCD11]/20 text-[#FFCD11]'
                      : 'bg-emerald-500/20 text-emerald-400'
                  }`}
                >
                  {isSafetyFocus ? (
                    <AlertTriangle className="w-12 h-12" />
                  ) : isDecisionFocus ? (
                    <Compass className="w-12 h-12 animate-spin-slow" />
                  ) : (
                    <CheckCircle className="w-12 h-12" />
                  )}
                </div>
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`text-xs font-black uppercase tracking-widest px-2.5 py-0.5 rounded ${
                        isSafetyFocus
                          ? 'bg-rose-500 text-black font-black'
                          : isDecisionFocus
                          ? 'bg-[#FFCD11] text-black font-black'
                          : 'bg-emerald-500 text-black font-black'
                      }`}
                    >
                      {isSafetyFocus
                        ? 'CRITICAL SAFETY INTERLOCK'
                        : isDecisionFocus
                        ? 'TACTICAL RECOVERY RECOMMENDED'
                        : 'ALL CLEAR • NOMINAL DIGGING'}
                    </span>
                    <span className="text-xs text-gray-400">• Autonomous Telemetry Live</span>
                  </div>
                  <h2 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
                    {isSafetyFocus
                      ? safety?.seatbelt_fastened === false
                        ? 'SEATBELT UNFASTENED — HYDRAULIC HOLD'
                        : 'PROXIMITY WARNING — OBJECT IN 15M BUFFER'
                      : isDecisionFocus
                      ? 'HAUL BOTTLENECK: 17-MINUTE TRAP DETECTED'
                      : 'ALL CLEAR: BENCH 2 TRENCHING IN PROGRESS'}
                  </h2>
                  <p className="text-sm sm:text-base text-gray-300 max-w-2xl leading-relaxed">
                    {isSafetyFocus
                      ? safety?.seatbelt_fastened === false
                        ? 'Fasten cab harness buckle immediately to re-enable implement controls.'
                        : 'Service vehicle / personnel inside 15m counterweight swing zone. Halt boom slew.'
                      : isDecisionFocus
                      ? 'Haul trucks queued at primary crusher + incoming rain front. Resequencing to Bench 3 saves 17 minutes and 14.8L fuel.'
                      : 'Hydraulics armed • Seatbelt 100% compliant • Swing perimeter 15m clear • Pace 104.5% on target.'}
                  </p>
                </div>
              </div>

              {/* Glove-friendly Touch Action */}
              {isDecisionFocus && (
                <button
                  type="button"
                  onClick={() => navigate('/trajectory')}
                  className="px-6 py-4 rounded-xl bg-[#FFCD11] hover:bg-[#E0A800] text-black font-black text-sm uppercase tracking-wider shadow-2xl transition transform hover:scale-105 flex items-center justify-center space-x-2 whitespace-nowrap cursor-pointer"
                >
                  <Compass className="w-5 h-5 text-black" />
                  <span>Choose Bench 3 Path →</span>
                </button>
              )}
            </div>
          </div>

          {/* 2. Three Giant Glanceable Glancemeters (0.2s Glance) */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Meter 1: Safety Radar */}
            <div
              className={`p-5 rounded-xl border flex flex-col justify-between ${
                safety?.seatbelt_fastened === false || (safety?.active_hazard_count || 0) > 0
                  ? 'bg-rose-950/40 border-rose-600'
                  : 'bg-[#181818] border-[#2A2A2A]'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">1. Safety Perimeter</span>
                <Shield
                  className={`w-5 h-5 ${
                    safety?.seatbelt_fastened === false || (safety?.active_hazard_count || 0) > 0
                      ? 'text-rose-400'
                      : 'text-emerald-400'
                  }`}
                />
              </div>
              <div
                className={`text-2xl font-black ${
                  safety?.active_hazard_count && safety.active_hazard_count > 0 ? 'text-rose-400' : 'text-emerald-400'
                }`}
              >
                {safety?.active_hazard_count && safety.active_hazard_count > 0 ? 'HAZARD AT 11M' : '15m ZONE CLEAR'}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                LiDAR 360° radar active • Highwall grade: <strong className="text-white">8° safe</strong>
              </div>
            </div>

            {/* Meter 2: Harness & Interlock */}
            <div
              className={`p-5 rounded-xl border flex flex-col justify-between ${
                safety?.seatbelt_fastened === false ? 'bg-rose-950/40 border-rose-600' : 'bg-[#181818] border-[#2A2A2A]'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">2. Harness Interlock</span>
                <Activity
                  className={`w-5 h-5 ${
                    safety?.seatbelt_fastened === false ? 'text-rose-400' : 'text-emerald-400'
                  }`}
                />
              </div>
              <div
                className={`text-2xl font-black ${
                  safety?.seatbelt_fastened === false ? 'text-rose-400' : 'text-emerald-400'
                }`}
              >
                {safety?.seatbelt_fastened === false ? 'DISENGAGED' : 'FASTENED (100%)'}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                Hydraulic lockout:{' '}
                <strong className={safety?.seatbelt_fastened === false ? 'text-rose-400' : 'text-emerald-400'}>
                  {safety?.seatbelt_fastened === false ? 'ENGAGED' : 'ARMED & READY'}
                </strong>
              </div>
            </div>

            {/* Meter 3: Haul Fleet & Pace */}
            <div className="p-5 rounded-xl border border-[#2A2A2A] bg-[#181818] flex flex-col justify-between">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">3. Haul Fleet Cycle</span>
                <Truck className="w-5 h-5 text-sky-400" />
              </div>
              <div className="text-2xl font-black text-white">
                {isDecisionFocus ? 'TRUCKS DELAYED (17M)' : 'TRUCK 02 ON APPROACH'}
              </div>
              <div className="text-xs text-gray-400 mt-1">
                Pacing: <strong className="text-[#FFCD11]">104.5%</strong> • Shift Excavated:{' '}
                <strong className="text-white">320 / 850 t</strong>
              </div>
            </div>
          </div>

          {/* 3. In-Cab Ergonomics Guarantee & Low-Stress Reassurance */}
          <div className="p-5 rounded-xl bg-[#1C1C1C] border border-[#2F2F2F] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-3.5">
              <div className="p-2.5 rounded-xl bg-[#FFCD11]/10 text-[#FFCD11]">
                <Radio className="w-6 h-6" />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white uppercase tracking-tight">
                  In-Cab Ergonomics Guarantee: 100% Passive Operation
                </h4>
                <p className="text-xs text-gray-400 leading-relaxed max-w-2xl mt-0.5">
                  Operating a 50-ton machine requires full visual focus on the bench and haul trucks. You{' '}
                  <strong className="text-white">never need to manage or tap this screen while digging</strong>. The digital
                  twin silently logs telemetry and sounds distinct audio chimes only if a safety breach or recovery decision
                  requires your attention.
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setViewMode('DETAILED')}
              className="px-4 py-2 rounded-lg bg-[#282828] hover:bg-[#333333] text-gray-200 hover:text-white border border-[#3E3E3E] text-xs font-bold transition whitespace-nowrap cursor-pointer"
            >
              Open Detailed Analytics →
            </button>
          </div>
        </div>
      )}

      {/* DETAILED AUDIT MODE (Full 6 Diagnostic Cards, Consolidated Bar & Action Center) */}
      {viewMode === 'DETAILED' && (
        <div className="space-y-6 animate-fadeIn">
      {/* Dynamic Attention Alert Banner */}
      {attentionMode !== 'NORMAL' && (
        <div
          className={`p-4 rounded-xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-lg ${
            isSafetyFocus
              ? 'bg-rose-950/70 border-rose-600/80 text-rose-200 animate-pulse'
              : isDecisionFocus
              ? 'bg-amber-950/70 border-[#FFCD11] text-[#FFCD11]'
              : isEfficiencyFocus
              ? 'bg-emerald-950/70 border-emerald-500 text-emerald-200'
              : isPlanningFocus
              ? 'bg-sky-950/70 border-sky-500 text-sky-200'
              : 'bg-purple-950/70 border-purple-500 text-purple-200'
          }`}
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-black/40">
              {isSafetyFocus ? (
                <AlertTriangle className="w-5 h-5 text-rose-400" />
              ) : isDecisionFocus ? (
                <Compass className="w-5 h-5 text-[#FFCD11]" />
              ) : (
                <Activity className="w-5 h-5" />
              )}
            </div>
            <div>
              <div className="text-[11px] font-black uppercase tracking-wider">
                Adaptive Attention Mode • {attentionMode.replace('_', ' ')}
              </div>
              <div className="text-sm font-bold text-white mt-0.5">{attentionReason}</div>
            </div>
          </div>
          {isDecisionFocus && (
            <button
              onClick={() => navigate('/trajectory')}
              className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-[#FFCD11] hover:bg-[#E0A800] text-[#111111] font-black text-xs uppercase tracking-wider shadow transition"
            >
              <span>Inspect Trajectories</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      )}

      {/* Primary Canonical Shift Twin Card — "What is happening right now?" */}
      <section className="bg-gradient-to-r from-[#1A1A1A] via-[#222222] to-[#1A1A1A] border border-[#2E2E2E] rounded-xl p-6 shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-1.5 max-w-xl">
            <div className="flex items-center space-x-2">
              <span className="text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded bg-[#FFCD11]/20 text-[#FFCD11]">
                CANONICAL SHIFT TWIN
              </span>
              <span className="text-xs text-gray-400 font-medium">Active Operational State</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
              Bench 2 North Trenching & Excavation
            </h2>
            <div className="flex items-center flex-wrap gap-x-3 gap-y-1 mt-1">
              <span className="text-xs text-gray-300">
                Operator: <span className="font-mono text-[#FFCD11] font-bold">{twin?.operator_id || demoState?.operator_id || 'OP1001'}</span>
              </span>
              <span className="text-xs text-gray-500">|</span>
              <span className="text-xs text-gray-300">
                Machine: <span className="font-mono text-[#FFCD11] font-bold">{twin?.machine_id || demoState?.machine_id || 'EXC-CAT-349D'}</span>
              </span>
              <span className="text-xs text-gray-500">|</span>
              <span className="text-xs text-gray-300">
                State: <span className="font-bold text-emerald-400">{twin?.productivity?.efficiency_rating || 'EXCAVATING & LOADING'}</span>
              </span>
            </div>
            <p className="text-xs text-gray-300 mt-1">
              Material:{' '}
              <span className="text-white font-medium">Sandstone Overburden</span> • Shift Time:{' '}
              <span className="font-mono text-white font-bold">Hour 3.5 of 8.0</span>
            </p>
          </div>

          {/* 7-Dimension High-Level Telemetry Badges */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 bg-[#121212]/90 p-3 rounded-lg border border-[#2B2B2B]">
            <div className="text-center px-3 py-1">
              <span className="text-[10px] uppercase font-bold text-gray-400">Shift Health</span>
              <div className="text-xl font-black text-white mt-0.5">
                {twin?.shift_health_score ?? 95.5}%
              </div>
            </div>
            <div className="text-center px-3 py-1 border-l border-[#262626]">
              <span className="text-[10px] uppercase font-bold text-gray-400">Safety Index</span>
              <div className={`text-xl font-black mt-0.5 ${safety?.overall_safety_score && safety.overall_safety_score < 80 ? 'text-rose-400' : 'text-emerald-400'}`}>
                {safety?.overall_safety_score ?? twin?.safety.safety_score ?? 98.0}%
              </div>
            </div>
            <div className="text-center px-3 py-1 border-l border-[#262626]">
              <span className="text-[10px] uppercase font-bold text-gray-400">Idle Rate</span>
              <div className={`text-xl font-black mt-0.5 ${twin?.behaviour.idle_percentage && twin.behaviour.idle_percentage > 12 ? 'text-amber-400' : 'text-[#FFCD11]'}`}>
                {twin?.behaviour.idle_percentage ?? 9.8}%
              </div>
            </div>
            <div className="text-center px-3 py-1 border-l border-[#262626]">
              <span className="text-[10px] uppercase font-bold text-gray-400">Pace vs Target</span>
              <div className="text-xl font-black text-sky-400 mt-0.5">
                {twin?.productivity.pace_percentage ?? 104.5}%
              </div>
            </div>
          </div>
        </div>

        {/* Real-time Environment & Machine Summary Strip */}
        <div className="mt-5 pt-4 border-t border-[#292929] grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
          <div>
            <span className="text-gray-400">Environment:</span>
            <div className="font-semibold text-white mt-0.5">
              {twin?.environment.weather_condition || 'CLEAR'}, {twin?.environment.ambient_temp_c || 23.5}°C
            </div>
          </div>
          <div>
            <span className="text-gray-400">Ground Saturation:</span>
            <div className="font-semibold text-white mt-0.5">
              {twin?.environment.ground_saturation_pct || 12.0}%{' '}
              {twin?.environment.ground_saturation_pct && twin.environment.ground_saturation_pct > 20 && (
                <span className="text-amber-400 font-bold">(Traction Loss)</span>
              )}
            </div>
          </div>
          <div>
            <span className="text-gray-400">Task Completion:</span>
            <div className="font-semibold text-white mt-0.5">
              {twin?.productivity.completed_volume_tons || 320} / {twin?.productivity.target_volume_tons || 850} tons (
              {Math.round(((twin?.productivity.completed_volume_tons || 320) / (twin?.productivity.target_volume_tons || 850)) * 100)}%)
            </div>
          </div>
          <div>
            <span className="text-gray-400">Forecasted Finish ETA:</span>
            <div className="font-semibold text-white mt-0.5 flex items-center space-x-1">
              <Clock className="w-3.5 h-3.5 text-purple-400" />
              <span>{twin?.prediction.estimated_remaining_minutes || 145} mins remaining</span>
            </div>
          </div>
        </div>
      </section>

      {/* Prominent Next-Best-Action Card */}
      {nextAction && (
        <section
          className={`bg-[#1A1A1A] border-l-4 rounded-r-xl p-5 shadow-lg ${
            nextAction.priority === 'CRITICAL'
              ? 'border-rose-500'
              : nextAction.priority === 'HIGH'
              ? 'border-[#FFCD11]'
              : 'border-sky-500'
          }`}
        >
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center space-x-2">
                <span
                  className={`text-[10px] font-black uppercase px-2 py-0.5 rounded ${
                    nextAction.priority === 'CRITICAL'
                      ? 'bg-rose-950 text-rose-300'
                      : nextAction.priority === 'HIGH'
                      ? 'bg-[#FFCD11]/20 text-[#FFCD11]'
                      : 'bg-sky-950 text-sky-300'
                  }`}
                >
                  NEXT BEST ACTION • {nextAction.priority}
                </span>
                <span className="text-xs text-gray-400 font-medium">Context-Aware Operational Suggestion</span>
              </div>
              <h3 className="text-lg font-bold text-white">{nextAction.title}</h3>
              <p className="text-xs text-gray-300 max-w-2xl">{nextAction.rationale}</p>
            </div>
            {nextAction.estimated_benefit && (
              <div className="flex sm:flex-col items-end justify-center">
                <span className="text-[10px] text-gray-400 uppercase font-semibold">Expected Impact</span>
                <span className="text-xs font-black text-[#FFCD11] bg-[#242424] px-3 py-1.5 rounded-lg border border-[#333333] mt-0.5">
                  {nextAction.estimated_benefit}
                </span>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Consolidated Outcome Info Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 px-4 py-2.5 rounded-xl bg-[#171717] border border-[#2A2A2A] text-xs">
        <div className="flex items-center space-x-2 text-gray-300">
          <Layers className="w-4 h-4 text-[#FFCD11]" />
          <span>
            <strong>Consolidated Shift Outcome:</strong> Live synthesis of Safety (:8001), Operations (:8002), and Training (:8003). <em>No tab switching needed during digging.</em>
          </span>
        </div>
        <div className="flex items-center space-x-3 text-gray-400 font-mono text-[11px]">
          <span>Shift Health: <strong className="text-white">{twin?.shift_health_score ?? 95.5}%</strong></span>
          <span>•</span>
          <span>Finish: <strong className="text-[#FFCD11]">{twin?.prediction.estimated_remaining_minutes || 145}m</strong></span>
        </div>
      </div>

      {/* Operator Action Center — "What changes can I make right now?" */}
      <section className="bg-gradient-to-br from-[#1C1C1C] via-[#202020] to-[#181818] border border-[#333333] rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <span className="p-1.5 rounded-lg bg-[#FFCD11]/20 text-[#FFCD11]">
              <Compass className="w-4 h-4" />
            </span>
            <div>
              <h3 className="text-sm font-black text-white uppercase tracking-tight">Operator Action Center</h3>
              <p className="text-[11px] text-gray-400">Direct interventions and simulation controls available to you</p>
            </div>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950/70 border border-emerald-500/40 text-emerald-300 font-bold uppercase">
            OPERATOR IN CONTROL
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {/* Action 1: Trajectory */}
          <button
            type="button"
            onClick={() => navigate('/trajectory')}
            className="flex flex-col justify-between p-3.5 rounded-xl bg-[#262626] hover:bg-[#2E2E2E] border border-[#383838] hover:border-[#FFCD11] transition text-left group cursor-pointer shadow-sm"
          >
            <div>
              <div className="flex items-center justify-between text-[#FFCD11] mb-1 font-bold text-xs">
                <span>1. Choose Trajectory</span>
                <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition" />
              </div>
              <p className="text-[11px] text-gray-300 leading-snug">
                Compare 4 digging sequences (e.g. Resequence to Bench 3 to bypass haul fleet queue).
              </p>
            </div>
            <span className="mt-3 text-[10px] font-black uppercase text-[#FFCD11] tracking-wider">
              Inspect Trajectories →
            </span>
          </button>

          {/* Action 2: What-If */}
          <button
            type="button"
            onClick={() => navigate('/what-if')}
            className="flex flex-col justify-between p-3.5 rounded-xl bg-[#262626] hover:bg-[#2E2E2E] border border-[#383838] hover:border-sky-400 transition text-left group cursor-pointer shadow-sm"
          >
            <div>
              <div className="flex items-center justify-between text-sky-400 mb-1 font-bold text-xs">
                <span>2. Simulate What-If</span>
                <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition" />
              </div>
              <p className="text-[11px] text-gray-300 leading-snug">
                Tune target pace, swing arc angles, and haul truck return intervals in real-time.
              </p>
            </div>
            <span className="mt-3 text-[10px] font-black uppercase text-sky-400 tracking-wider">
              Launch Simulator →
            </span>
          </button>

          {/* Action 3: Safety Radar */}
          <button
            type="button"
            onClick={() => navigate('/safety')}
            className="flex flex-col justify-between p-3.5 rounded-xl bg-[#262626] hover:bg-[#2E2E2E] border border-[#383838] hover:border-rose-400 transition text-left group cursor-pointer shadow-sm"
          >
            <div>
              <div className="flex items-center justify-between text-rose-400 mb-1 font-bold text-xs">
                <span>3. Safety & Proximity</span>
                <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition" />
              </div>
              <p className="text-[11px] text-gray-300 leading-snug">
                Review 15m proximity radar, highwall stability grade, and seatbelt harness compliance.
              </p>
            </div>
            <span className="mt-3 text-[10px] font-black uppercase text-rose-400 tracking-wider">
              Inspect Safety Radar →
            </span>
          </button>

          {/* Action 4: Training Hub */}
          <button
            type="button"
            onClick={() => navigate('/training')}
            className="flex flex-col justify-between p-3.5 rounded-xl bg-[#262626] hover:bg-[#2E2E2E] border border-[#383838] hover:border-purple-400 transition text-left group cursor-pointer shadow-sm"
          >
            <div>
              <div className="flex items-center justify-between text-purple-400 mb-1 font-bold text-xs">
                <span>4. In-Cab Micro-Learning</span>
                <ArrowUpRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition" />
              </div>
              <p className="text-[11px] text-gray-300 leading-snug">
                Interactive 2-minute decision coaching scenario triggered by live context signals.
              </p>
            </div>
            <span className="mt-3 text-[10px] font-black uppercase text-purple-400 tracking-wider">
              Open Training Hub →
            </span>
          </button>
        </div>
      </section>

      {/* Main Cockpit Operational Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* 1. Daily Task Dashboard */}
        <div className={`bg-[#181818] border rounded-xl p-5 shadow ${isPlanningFocus ? 'border-sky-500 ring-1 ring-sky-500/50' : 'border-[#282828]'}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-[#FFCD11]" />
              <h3 className="font-bold text-white text-sm">Task Dashboard</h3>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-sky-950 text-sky-300 font-bold uppercase">
              IN PROGRESS
            </span>
          </div>
          <div className="text-xs text-gray-400 mb-1">Current Assignment:</div>
          <div className="font-bold text-white text-sm mb-3">Task T002 — Bench 2 Deep Trenching</div>
          <div className="space-y-3 text-xs">
            <div>
              <div className="flex justify-between text-gray-300 mb-1">
                <span>Material Excavated:</span>
                <span className="font-mono text-white font-bold">
                  {twin?.productivity.completed_volume_tons || 320} / {twin?.productivity.target_volume_tons || 850} tons
                </span>
              </div>
              <div className="w-full bg-[#101010] h-2.5 rounded-full overflow-hidden border border-[#222222]">
                <div
                  className="bg-[#FFCD11] h-full rounded-full transition-all"
                  style={{
                    width: `${Math.min(100, Math.round(((twin?.productivity.completed_volume_tons || 320) / (twin?.productivity.target_volume_tons || 850)) * 100))}%`,
                  }}
                ></div>
              </div>
            </div>
            <div className="flex justify-between text-gray-400 pt-1 border-t border-[#242424]">
              <span>Scheduled Shift Duration:</span>
              <span className="text-white font-mono">4.0 hrs (240 min)</span>
            </div>
            <button
              onClick={() => navigate('/tasks')}
              className="w-full mt-2 py-1.5 rounded bg-[#252525] hover:bg-[#303030] text-gray-200 text-xs font-semibold transition"
            >
              View Full Task Schedule →
            </button>
          </div>
        </div>

        {/* 2. Real-Time Safety */}
        <div className={`bg-[#181818] border rounded-xl p-5 shadow ${isSafetyFocus ? 'border-rose-500 ring-2 ring-rose-500/40' : 'border-[#282828]'}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Shield className={`w-4 h-4 ${safety?.seatbelt_fastened === false || (safety?.active_hazard_count || 0) > 0 ? 'text-rose-400' : 'text-emerald-400'}`} />
              <h3 className="font-bold text-white text-sm">Real-Time Safety</h3>
            </div>
            <span
              className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${
                safety?.seatbelt_fastened === false || (safety?.active_hazard_count || 0) > 0
                  ? 'bg-rose-950 text-rose-300'
                  : 'bg-emerald-950 text-emerald-300'
              }`}
            >
              {safety?.seatbelt_fastened === false ? 'UNSAFE' : (safety?.active_hazard_count || 0) > 0 ? 'WARNING' : 'COMPLIANT'}
            </span>
          </div>
          <div className="space-y-3 text-xs">
            <div className="flex justify-between items-center py-1 border-b border-[#242424]">
              <span className="text-gray-400">Seatbelt Harness:</span>
              <span className={`font-bold ${safety?.seatbelt_fastened === false ? 'text-rose-400 animate-pulse' : 'text-emerald-400'}`}>
                {safety?.seatbelt_fastened === false ? 'UNFASTENED (ALERT)' : 'FASTENED (99.4% streak)'}
              </span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-[#242424]">
              <span className="text-gray-400">Proximity Buffer:</span>
              <span className={`font-bold ${(safety?.active_hazard_count || 0) > 0 ? 'text-rose-400 animate-pulse' : 'text-white'}`}>
                {(safety?.active_hazard_count || 0) > 0 ? '1 VEHICLE IN 12M ZONE' : '0 active (Perimeter Clear)'}
              </span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-gray-400">Highwall Geotechnical Stability:</span>
              <span className="text-emerald-400 font-bold">STABLE (8° safe)</span>
            </div>
            <button
              onClick={() => navigate('/safety')}
              className="w-full mt-2 py-1.5 rounded bg-[#252525] hover:bg-[#303030] text-gray-200 text-xs font-semibold transition"
            >
              Inspect Safety & Incident Audit →
            </button>
          </div>
        </div>

        {/* 3. CAT Trajectory Consequence Engine (Primary Differentiator) */}
        <div className={`bg-gradient-to-b from-[#1E1E1E] to-[#181818] border rounded-xl p-5 shadow ${isDecisionFocus ? 'border-[#FFCD11] ring-2 ring-[#FFCD11]/40' : 'border-[#333333]'}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Compass className="w-4 h-4 text-[#FFCD11]" />
              <h3 className="font-bold text-white text-sm">CAT Trajectory</h3>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-[#FFCD11]/20 text-[#FFCD11] font-bold uppercase">
              CONSEQUENCE ENGINE
            </span>
          </div>
          <div className="text-xs text-gray-300 mb-2">
            {activeDecisionPoint
              ? 'Tactical decision point detected: haul fleet bunching & approaching rain.'
              : 'Continuous consequence modeling across 3 candidate trajectories.'}
          </div>
          <div className="bg-[#121212] p-3 rounded-lg border border-[#2A2A2A] space-y-2 mb-3 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-400">Trajectory A (Continue):</span>
              <span className="text-rose-400 font-mono font-bold">+17 min delay trap</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Trajectory B (Resequence):</span>
              <span className="text-emerald-400 font-mono font-bold">17 min saved & 14.8L fuel</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Trajectory C (Reposition):</span>
              <span className="text-sky-400 font-mono font-bold">13 min saved & 11.2L fuel</span>
            </div>
          </div>
          <button
            onClick={() => navigate('/trajectory')}
            className="w-full py-2 rounded-lg bg-[#FFCD11] hover:bg-[#E0A800] text-[#111111] text-xs font-black uppercase tracking-wider shadow transition"
          >
            Open Trajectory Comparison & DAG →
          </button>
        </div>

        {/* 4. Behavior Analytics */}
        <div className={`bg-[#181818] border rounded-xl p-5 shadow ${isEfficiencyFocus ? 'border-emerald-500 ring-1 ring-emerald-500/50' : 'border-[#282828]'}`}>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Activity className="w-4 h-4 text-emerald-400" />
              <h3 className="font-bold text-white text-sm">Behavior & Idle State</h3>
            </div>
            <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${twin?.behaviour.idle_percentage && twin.behaviour.idle_percentage > 12 ? 'bg-amber-950 text-amber-300' : 'bg-emerald-950 text-emerald-300'}`}>
              {twin?.behaviour.idle_percentage && twin.behaviour.idle_percentage > 12 ? 'HIGH IDLE' : 'OPTIMAL'}
            </span>
          </div>
          <div className="space-y-2.5 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-400">Current Idle Percentage:</span>
              <span className="font-mono text-white font-bold">{twin?.behaviour.idle_percentage || 9.8}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Behavior Consistency Score:</span>
              <span className="font-mono text-emerald-400 font-bold">{twin?.behaviour.behaviour_score || 94.0}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Aggressive Maneuvers:</span>
              <span className="font-mono text-white">0 events</span>
            </div>
            <button
              onClick={() => navigate('/machine')}
              className="w-full mt-2 py-1.5 rounded bg-[#252525] hover:bg-[#303030] text-gray-200 text-xs font-semibold transition"
            >
              Inspect Machine & Telematics →
            </button>
          </div>
        </div>

        {/* 5. Probabilistic Task-Time Estimation (ETA) */}
        <div className="bg-[#181818] border border-[#282828] rounded-xl p-5 shadow">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-purple-400" />
              <h3 className="font-bold text-white text-sm">Task ETA Forecast</h3>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-purple-950 text-purple-300 font-bold uppercase">
              ML PREDICTION
            </span>
          </div>
          <div className="space-y-2.5 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-400">Estimated Remaining:</span>
              <span className="font-mono text-white font-bold">
                ~{twin?.prediction.estimated_remaining_minutes || 145} minutes
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Model Confidence:</span>
              <span className="font-mono text-purple-300 font-bold">
                {Math.round((twin?.prediction.confidence_score || 0.92) * 100)}% (P10/P90 Interval)
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Weather Traction Delta:</span>
              <span className="font-mono text-gray-300">+4 min on 12% grade</span>
            </div>
            <button
              onClick={() => navigate('/insights')}
              className="w-full mt-2 py-1.5 rounded bg-[#252525] hover:bg-[#303030] text-gray-200 text-xs font-semibold transition"
            >
              View Prediction Breakdown & Trends →
            </button>
          </div>
        </div>

        {/* 6. Contextual Training Recommendation */}
        <div className={`bg-[#181818] border rounded-xl p-5 shadow flex flex-col justify-between ${isTrainingFocus ? 'border-purple-500 ring-1 ring-purple-500/50' : 'border-[#282828]'}`}>
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <BookOpen className="w-4 h-4 text-[#FFCD11]" />
                <h3 className="font-bold text-white text-sm">Training Recommendation</h3>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded bg-[#FFCD11]/20 text-[#FFCD11] font-bold uppercase">
                MICRO-LEARNING
              </span>
            </div>
            <div className="text-xs text-gray-400 mb-1">Recommended Module:</div>
            <div className="font-bold text-white text-sm mb-1">
              {trainingRec?.module_title || 'Safe Start Check'}
            </div>
            <p className="text-xs text-gray-400 mb-3">
              {trainingRec?.reason || 'Contextual signal triggered a micro-learning refresher.'}
            </p>
          </div>
          <button
            onClick={() => navigate(`/training/${trainingRec?.module_id || 'SAFE_START_01'}`)}
            className="w-full py-2 px-3 bg-[#2D2D2D] hover:bg-[#FFCD11] hover:text-[#111111] text-white text-xs font-bold rounded-lg transition"
          >
            Launch Interactive Scenario →
          </button>
        </div>
      </div>
        </div>
      )}
    </div>
  );
};


