import React from 'react';
import { Brain, Activity, Clock, Compass, TrendingUp, Sparkles, CheckCircle2 } from 'lucide-react';
import { DashboardResponse, DemoState } from '../../types';

interface InsightsScreenProps {
  dashboard: DashboardResponse | null;
  demoState: DemoState | null;
}

export const InsightsScreen: React.FC<InsightsScreenProps> = ({ dashboard, demoState }) => {
  const twin = dashboard?.shift_twin_summary;
  const attentionMode = dashboard?.attention_mode || demoState?.attention_mode || 'NORMAL';
  const attentionReason = dashboard?.attention_reason || demoState?.attention_reason || 'Nominal shift state.';

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#282828] pb-4">
        <div>
          <h2 className="text-xl font-black text-white uppercase tracking-tight flex items-center space-x-2">
            <Brain className="w-5 h-5 text-[#FFCD11]" />
            <span>SHIFT TWIN INTELLIGENCE & INSIGHTS</span>
          </h2>
          <p className="text-xs text-gray-400">
            Canonical 7-dimension digital twin context, operational memory trends, and predictive models.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs px-2.5 py-1 rounded-lg bg-[#252525] border border-[#3A3A3A] text-[#FFCD11] font-bold">
            Attention: {attentionMode}
          </span>
        </div>
      </div>

      {/* 7-Dimension Digital Twin Deep-Dive Grid */}
      <section className="bg-[#181818] border border-[#2B2B2B] rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex items-center justify-between border-b border-[#242424] pb-3">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-4 h-4 text-[#FFCD11]" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Canonical 7-Dimension Twin Composition
            </h3>
          </div>
          <span className="text-xs font-mono text-gray-400">Twin ID: {twin?.twin_id || 'TWIN-OP1001-LIVE'}</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
          {/* Dim 1: Operator */}
          <div className="bg-[#121212] p-4 rounded-xl border border-[#242424] space-y-1">
            <span className="text-[10px] font-bold uppercase text-[#FFCD11]">1. Operator Dimension</span>
            <div className="font-bold text-white text-sm">OP1001 — J. Miller</div>
            <div className="text-gray-400">Tier: Intermediate • Shift Hours: 3.5 / 8.0 hrs</div>
            <div className="text-emerald-400 font-medium pt-1">Fatigue Score: 12.0 (Low Risk)</div>
          </div>

          {/* Dim 2: Machine */}
          <div className="bg-[#121212] p-4 rounded-xl border border-[#242424] space-y-1">
            <span className="text-[10px] font-bold uppercase text-[#FFCD11]">2. Machine Dimension</span>
            <div className="font-bold text-white text-sm">EXC-CAT-349D Excavator</div>
            <div className="text-gray-400">Engine Hours: 4,218.4 hrs • Fuel Burn: 14.2 L/hr</div>
            <div className="text-emerald-400 font-medium pt-1">Hydraulic Implement: 34,500 kPa Nominal</div>
          </div>

          {/* Dim 3: Task */}
          <div className="bg-[#121212] p-4 rounded-xl border border-[#242424] space-y-1">
            <span className="text-[10px] font-bold uppercase text-[#FFCD11]">3. Task Dimension</span>
            <div className="font-bold text-white text-sm">Task T002 — Deep Trenching</div>
            <div className="text-gray-400">Target: 850t • Completed: 320t (37.6%)</div>
            <div className="text-sky-400 font-medium pt-1">Zone: Bench 2 North Highwall Cut</div>
          </div>

          {/* Dim 4: Environment */}
          <div className="bg-[#121212] p-4 rounded-xl border border-[#242424] space-y-1">
            <span className="text-[10px] font-bold uppercase text-[#FFCD11]">4. Environment Dimension</span>
            <div className="font-bold text-white text-sm">
              {twin?.environment.weather_condition || 'CLEAR'}, {twin?.environment.ambient_temp_c || 23.5}°C
            </div>
            <div className="text-gray-400">Ground Saturation: {twin?.environment.ground_saturation_pct || 12.0}%</div>
            <div className="text-amber-400 font-medium pt-1">Forecast: Rain front at 11:30 AM</div>
          </div>

          {/* Dim 5: Safety */}
          <div className="bg-[#121212] p-4 rounded-xl border border-[#242424] space-y-1">
            <span className="text-[10px] font-bold uppercase text-[#FFCD11]">5. Safety Dimension</span>
            <div className="font-bold text-white text-sm">
              Safety Score: {twin?.safety.safety_score || 98.0}%
            </div>
            <div className="text-gray-400">
              Harness: {twin?.safety.seatbelt_status !== false ? 'FASTENED' : 'UNBUCKLED'} • Hazards: {twin?.safety.active_proximity_hazards || 0}
            </div>
            <div className="text-emerald-400 font-medium pt-1">Streak: 99.4% shift compliance</div>
          </div>

          {/* Dim 6: Behaviour */}
          <div className="bg-[#121212] p-4 rounded-xl border border-[#242424] space-y-1">
            <span className="text-[10px] font-bold uppercase text-[#FFCD11]">6. Behaviour Dimension</span>
            <div className="font-bold text-white text-sm">
              Idle Rate: {twin?.behaviour.idle_percentage || 9.8}%
            </div>
            <div className="text-gray-400">Cycle Consistency: 94.2% • Aggressive Slew: 0</div>
            <div className="text-[#FFCD11] font-medium pt-1">AEC Auto-Idle Engaged</div>
          </div>

          {/* Dim 7: Prediction */}
          <div className="bg-[#121212] p-4 rounded-xl border border-[#242424] space-y-1 md:col-span-2 lg:col-span-3">
            <span className="text-[10px] font-bold uppercase text-[#FFCD11]">7. Prediction Dimension</span>
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-1">
              <div>
                <div className="font-bold text-white text-sm">
                  Completion Forecast: {twin?.prediction.estimated_remaining_minutes || 145} minutes remaining
                </div>
                <div className="text-gray-400 text-xs">
                  Model: Historical regression + Weather coefficient • Confidence: {Math.round((twin?.prediction.confidence_score || 0.92) * 100)}%
                </div>
              </div>
              <span className="text-xs font-mono font-bold text-purple-300 bg-purple-950 px-3 py-1.5 rounded-lg border border-purple-800">
                P10: 138 min | P90: 162 min
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* Operational Trends & Attention Reason */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        <div className="bg-[#181818] border border-[#2B2B2B] rounded-xl p-5 space-y-3">
          <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <TrendingUp className="w-4 h-4 text-emerald-400" />
            <span>Prediction & Productivity Trends</span>
          </h4>
          <p className="text-gray-400">
            Trench excavation rate is running at 104.5% of scheduled pace. Haul fleet cycle spacing is the primary operational variance factor.
          </p>
          <div className="bg-[#121212] p-3 rounded-lg border border-[#242424] space-y-1.5 font-mono">
            <div className="flex justify-between">
              <span className="text-gray-400">Mean Dig-to-Dump:</span>
              <span className="text-white">28.5 seconds</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Bucket Fill Factor:</span>
              <span className="text-emerald-400">92%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Truck Exchange Interval:</span>
              <span className="text-amber-400">18.2 min gap (Crusher delay)</span>
            </div>
          </div>
        </div>

        <div className="bg-[#181818] border border-[#2B2B2B] rounded-xl p-5 space-y-3">
          <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <Activity className="w-4 h-4 text-[#FFCD11]" />
            <span>Adaptive Attention Engine</span>
          </h4>
          <p className="text-gray-400">
            Backend operations intelligence derived current attention mode based on multi-dimensional telemetry:
          </p>
          <div className="bg-[#121212] p-3 rounded-lg border border-[#242424] space-y-1.5">
            <div className="text-xs text-white font-bold">Active Mode: {attentionMode}</div>
            <div className="text-xs text-gray-300 leading-relaxed">{attentionReason}</div>
            <div className="text-[10px] text-gray-500 pt-1 border-t border-[#222222]">
              Derived strictly by Operations Service backend. Zero local UI derivation.
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

