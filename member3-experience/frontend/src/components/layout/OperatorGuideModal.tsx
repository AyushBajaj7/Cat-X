import React from 'react';
import {
  X,
  Cpu,
  Shield,
  Compass,
  CheckCircle2,
  Sliders,
  HelpCircle,
  Truck,
  Activity,
  Layers,
} from 'lucide-react';

interface OperatorGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const OperatorGuideModal: React.FC<OperatorGuideModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
      <div className="bg-[#181818] border border-[#333333] rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl text-gray-200">
        {/* Header */}
        <div className="flex items-center justify-between p-5 border-b border-[#2A2A2A] sticky top-0 bg-[#181818] z-10">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-[#FFCD11]/20 text-[#FFCD11]">
              <HelpCircle className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-black text-white uppercase tracking-tight">
                CAT Operator Shift Twin • System Guide
              </h2>
              <p className="text-xs text-gray-400">Everything you need to know about your in-cab companion</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-[#252525] transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6 text-xs sm:text-sm">
          {/* 1. Single vs Multiple Machines */}
          <div className="p-4 rounded-xl bg-[#202020] border border-[#2E2E2E] space-y-2">
            <div className="flex items-center space-x-2 text-[#FFCD11] font-bold">
              <Cpu className="w-4 h-4" />
              <h3 className="uppercase text-xs tracking-wider">1. Does it track a single machine or multiple machines?</h3>
            </div>
            <p className="text-gray-300 leading-relaxed text-xs">
              <strong className="text-white">Your Cab is Single-Machine Focused:</strong> This companion is mounted in your excavator cabin (<code className="text-[#FFCD11] bg-black/40 px-1 py-0.5 rounded font-mono">EXC-CAT-349D</code>). It monitors <em>your</em> seatbelt, <em>your</em> cycle times, <em>your</em> idle rate, and <em>your</em> immediate 15-meter safety perimeter.
            </p>
            <div className="flex items-center space-x-2 pt-1 text-xs text-gray-400">
              <Truck className="w-3.5 h-3.5 text-sky-400" />
              <span><strong>Fleet Situational Awareness:</strong> It also tracks the 4 haul trucks in your fleet cycle and support vehicles, alerting you if trucks are delayed at the crusher or enter your swing radius.</span>
            </div>
          </div>

          {/* 2. How does it keep track? */}
          <div className="p-4 rounded-xl bg-[#202020] border border-[#2E2E2E] space-y-2">
            <div className="flex items-center space-x-2 text-emerald-400 font-bold">
              <Activity className="w-4 h-4" />
              <h3 className="uppercase text-xs tracking-wider">2. How does it keep track of the machine?</h3>
            </div>
            <p className="text-gray-300 leading-relaxed text-xs">
              Continuous live telemetry streams directly into the digital twin through machine sensors:
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-gray-300">
              <div className="bg-[#181818] p-2.5 rounded-lg border border-[#2A2A2A]">
                <strong className="text-white block mb-0.5">🛡️ Safety Telemetry:</strong>
                Seatbelt latch switch, 360° LiDAR proximity radar (15m radius), highwall geotechnical slope inclinometer (15° safety limit).
              </div>
              <div className="bg-[#181818] p-2.5 rounded-lg border border-[#2A2A2A]">
                <strong className="text-white block mb-0.5">⚙️ Operations & Engine:</strong>
                CAN-bus engine RPM (detecting idle fuel burn at 1800 RPM), bucket payload scales, and haul fleet GPS timestamps.
              </div>
            </div>
          </div>

          {/* 3. Do you need to switch tabs? */}
          <div className="p-4 rounded-xl bg-[#202020] border border-[#2E2E2E] space-y-2">
            <div className="flex items-center space-x-2 text-sky-400 font-bold">
              <Layers className="w-4 h-4" />
              <h3 className="uppercase text-xs tracking-wider">3. Do you need to switch tabs during digging?</h3>
            </div>
            <p className="text-gray-300 leading-relaxed text-xs">
              <strong className="text-white font-bold">NO. Stay on the Shift Cockpit!</strong> The <strong>Shift Cockpit</strong> is designed as an all-in-one Heads-Up Display (HUD). It automatically updates whenever conditions change:
            </p>
            <ul className="list-disc list-inside space-y-1 text-xs text-gray-400">
              <li>If you unbuckle your harness, a red <strong className="text-rose-400">SAFETY FOCUS</strong> banner illuminates right at the top.</li>
              <li>If haul fleet trucks bunch up at the crusher, an amber <strong className="text-[#FFCD11]">DECISION FOCUS</strong> banner appears.</li>
              <li>The other tabs (<em>Safety, Machine, Training, Decision Memory</em>) are optional deep-dives for shift breaks, pre-shift review, or supervisor audits.</li>
            </ul>
          </div>

          {/* 4. Where is the consolidated outcome? */}
          <div className="p-4 rounded-xl bg-[#202020] border border-[#2E2E2E] space-y-2">
            <div className="flex items-center space-x-2 text-purple-400 font-bold">
              <CheckCircle2 className="w-4 h-4" />
              <h3 className="uppercase text-xs tracking-wider">4. Where do you see the consolidated outcome?</h3>
            </div>
            <p className="text-gray-300 leading-relaxed text-xs">
              Directly on the main screen:
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-xs">
              <div className="bg-[#181818] p-2 rounded-lg border border-[#2A2A2A]">
                <span className="text-[10px] text-gray-400 block uppercase">Shift Health</span>
                <span className="text-base font-black text-white">96%</span>
              </div>
              <div className="bg-[#181818] p-2 rounded-lg border border-[#2A2A2A]">
                <span className="text-[10px] text-gray-400 block uppercase">Safety Index</span>
                <span className="text-base font-black text-emerald-400">98%</span>
              </div>
              <div className="bg-[#181818] p-2 rounded-lg border border-[#2A2A2A]">
                <span className="text-[10px] text-gray-400 block uppercase">Finish ETA</span>
                <span className="text-base font-black text-[#FFCD11]">145 mins</span>
              </div>
              <div className="bg-[#181818] p-2 rounded-lg border border-[#2A2A2A]">
                <span className="text-[10px] text-gray-400 block uppercase">Next Best Action</span>
                <span className="text-xs font-bold text-sky-300 block truncate">Auto-Suggested</span>
              </div>
            </div>
          </div>

          {/* 5. What changes can the operator make? */}
          <div className="p-4 rounded-xl bg-[#202020] border border-[#2E2E2E] space-y-2">
            <div className="flex items-center space-x-2 text-amber-400 font-bold">
              <Compass className="w-4 h-4" />
              <h3 className="uppercase text-xs tracking-wider">5. What changes can you (the operator) make?</h3>
            </div>
            <div className="space-y-2 text-xs text-gray-300">
              <div className="flex items-start space-x-2">
                <span className="text-[#FFCD11] font-bold">A.</span>
                <div>
                  <strong className="text-white">Choose CAT Recovery Trajectories:</strong> When delays or rain threaten your shift, click <code className="text-[#FFCD11] bg-black/40 px-1 py-0.5 rounded font-mono">Inspect Trajectories</code> to evaluate alternative digging sequences (e.g. pre-stripping Bench 3 vs waiting). You pick the path, enter your reason, and commit it.
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <span className="text-sky-400 font-bold">B.</span>
                <div>
                  <strong className="text-white">Run What-If Parameter Simulations:</strong> On the <code className="text-sky-300 bg-black/40 px-1 py-0.5 rounded font-mono">What-If</code> screen, adjust swing angle, target tons/hr, or idle limits to preview time and fuel savings before changing tactics.
                </div>
              </div>
              <div className="flex items-start space-x-2">
                <span className="text-emerald-400 font-bold">C.</span>
                <div>
                  <strong className="text-white">Take Corrective Actions:</strong> Fasten seatbelt to restore safety streak; halt boom swing to clear proximity buffer; complete 2-minute micro-training modules.
                </div>
              </div>
            </div>
          </div>

          {/* 6. What is the top 10-step bar? */}
          <div className="p-4 rounded-xl bg-[#241A05] border border-[#FFCD11]/40 space-y-2">
            <div className="flex items-center space-x-2 text-[#FFCD11] font-bold">
              <Sliders className="w-4 h-4" />
              <h3 className="uppercase text-xs tracking-wider">6. What is the top "10 Steps" bar?</h3>
            </div>
            <p className="text-xs text-gray-300 leading-relaxed">
              The bar at the very top is a <strong className="text-white">Scenario Simulator</strong> demonstrating a full shift story: <strong className="text-[#FFCD11]">"The 17-Minute Trap"</strong>.
              Clicking steps 1 to 10 lets you jump to different moments in time (normal shift ➔ seatbelt event ➔ proximity alert ➔ haul fleet queue delay ➔ tactical trajectory choice ➔ outcome replay ➔ decision memory).
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#2A2A2A] bg-[#161616] flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-[#FFCD11] hover:bg-[#E0A800] text-black font-black text-xs uppercase tracking-wider transition shadow-lg"
          >
            Got It • Return to Cockpit
          </button>
        </div>
      </div>
    </div>
  );
};
