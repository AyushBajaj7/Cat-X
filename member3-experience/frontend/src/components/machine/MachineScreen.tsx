import React from 'react';
import { Cpu, Fuel, Activity, Clock, Shield, Compass, RotateCw } from 'lucide-react';
import { DemoState } from '../../types';

interface MachineScreenProps {
  demoState: DemoState | null;
}

export const MachineScreen: React.FC<MachineScreenProps> = ({ demoState }) => {
  const machineId = demoState?.machine_id || 'EXC-CAT-349D';
  const idlePct = demoState?.idle_percentage || 9.8;
  const fuelRate = demoState?.fuel_burn_rate_lph || 14.2;
  const seatbelt = demoState?.seatbelt_fastened !== false;
  const hazards = demoState?.active_hazard_count || 0;

  // Derive dynamic machine state based on demo step
  const getMachineState = () => {
    if (!seatbelt) return 'SAFETY_HOLD (SEATBELT UNBUCKLED)';
    if (hazards > 0) return 'PROXIMITY_HOLD (PERSONNEL IN ZONE)';
    if (idlePct > 13.0) return 'LOW_IDLE_STANDBY (CRUSHER WAIT)';
    if (demoState?.current_step === 7) return 'RE-SEQUENCING (UPPER BENCH 3)';
    return 'EXCAVATING & LOADING';
  };

  const machineState = getMachineState();

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#282828] pb-4">
        <div>
          <h2 className="text-xl font-black text-white uppercase tracking-tight flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-[#FFCD11]" />
            <span>MACHINE TELEMATICS & STATE</span>
          </h2>
          <p className="text-xs text-gray-400">
            Real-time CAN-bus instrumentation, hydraulic telemetry, and machine status.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-xs font-mono font-bold text-emerald-400">LIVE FEED SYNCED</span>
        </div>
      </div>

      {/* Primary Machine Overview Banner */}
      <section className="bg-gradient-to-r from-[#1E1E1E] via-[#242424] to-[#1E1E1E] border border-[#2F2F2F] rounded-2xl p-6 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2 text-xs">
              <span className="text-[#FFCD11] font-bold uppercase tracking-wider">Caterpillar 349 Series</span>
              <span className="text-gray-400">• Hydraulic Excavator</span>
            </div>
            <h3 className="text-2xl sm:text-3xl font-black text-white mt-1 font-mono">{machineId}</h3>
          </div>
          <div className="bg-[#121212] px-4 py-2 rounded-xl border border-[#333333] text-left sm:text-right">
            <span className="text-[10px] text-gray-400 uppercase font-bold">Active Machine State</span>
            <div className="text-sm font-black text-[#FFCD11] mt-0.5 font-mono">{machineState}</div>
          </div>
        </div>

        {/* Live Gauges Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 text-xs">
          <div className="bg-[#141414] p-3 rounded-xl border border-[#282828]">
            <span className="text-gray-400 uppercase text-[10px] font-semibold">Engine Operating Hours</span>
            <div className="text-xl font-mono font-black text-white mt-1">4,218.4 hrs</div>
            <div className="text-[10px] text-gray-500 mt-0.5">Shift: 3.5 hrs accumulated</div>
          </div>

          <div className="bg-[#141414] p-3 rounded-xl border border-[#282828]">
            <span className="text-gray-400 uppercase text-[10px] font-semibold">Instant Fuel Burn</span>
            <div className="text-xl font-mono font-black text-[#FFCD11] mt-1">{fuelRate} L/hr</div>
            <div className="text-[10px] text-gray-500 mt-0.5">Tank Level: 74% (480L remaining)</div>
          </div>

          <div className="bg-[#141414] p-3 rounded-xl border border-[#282828]">
            <span className="text-gray-400 uppercase text-[10px] font-semibold">Dig-and-Dump Cycles</span>
            <div className="text-xl font-mono font-black text-sky-400 mt-1">142 cycles</div>
            <div className="text-[10px] text-gray-500 mt-0.5">Avg cycle: 28.5s (Target 28.0s)</div>
          </div>

          <div className="bg-[#141414] p-3 rounded-xl border border-[#282828]">
            <span className="text-gray-400 uppercase text-[10px] font-semibold">Low-Idle Time Ratio</span>
            <div className={`text-xl font-mono font-black mt-1 ${idlePct > 12.0 ? 'text-amber-400' : 'text-emerald-400'}`}>
              {idlePct}%
            </div>
            <div className="text-[10px] text-gray-500 mt-0.5">Site Limit: &lt;12.0% idle</div>
          </div>
        </div>
      </section>

      {/* Detailed Sensor Strip */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
        <div className="bg-[#181818] border border-[#2B2B2B] rounded-xl p-5 space-y-3">
          <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <Activity className="w-4 h-4 text-[#FFCD11]" />
            <span>Hydraulic Subsystem Pressure</span>
          </h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center py-1 border-b border-[#242424]">
              <span className="text-gray-400">Implement Hydraulic Pump:</span>
              <span className="font-mono text-white font-bold">34,500 kPa</span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-[#242424]">
              <span className="text-gray-400">Slew Drive Hydraulic Motor:</span>
              <span className="font-mono text-white font-bold">22,100 kPa</span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-gray-400">Engine Coolant Temperature:</span>
              <span className="font-mono text-emerald-400 font-bold">88°C (Optimal)</span>
            </div>
          </div>
        </div>

        <div className="bg-[#181818] border border-[#2B2B2B] rounded-xl p-5 space-y-3">
          <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center space-x-2">
            <Shield className="w-4 h-4 text-emerald-400" />
            <span>Safety Interlocks & Sensors</span>
          </h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center py-1 border-b border-[#242424]">
              <span className="text-gray-400">3-Point Harness Switch:</span>
              <span className={`font-mono font-bold ${seatbelt ? 'text-emerald-400' : 'text-rose-400'}`}>
                {seatbelt ? 'ENGAGED' : 'DISENGAGED (INTERLOCK FAULT)'}
              </span>
            </div>
            <div className="flex justify-between items-center py-1 border-b border-[#242424]">
              <span className="text-gray-400">Proximity Radar 360°:</span>
              <span className={`font-mono font-bold ${hazards > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                {hazards > 0 ? '1 OBJECT WITHIN 12M' : 'ALL CLEAR (ZONE 15M)'}
              </span>
            </div>
            <div className="flex justify-between items-center py-1">
              <span className="text-gray-400">Hydraulic Lockout Lever:</span>
              <span className="font-mono text-white font-bold">ARMED (ACTIVE WORK)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

