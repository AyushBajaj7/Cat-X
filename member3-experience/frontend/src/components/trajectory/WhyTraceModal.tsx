import React from 'react';
import { X, HelpCircle, Activity } from 'lucide-react';
import { WhyDecisionTrace } from '../../types';

interface WhyTraceModalProps {
  trace: WhyDecisionTrace | null;
  scenarioTitle: string;
  onClose: () => void;
}

export const WhyTraceModal: React.FC<WhyTraceModalProps> = ({ trace, scenarioTitle, onClose }) => {
  if (!trace) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-[#1C1C1C] border border-[#3E3E3E] rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-5 sm:p-6 shadow-2xl relative space-y-4">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-[#2C2C2C] pb-3">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-[#FFCD11]/20 text-[#FFCD11]">
              <HelpCircle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Decision Trace: "Why?"</h3>
              <p className="text-xs text-gray-400">{scenarioTitle}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-[#2C2C2C] transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Trace Content Grid */}
        <div className="space-y-3.5 text-xs">
          <div className="bg-[#141414] p-3 rounded-lg border border-[#262626]">
            <span className="text-gray-400 uppercase font-semibold text-[10px]">Triggering Signal</span>
            <div className="text-sm font-bold text-white mt-0.5">{trace.signal}</div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-[#141414] p-3 rounded-lg border border-[#262626]">
              <span className="text-gray-400 uppercase font-semibold text-[10px]">Observed Telemetry</span>
              <div className="text-base font-mono font-bold text-[#FFCD11] mt-0.5">{trace.value}</div>
            </div>
            <div className="bg-[#141414] p-3 rounded-lg border border-[#262626]">
              <span className="text-gray-400 uppercase font-semibold text-[10px]">Operating Baseline</span>
              <div className="text-base font-mono font-bold text-gray-300 mt-0.5">{trace.baseline}</div>
            </div>
          </div>

          <div className="bg-[#141414] p-3 rounded-lg border border-[#262626]">
            <span className="text-gray-400 uppercase font-semibold text-[10px]">Consequence Interpretation</span>
            <div className="text-xs font-medium text-gray-200 mt-1 leading-relaxed">{trace.interpretation}</div>
          </div>

          <div className="bg-[#141414] p-3 rounded-lg border border-[#262626] flex items-center justify-between">
            <span className="text-gray-400 uppercase font-semibold text-[10px]">Authoritative Source:</span>
            <span className="text-white font-mono font-semibold">{trace.source}</span>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-[#2D2D2D] hover:bg-[#3D3D3D] text-white font-bold text-xs transition"
          >
            Close Trace
          </button>
        </div>
      </div>
    </div>
  );
};

