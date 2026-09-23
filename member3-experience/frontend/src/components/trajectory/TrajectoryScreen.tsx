import React, { useState } from 'react';
import {
  Compass,
  AlertTriangle,
  HelpCircle,
  CheckCircle2,
  Clock,
  Fuel,
  Activity,
  TrendingUp,
  Shield,
  ShieldAlert,
  ArrowRight,
  GitBranch,
} from 'lucide-react';
import { DemoState, TrajectoryScenario, WhyDecisionTrace } from '../../types';
import { ConsequenceGraph } from './ConsequenceGraph';
import { WhyTraceModal } from './WhyTraceModal';
import { DecisionChoiceModal } from './DecisionChoiceModal';
import { OutcomeReplayCard } from './OutcomeReplayCard';

interface TrajectoryScreenProps {
  demoState: DemoState | null;
  onChooseTrajectory: (scenarioId: string, reason: string, reasonCategory: string) => Promise<void>;
  loading?: boolean;
}

export const TrajectoryScreen: React.FC<TrajectoryScreenProps> = ({
  demoState,
  onChooseTrajectory,
  loading = false,
}) => {
  const [selectedWhyTrace, setSelectedWhyTrace] = useState<{
    trace: WhyDecisionTrace;
    title: string;
  } | null>(null);

  const [activeScenarioForChoice, setActiveScenarioForChoice] = useState<TrajectoryScenario | null>(null);
  const [expandedGraphScenarioId, setExpandedGraphScenarioId] = useState<string>('SCEN-02-RESEQUENCE');

  const dp = demoState?.decision_point;
  const scenarios = demoState?.scenarios || [];
  const chosenScenarioId = demoState?.chosen_scenario;
  const outcomeReplay = demoState?.outcome_replay;

  const handleConfirmChoice = async (scenarioId: string, reason: string, reasonCategory: string) => {
    await onChooseTrajectory(scenarioId, reason, reasonCategory);
    setActiveScenarioForChoice(null);
  };

  const activeGraphScenario = scenarios.find((s) => s.scenario_id === expandedGraphScenarioId) || scenarios[1] || scenarios[0];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Active Decision Point Alert Banner */}
      {dp && (
        <section className="bg-gradient-to-r from-amber-950/80 via-[#261E0A] to-amber-950/80 border-2 border-[#FFCD11] rounded-2xl p-6 shadow-2xl">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
            <div className="space-y-1.5">
              <div className="flex items-center space-x-2.5">
                <span className="flex items-center space-x-1.5 text-xs font-black uppercase tracking-wider px-2.5 py-1 rounded bg-[#FFCD11] text-[#111111] shadow">
                  <AlertTriangle className="w-3.5 h-3.5" />
                  <span>DECISION POINT DETECTED</span>
                </span>
                <span className="text-xs font-mono font-bold text-[#FFCD11]">{dp.decision_point_id}</span>
                <span className="text-xs text-gray-400 font-medium">• Trigger: {dp.trigger_type}</span>
              </div>
              <h2 className="text-xl sm:text-2xl font-black text-white">{dp.summary}</h2>
              <p className="text-xs text-gray-300">
                Machine <strong className="text-white">{dp.machine_id}</strong> on Task{' '}
                <strong className="text-[#FFCD11]">{dp.task_id}</strong> • Consequence Engine evaluated{' '}
                <strong className="text-white">{scenarios.length} operational trajectories</strong>.
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-black uppercase px-3 py-1.5 rounded-lg bg-rose-950 text-rose-300 border border-rose-800 animate-pulse">
                Severity: {dp.severity}
              </span>
            </div>
          </div>

          {/* Decision Evidence Metric Pills */}
          {dp.evidence && (
            <div className="mt-5 pt-4 border-t border-amber-800/40 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="bg-black/40 p-2.5 rounded-lg border border-amber-900/40">
                <span className="text-gray-400 uppercase text-[10px] font-semibold">Truck Gap Projected</span>
                <div className="font-mono font-bold text-white text-sm mt-0.5">
                  {dp.evidence.truck_gap_projected_minutes ?? 18.2} mins
                </div>
              </div>
              <div className="bg-black/40 p-2.5 rounded-lg border border-amber-900/40">
                <span className="text-gray-400 uppercase text-[10px] font-semibold">Arrival Queue Bunching</span>
                <div className="font-mono font-bold text-amber-300 text-sm mt-0.5">
                  {dp.evidence.truck_queue_on_arrival ?? 4} haul trucks
                </div>
              </div>
              <div className="bg-black/40 p-2.5 rounded-lg border border-amber-900/40">
                <span className="text-gray-400 uppercase text-[10px] font-semibold">Rain Front Onset</span>
                <div className="font-mono font-bold text-rose-300 text-sm mt-0.5">
                  11:30 AM (North Bench)
                </div>
              </div>
              <div className="bg-black/40 p-2.5 rounded-lg border border-amber-900/40">
                <span className="text-gray-400 uppercase text-[10px] font-semibold">Baseline Shift Delay</span>
                <div className="font-mono font-bold text-rose-400 text-sm mt-0.5">
                  +{dp.evidence.baseline_eta_delay_minutes ?? 17.4} mins trap
                </div>
              </div>
            </div>
          )}
        </section>
      )}

      {/* Trajectories Comparison Section */}
      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-lg font-black text-white uppercase tracking-tight flex items-center space-x-2">
              <GitBranch className="w-5 h-5 text-[#FFCD11]" />
              <span>COMPARE CANDIDATE TRAJECTORIES</span>
            </h3>
            <p className="text-xs text-gray-400">
              Evaluated against real-time operations API models, deterministic safety constraints, and consequence flows.
            </p>
          </div>
          {chosenScenarioId && (
            <div className="flex items-center space-x-2 text-xs text-emerald-400 bg-emerald-950/60 border border-emerald-800 px-3 py-1.5 rounded-lg">
              <CheckCircle2 className="w-4 h-4" />
              <span>
                Active Choice: <strong className="font-mono">{chosenScenarioId}</strong>
              </span>
            </div>
          )}
        </div>

        {/* Trajectory Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {scenarios.map((scen) => {
            const isChosen = scen.scenario_id === chosenScenarioId;
            const isRejected = scen.constraint_status === 'REJECTED';
            const outcome = scen.predicted_outcome;

            return (
              <div
                key={scen.scenario_id}
                className={`rounded-2xl border p-5 flex flex-col justify-between transition-all duration-200 ${
                  isChosen
                    ? 'bg-gradient-to-b from-emerald-950/40 to-[#181818] border-emerald-500 shadow-xl ring-2 ring-emerald-500/40'
                    : isRejected
                    ? 'bg-[#151515] border-rose-900/60 opacity-80'
                    : 'bg-[#1A1A1A] border-[#2E2E2E] hover:border-[#FFCD11]/60 shadow-lg'
                }`}
              >
                <div className="space-y-3">
                  {/* Status & Action Badge */}
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold text-gray-400">
                      {scen.action_id}
                    </span>
                    {isRejected ? (
                      <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800">
                        REJECTED
                      </span>
                    ) : (
                      <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
                        FEASIBLE
                      </span>
                    )}
                  </div>

                  <div>
                    <h4 className="text-sm font-black text-white">{scen.title}</h4>
                    <p className="text-xs text-gray-300 mt-1 line-clamp-3">{scen.description}</p>
                  </div>

                  {/* Constraint Rejection Box */}
                  {isRejected && scen.constraint_detail && (
                    <div className="bg-rose-950/60 border border-rose-800 rounded-lg p-3 text-[11px] text-rose-200 space-y-1">
                      <div className="font-bold flex items-center space-x-1 text-rose-300">
                        <ShieldAlert className="w-3.5 h-3.5 shrink-0" />
                        <span>REJECTED — SAFETY/OPERATIONAL CONSTRAINT</span>
                      </div>
                      <div>
                        Constraint: <strong>{scen.constraint_detail.constraint}</strong>
                      </div>
                      <div>
                        Calculated Value: <strong className="text-rose-400">{scen.constraint_detail.value}</strong> (Limit: {scen.constraint_detail.threshold})
                      </div>
                      <div className="text-[10px] text-gray-400 pt-1 border-t border-rose-900/60">
                        {scen.constraint_detail.explanation}
                      </div>
                    </div>
                  )}

                  {/* Multi-Dimensional Operational Forecast Table */}
                  <div className="space-y-1.5 text-xs bg-[#111111] p-3 rounded-lg border border-[#242424]">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Duration Forecast:</span>
                      <span className="font-mono font-bold text-white">
                        {outcome.duration_minutes ?? 145} min
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Shift Delay:</span>
                      <span
                        className={`font-mono font-bold ${
                          outcome.shift_delay_minutes > 0
                            ? 'text-rose-400'
                            : 'text-emerald-400'
                        }`}
                      >
                        {outcome.shift_delay_minutes > 0
                          ? `+${outcome.shift_delay_minutes} min trap`
                          : `${Math.abs(outcome.shift_delay_minutes)} min saved`}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Fuel Consumption:</span>
                      <span className="font-mono font-bold text-white">{outcome.fuel_liters} L</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Productivity Proxy:</span>
                      <span className="font-mono font-bold text-sky-400">
                        {outcome.productivity_tons_per_hr ?? 105} tons/hr
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-400">Dead Idle Time:</span>
                      <span className="font-mono font-bold text-[#FFCD11]">
                        {outcome.idle_minutes ?? 0} min
                      </span>
                    </div>
                    <div className="flex justify-between items-center pt-1 border-t border-[#202020]">
                      <span className="text-gray-400">Safety Risk Score:</span>
                      <span
                        className={`font-mono font-bold ${
                          outcome.safety_risk_score > 30 ? 'text-rose-400' : 'text-emerald-400'
                        }`}
                      >
                        {outcome.safety_risk_score} / 100
                      </span>
                    </div>
                  </div>
                </div>

                {/* Card Action Buttons */}
                <div className="mt-4 pt-3 border-t border-[#282828] space-y-2">
                  <div className="flex items-center space-x-2">
                    {scen.consequence_graph && (
                      <button
                        onClick={() => setExpandedGraphScenarioId(scen.scenario_id)}
                        className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold border transition flex items-center justify-center space-x-1 ${
                          expandedGraphScenarioId === scen.scenario_id
                            ? 'bg-[#FFCD11]/20 border-[#FFCD11] text-[#FFCD11]'
                            : 'bg-[#222222] border-[#333333] text-gray-300 hover:bg-[#2A2A2A]'
                        }`}
                      >
                        <GitBranch className="w-3.5 h-3.5" />
                        <span>Inspect DAG</span>
                      </button>
                    )}

                    {scen.why_trace && (
                      <button
                        onClick={() =>
                          setSelectedWhyTrace({ trace: scen.why_trace!, title: scen.title })
                        }
                        className="py-1.5 px-2.5 rounded-lg text-xs font-semibold bg-[#222222] hover:bg-[#2E2E2E] text-gray-300 border border-[#333333] transition flex items-center space-x-1"
                        title="Inspect Decision Trace"
                      >
                        <HelpCircle className="w-3.5 h-3.5 text-[#FFCD11]" />
                        <span>Why?</span>
                      </button>
                    )}
                  </div>

                  {/* Choose Trajectory Button */}
                  {scen.selectable ? (
                    <button
                      onClick={() => setActiveScenarioForChoice(scen)}
                      disabled={loading || isChosen}
                      className={`w-full py-2 px-3 rounded-lg text-xs font-black uppercase tracking-wider transition shadow flex items-center justify-center space-x-1.5 ${
                        isChosen
                          ? 'bg-emerald-600 text-white cursor-default'
                          : 'bg-[#FFCD11] hover:bg-[#E0A800] text-[#111111]'
                      }`}
                    >
                      {isChosen ? (
                        <>
                          <CheckCircle2 className="w-4 h-4" />
                          <span>Committed Path</span>
                        </>
                      ) : (
                        <>
                          <Compass className="w-4 h-4" />
                          <span>Choose This Trajectory</span>
                        </>
                      )}
                    </button>
                  ) : (
                    <button
                      disabled
                      className="w-full py-2 px-3 rounded-lg text-xs font-bold uppercase tracking-wider bg-[#222222] text-gray-500 cursor-not-allowed border border-[#333333]"
                    >
                      Infeasible (Safety Blocked)
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Consequence Graph Visualizer for Selected Candidate */}
      {activeGraphScenario?.consequence_graph && (
        <section className="space-y-2">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-black text-white uppercase tracking-wider flex items-center space-x-2">
              <GitBranch className="w-4 h-4 text-[#FFCD11]" />
              <span>Consequence Graph: {activeGraphScenario.title}</span>
            </h3>
            <span className="text-xs text-gray-400">Labeled: Operational consequence chain</span>
          </div>
          <ConsequenceGraph graph={activeGraphScenario.consequence_graph} />
        </section>
      )}

      {/* Outcome Replay Component */}
      {outcomeReplay && (
        <section className="space-y-2">
          <OutcomeReplayCard outcome={outcomeReplay} />
        </section>
      )}

      {/* Modals */}
      {selectedWhyTrace && (
        <WhyTraceModal
          trace={selectedWhyTrace.trace}
          scenarioTitle={selectedWhyTrace.title}
          onClose={() => setSelectedWhyTrace(null)}
        />
      )}

      {activeScenarioForChoice && (
        <DecisionChoiceModal
          scenario={activeScenarioForChoice}
          operatorId={demoState?.operator_id || 'OP1001'}
          onConfirm={handleConfirmChoice}
          onClose={() => setActiveScenarioForChoice(null)}
          loading={loading}
        />
      )}
    </div>
  );
};

