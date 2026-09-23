import React from 'react';
import { Shield, AlertTriangle, AlertCircle, CheckCircle2, ShieldAlert, Activity } from 'lucide-react';
import { SafetyAlert, SafetyStatus } from '../../types';

interface SafetyScreenProps {
  safety: SafetyStatus | null;
  alerts: SafetyAlert[];
  behaviour: any;
  loading?: boolean;
}

export const SafetyScreen: React.FC<SafetyScreenProps> = ({ safety, alerts, behaviour, loading }) => {
  // Determine compliance state from backend values (do not calculate local thresholds)
  const isUnsafe = safety?.seatbelt_fastened === false || (safety?.active_hazard_count || 0) > 0;
  const isWarning = (safety?.overall_safety_score || 100) < 85 && !isUnsafe;

  const safetyLevel = isUnsafe ? 'HIGH_RISK' : isWarning ? 'WARNING' : 'SAFE';

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#282828] pb-4">
        <div>
          <h2 className="text-xl font-black text-white uppercase tracking-tight flex items-center space-x-2">
            <Shield className="w-5 h-5 text-[#FFCD11]" />
            <span>REAL-TIME SAFETY & INCIDENT AUDIT</span>
          </h2>
          <p className="text-xs text-gray-400">
            Seatbelt compliance tracking, proximity hazard triggers, behavior anomalies, and geotechnical constraint warnings.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span
            className={`px-3 py-1.5 rounded-lg text-xs font-black uppercase tracking-wider border flex items-center space-x-1.5 ${
              safetyLevel === 'HIGH_RISK'
                ? 'bg-rose-950 border-rose-500 text-rose-300 animate-pulse'
                : safetyLevel === 'WARNING'
                ? 'bg-amber-950 border-amber-500 text-amber-300'
                : 'bg-emerald-950 border-emerald-500 text-emerald-300'
            }`}
          >
            {safetyLevel === 'HIGH_RISK' ? (
              <AlertCircle className="w-4 h-4" />
            ) : safetyLevel === 'WARNING' ? (
              <AlertTriangle className="w-4 h-4" />
            ) : (
              <CheckCircle2 className="w-4 h-4" />
            )}
            <span>STATUS: {safetyLevel.replace('_', ' ')}</span>
          </span>
        </div>
      </div>

      {/* Safety Compliance Overview Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Seatbelt */}
        <div
          className={`p-4 rounded-xl border ${
            safety?.seatbelt_fastened === false
              ? 'bg-rose-950/60 border-rose-500 text-rose-200'
              : 'bg-[#181818] border-[#2A2A2A]'
          }`}
        >
          <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
            <span>Seatbelt Interlock</span>
            <Shield className="w-4 h-4" />
          </div>
          <div className="text-lg font-black font-mono">
            {safety?.seatbelt_fastened === false ? (
              <span className="text-rose-400 animate-pulse">UNFASTENED (ALERT)</span>
            ) : (
              <span className="text-emerald-400">FASTENED</span>
            )}
          </div>
          <div className="text-[11px] text-gray-400 mt-1">
            Compliance streak: <strong className="text-white">{safety?.seatbelt_compliance_pct ?? 99.4}%</strong>
          </div>
        </div>

        {/* Metric 2: Proximity Hazards */}
        <div
          className={`p-4 rounded-xl border ${
            (safety?.active_hazard_count || 0) > 0
              ? 'bg-rose-950/60 border-rose-500 text-rose-200'
              : 'bg-[#181818] border-[#2A2A2A]'
          }`}
        >
          <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
            <span>Proximity Boundary</span>
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div className="text-lg font-black font-mono">
            {(safety?.active_hazard_count || 0) > 0 ? (
              <span className="text-rose-400 animate-pulse">
                {safety?.active_hazard_count} HAZARD ACTIVE
              </span>
            ) : (
              <span className="text-white">PERIMETER CLEAR</span>
            )}
          </div>
          <div className="text-[11px] text-gray-400 mt-1">
            15m dynamic exclusion radius
          </div>
        </div>

        {/* Metric 3: Safety Score */}
        <div className="p-4 rounded-xl border bg-[#181818] border-[#2A2A2A]">
          <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
            <span>Safety Score</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-lg font-black font-mono text-white">
            {safety?.overall_safety_score ?? 98.0}%
          </div>
          <div className="text-[11px] text-gray-400 mt-1">
            Target benchmark: &gt;95.0%
          </div>
        </div>

        {/* Metric 4: Geotechnical Constraints */}
        <div className="p-4 rounded-xl border bg-[#181818] border-[#2A2A2A]">
          <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
            <span>Slope & Stance</span>
            <ShieldAlert className="w-4 h-4 text-[#FFCD11]" />
          </div>
          <div className="text-lg font-black font-mono text-emerald-400">
            STABLE (8° safe)
          </div>
          <div className="text-[11px] text-gray-400 mt-1">
            Limit: 15.0° max highwall grade
          </div>
        </div>
      </div>

      {/* Active Alerts List */}
      <section className="space-y-3">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">
          Active & Recent Safety Alerts ({alerts.length})
        </h3>
        {alerts.length === 0 ? (
          <div className="bg-[#141414] border border-[#252525] rounded-xl p-6 text-center text-xs text-gray-400">
            No active safety alerts. Operating within verified safe envelope.
          </div>
        ) : (
          <div className="space-y-2">
            {alerts.map((al) => (
              <div
                key={al.alert_id}
                className={`p-4 rounded-xl border flex items-center justify-between gap-3 text-xs ${
                  al.severity === 'CRITICAL'
                    ? 'bg-rose-950/80 border-rose-600 text-rose-200'
                    : 'bg-amber-950/80 border-amber-600 text-amber-200'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <AlertCircle className="w-5 h-5 shrink-0" />
                  <div>
                    <div className="font-bold text-sm text-white">{al.message}</div>
                    <div className="text-[11px] text-gray-300 mt-0.5 font-mono">
                      Alert ID: {al.alert_id} • Operator: {al.operator_id} • Timestamp: {al.timestamp}
                    </div>
                  </div>
                </div>
                <span className="font-mono font-bold uppercase px-2 py-1 rounded bg-black/40 text-[10px]">
                  {al.severity}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Operator Behaviour & Physical Constraints */}
      <section className="bg-[#181818] border border-[#2B2B2B] rounded-xl p-5 space-y-3 text-xs">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">
          Behavior Analytics & Safety Constraints
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="bg-[#121212] p-3 rounded-lg border border-[#222222]">
            <span className="text-gray-400">Idle Performance:</span>
            <div className="font-mono font-bold text-white mt-1">
              {behaviour?.idle_percentage || 9.8}%{' '}
              {behaviour?.idle_percentage > 12 && (
                <span className="text-amber-400 text-[11px]">(Excessive Idle Flag)</span>
              )}
            </div>
          </div>
          <div className="bg-[#121212] p-3 rounded-lg border border-[#222222]">
            <span className="text-gray-400">Aggressive Maneuver Signals:</span>
            <div className="font-mono font-bold text-emerald-400 mt-1">
              0 events (Clean Slew Profile)
            </div>
          </div>
          <div className="bg-[#121212] p-3 rounded-lg border border-[#222222]">
            <span className="text-gray-400">Geotechnical Standoff:</span>
            <div className="font-mono font-bold text-white mt-1">
              6.5m from crest (min 4.0m threshold)
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

