import React, { useState } from 'react';
import { Sliders, Sparkles, TrendingUp, Clock, Fuel, AlertCircle, Compass } from 'lucide-react';
import { Link } from 'react-router-dom';
import { WhatIfResult } from '../types';
import { simulateWhatIf } from '../api/client';

export const WhatIfPage: React.FC = () => {
  const [weather, setWeather] = useState<string>('RAIN_MODERATE');
  const [operatorSkill, setOperatorSkill] = useState<string>('INTERMEDIATE');
  const [expectedIdleReduction, setExpectedIdleReduction] = useState<number>(15);
  const [machineAgeHours, setMachineAgeHours] = useState<number>(4200);
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<WhatIfResult | null>(null);

  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await simulateWhatIf({
        task_id: 'T002',
        simulated_idle_reduction_pct: expectedIdleReduction,
        weather,
        operator_skill: operatorSkill,
        machine_age_hours: machineAgeHours,
      });
      setResult(res);
    } catch {
      // Fallback preview
      const timeSaved = Math.round(expectedIdleReduction * 1.15);
      setResult({
        task_id: 'T002',
        simulated_parameters: { weather, expectedIdleReduction, operatorSkill },
        time_saved_minutes: timeSaved,
        fuel_saved_liters: Math.round(timeSaved * 0.95),
        predicted_shift_delay_minutes: Math.max(0, 17 - timeSaved),
        summary: `Simulating ${expectedIdleReduction}% idle reduction under ${weather} yields ${timeSaved} mins saved and ${Math.round(timeSaved * 0.95)}L fuel reduction.`,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#282828] pb-4">
        <div>
          <h2 className="text-xl font-black text-white uppercase tracking-tight flex items-center space-x-2">
            <Sliders className="w-5 h-5 text-[#FFCD11]" />
            <span>WHAT-IF PARAMETER EXPLORATION</span>
          </h2>
          <p className="text-xs text-gray-400">
            Explore counterfactual shift outcomes by adjusting weather, idle mitigation, and machine variables.
          </p>
        </div>
        <Link
          to="/trajectory"
          className="text-xs px-3 py-1.5 rounded-lg bg-[#252525] hover:bg-[#303030] text-[#FFCD11] font-bold border border-[#3E3E3E] transition flex items-center space-x-1"
        >
          <Compass className="w-3.5 h-3.5" />
          <span>Go to CAT Trajectory →</span>
        </Link>
      </div>

      {/* Differentiator Notice */}
      <div className="p-4 rounded-xl bg-[#181818] border border-[#2E2E2E] text-xs text-gray-400 flex items-start space-x-3">
        <AlertCircle className="w-4 h-4 text-[#FFCD11] shrink-0 mt-0.5" />
        <div>
          <strong className="text-white">Product Architecture Note:</strong> General what-if exploration provides
          broad hypothetical scenario testing. The primary product differentiator remains{' '}
          <strong className="text-[#FFCD11]">CAT Trajectory</strong>—which algorithmically identifies emergent decision
          points, evaluates safety constraints, and produces causal consequence DAGs.
        </div>
      </div>

      {/* Input Parameters Form */}
      <form onSubmit={handleSimulate} className="bg-[#181818] border border-[#2E2E2E] rounded-2xl p-6 shadow-xl space-y-6">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">
          Simulate Operational Variations
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 text-xs">
          {/* Weather */}
          <div>
            <label className="block text-gray-300 font-semibold mb-2">Weather Condition:</label>
            <select
              value={weather}
              onChange={(e) => setWeather(e.target.value)}
              className="w-full bg-[#121212] border border-[#333333] rounded-lg p-3 text-white focus:outline-none focus:border-[#FFCD11]"
            >
              <option value="CLEAR">Clear & Dry (Ground saturation 10%)</option>
              <option value="RAIN_MODERATE">Approaching Rain Front (Ground saturation 28%)</option>
              <option value="RAIN_HEAVY">Heavy Rainstorm (Ground saturation 45%)</option>
              <option value="MUD_SLURRY">Severe Mud / Slick Haul Ramp</option>
            </select>
          </div>

          {/* Operator Skill */}
          <div>
            <label className="block text-gray-300 font-semibold mb-2">Operator Skill Level:</label>
            <select
              value={operatorSkill}
              onChange={(e) => setOperatorSkill(e.target.value)}
              className="w-full bg-[#121212] border border-[#333333] rounded-lg p-3 text-white focus:outline-none focus:border-[#FFCD11]"
            >
              <option value="NOVICE">Tier 1: Novice (&lt; 500 hours)</option>
              <option value="INTERMEDIATE">Tier 2: Intermediate (OP1001 standard)</option>
              <option value="MASTER">Tier 3: Master Operator (&gt; 5,000 hours)</option>
            </select>
          </div>

          {/* Expected Idle Reduction Slider */}
          <div>
            <div className="flex justify-between text-gray-300 font-semibold mb-2">
              <span>Expected Idle Reduction:</span>
              <span className="font-mono text-[#FFCD11] font-bold">{expectedIdleReduction}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="40"
              step="5"
              value={expectedIdleReduction}
              onChange={(e) => setExpectedIdleReduction(Number(e.target.value))}
              className="w-full accent-[#FFCD11]"
            />
            <div className="flex justify-between text-[10px] text-gray-500 mt-1">
              <span>0% (No action)</span>
              <span>20% (AEC + Resequence)</span>
              <span>40% (Max shutdown)</span>
            </div>
          </div>

          {/* Machine Age / Hours */}
          <div>
            <div className="flex justify-between text-gray-300 font-semibold mb-2">
              <span>Machine Operating Hours:</span>
              <span className="font-mono text-white font-bold">{machineAgeHours} hrs</span>
            </div>
            <input
              type="range"
              min="500"
              max="10000"
              step="500"
              value={machineAgeHours}
              onChange={(e) => setMachineAgeHours(Number(e.target.value))}
              className="w-full accent-[#FFCD11]"
            />
            <div className="flex justify-between text-[10px] text-gray-500 mt-1">
              <span>500 hrs (New)</span>
              <span>4,200 hrs (Current)</span>
              <span>10,000 hrs (Aged)</span>
            </div>
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 rounded-xl bg-[#FFCD11] hover:bg-[#E0A800] text-[#111111] text-xs font-black uppercase tracking-wider transition shadow flex items-center space-x-2"
          >
            <span>{loading ? 'Simulating...' : 'Run What-If Shift Simulation'}</span>
          </button>
        </div>
      </form>

      {/* Simulation Result Presentation */}
      {result && (
        <section className="bg-[#181818] border border-[#2E2E2E] rounded-2xl p-6 shadow-xl space-y-4 animate-fade-in">
          <div className="border-b border-[#242424] pb-3">
            <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-[#FFCD11]">
              Simulated Forecast Result
            </span>
            <h3 className="text-base font-bold text-white mt-0.5">{result.summary}</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="bg-[#121212] p-4 rounded-xl border border-[#252525]">
              <span className="text-gray-400 uppercase text-[10px] font-semibold">Time Saved</span>
              <div className="text-2xl font-black font-mono text-emerald-400 mt-1">
                {result.time_saved_minutes} mins
              </div>
            </div>

            <div className="bg-[#121212] p-4 rounded-xl border border-[#252525]">
              <span className="text-gray-400 uppercase text-[10px] font-semibold">Fuel Saved</span>
              <div className="text-2xl font-black font-mono text-[#FFCD11] mt-1">
                {result.fuel_saved_liters} L
              </div>
            </div>

            <div className="bg-[#121212] p-4 rounded-xl border border-[#252525]">
              <span className="text-gray-400 uppercase text-[10px] font-semibold">Projected Shift Delay</span>
              <div
                className={`text-2xl font-black font-mono mt-1 ${
                  result.predicted_shift_delay_minutes > 0 ? 'text-amber-400' : 'text-emerald-400'
                }`}
              >
                {result.predicted_shift_delay_minutes > 0
                  ? `+${result.predicted_shift_delay_minutes} min`
                  : '0 min (On Time)'}
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  );
};

