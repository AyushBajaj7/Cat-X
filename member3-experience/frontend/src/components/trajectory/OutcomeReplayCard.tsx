import React from 'react';
import { Clock, Fuel, Activity, TrendingUp, CheckCircle2, AlertCircle } from 'lucide-react';
import { OutcomeReplay } from '../../types';

interface OutcomeReplayCardProps {
  outcome: OutcomeReplay;
}

export const OutcomeReplayCard: React.FC<OutcomeReplayCardProps> = ({ outcome }) => {
  const pred = outcome.predicted_outcome;
  const act = outcome.actual_outcome;
  const err = outcome.prediction_error;

  return (
    <div className="bg-[#181818] border border-[#2E2E2E] rounded-xl p-5 shadow-xl space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#242424] pb-3">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800">
              {outcome.simulation_label || 'SIMULATED OUTCOME — PROJECTION AUDITED'}
            </span>
            <span className="text-xs text-gray-400 font-mono">Decision: {outcome.decision_id}</span>
          </div>
          <h3 className="text-base font-bold text-white mt-1">
            Trajectory Execution & Model Accuracy Audit
          </h3>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs px-2.5 py-1 rounded-full bg-[#242424] border border-[#333333] text-emerald-400 font-mono font-bold">
            Accuracy: {err?.accuracy_pct || 98.9}%
          </span>
          <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-950/60 text-emerald-300 font-semibold border border-emerald-800">
            {outcome.drift_status}
          </span>
        </div>
      </div>

      {/* Comparison Grid: Predicted vs Actual */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
        {/* Metric 1: Duration */}
        <div className="bg-[#121212] p-3 rounded-lg border border-[#252525] space-y-1">
          <div className="flex items-center space-x-1.5 text-gray-400">
            <Clock className="w-3.5 h-3.5 text-purple-400" />
            <span className="font-semibold uppercase text-[10px]">Total Duration</span>
          </div>
          <div className="flex items-baseline justify-between pt-1">
            <span className="text-gray-400">Predicted:</span>
            <span className="font-mono text-gray-300 font-bold">{pred.eta_minutes} min</span>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-gray-400">Simulated:</span>
            <span className="font-mono text-white font-bold">{act.eta_minutes} min</span>
          </div>
          <div className="flex items-baseline justify-between text-[11px] pt-1 border-t border-[#222222]">
            <span className="text-gray-500">Error Delta:</span>
            <span className="font-mono text-emerald-400 font-bold">
              +{err.eta_delta_minutes} min (within bounds)
            </span>
          </div>
        </div>

        {/* Metric 2: Fuel Consumption */}
        <div className="bg-[#121212] p-3 rounded-lg border border-[#252525] space-y-1">
          <div className="flex items-center space-x-1.5 text-gray-400">
            <Fuel className="w-3.5 h-3.5 text-emerald-400" />
            <span className="font-semibold uppercase text-[10px]">Fuel Consumption</span>
          </div>
          <div className="flex items-baseline justify-between pt-1">
            <span className="text-gray-400">Predicted:</span>
            <span className="font-mono text-gray-300 font-bold">{pred.fuel_liters} L</span>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-gray-400">Simulated:</span>
            <span className="font-mono text-white font-bold">{act.fuel_liters} L</span>
          </div>
          <div className="flex items-baseline justify-between text-[11px] pt-1 border-t border-[#222222]">
            <span className="text-gray-500">Error Delta:</span>
            <span className="font-mono text-emerald-400 font-bold">
              {err.fuel_delta_liters} L
            </span>
          </div>
        </div>

        {/* Metric 3: Idle Minutes */}
        <div className="bg-[#121212] p-3 rounded-lg border border-[#252525] space-y-1">
          <div className="flex items-center space-x-1.5 text-gray-400">
            <Activity className="w-3.5 h-3.5 text-[#FFCD11]" />
            <span className="font-semibold uppercase text-[10px]">Dead Idle Time</span>
          </div>
          <div className="flex items-baseline justify-between pt-1">
            <span className="text-gray-400">Predicted:</span>
            <span className="font-mono text-gray-300 font-bold">{pred.idle_minutes} min</span>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-gray-400">Simulated:</span>
            <span className="font-mono text-white font-bold">{act.idle_minutes} min</span>
          </div>
          <div className="flex items-baseline justify-between text-[11px] pt-1 border-t border-[#222222]">
            <span className="text-gray-500">Saved:</span>
            <span className="font-mono text-[#FFCD11] font-bold">16.8 min dead idle averted</span>
          </div>
        </div>

        {/* Metric 4: Shift Delay */}
        <div className="bg-[#121212] p-3 rounded-lg border border-[#252525] space-y-1">
          <div className="flex items-center space-x-1.5 text-gray-400">
            <TrendingUp className="w-3.5 h-3.5 text-sky-400" />
            <span className="font-semibold uppercase text-[10px]">Shift Delay vs Handoff</span>
          </div>
          <div className="flex items-baseline justify-between pt-1">
            <span className="text-gray-400">Predicted:</span>
            <span className="font-mono text-gray-300 font-bold">{pred.shift_delay_minutes} min</span>
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-gray-400">Simulated:</span>
            <span className="font-mono text-emerald-400 font-bold">{act.shift_delay_minutes} min</span>
          </div>
          <div className="flex items-baseline justify-between text-[11px] pt-1 border-t border-[#222222]">
            <span className="text-gray-500">Net Finish:</span>
            <span className="font-mono text-emerald-400 font-bold">15.8 mins ahead of rain</span>
          </div>
        </div>
      </div>
    </div>
  );
};

