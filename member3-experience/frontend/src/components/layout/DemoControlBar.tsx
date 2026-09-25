import React from 'react';
import { RotateCcw, ChevronRight, ChevronLeft, Play, Sparkles } from 'lucide-react';
import { DemoState } from '../../types';

interface DemoControlBarProps {
  demoState: DemoState | null;
  onStepChange: (step: number) => void;
  onReset: () => void;
  loading?: boolean;
}

export const DemoControlBar: React.FC<DemoControlBarProps> = ({
  demoState,
  onStepChange,
  onReset,
  loading = false,
}) => {
  const currentStep = demoState?.current_step || 1;

  const stepsList = [
    { num: 1, label: 'Normal' },
    { num: 2, label: 'Seatbelt' },
    { num: 3, label: 'Proximity' },
    { num: 4, label: 'High Idle' },
    { num: 5, label: 'Decision Point' },
    { num: 6, label: 'Trajectories' },
    { num: 7, label: 'Human Choice' },
    { num: 8, label: 'Outcome Replay' },
    { num: 9, label: 'Memory' },
    { num: 10, label: 'Similar Context' },
  ];

  return (
    <div className="bg-[#181818] border-b border-[#2E2E2E] px-3 sm:px-4 py-2 text-xs">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-stretch md:items-center justify-between gap-2">
        {/* Top bar on mobile / Left section on desktop: Title, step indicator & Prev/Next controls */}
        <div className="flex items-center justify-between gap-2 w-full md:w-auto shrink-0">
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-[#FFCD11]/10 border border-[#FFCD11]/30 text-[#FFCD11] font-bold shrink-0">
              <Sparkles className="w-3.5 h-3.5 animate-pulse" />
              <span className="uppercase tracking-wider hidden sm:inline">Demo Scenario: "The 17-Minute Trap"</span>
              <span className="uppercase tracking-wider sm:hidden">17-Min Trap</span>
            </div>
            <span className="text-gray-400 font-medium text-[11px] sm:text-xs whitespace-nowrap">
              Step <strong className="text-white">{currentStep}</strong>/10
            </span>
          </div>

          {/* Quick Prev / Next / Reset controls on mobile */}
          <div className="flex items-center space-x-1.5 md:hidden">
            <button
              type="button"
              onClick={() => onStepChange(Math.max(1, currentStep - 1))}
              disabled={currentStep <= 1}
              className="p-1 rounded bg-[#2A2A2A] hover:bg-[#333333] text-gray-200 disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer transition"
              title="Previous Step"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={() => onStepChange(Math.min(10, currentStep + 1))}
              disabled={currentStep >= 10}
              className="flex items-center space-x-1 px-2.5 py-1 rounded bg-[#FFCD11] hover:bg-[#E0A800] text-[#111111] font-bold text-xs disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer shadow transition"
              title="Next Step"
            >
              <span>Next</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={onReset}
              className="p-1 rounded bg-[#2A2A2A] hover:bg-rose-900/50 hover:text-rose-300 text-gray-300 border border-[#3A3A3A] cursor-pointer transition"
              title="Reset Scenario"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Step selector pills carousel (Horizontal scroll on mobile/tablet, flex wrap on large screens) */}
        <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5 scroll-smooth flex-1 min-w-0 mx-0 md:mx-2">
          <span className="text-[10px] sm:text-[11px] font-bold text-gray-500 uppercase tracking-wider hidden lg:inline mr-1 shrink-0">
            Shift Events:
          </span>
          {stepsList.map((s) => {
            const isActive = s.num === currentStep;
            const isCompleted = s.num < currentStep;
            return (
              <button
                key={s.num}
                type="button"
                onClick={() => onStepChange(s.num)}
                title={`Jump to Step ${s.num}: ${s.label}`}
                className={`px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer select-none flex items-center space-x-1.5 shrink-0 border ${
                  isActive
                    ? 'bg-[#FFCD11] border-[#FFCD11] text-[#111111] shadow-lg font-black scale-105 ring-2 ring-[#FFCD11]/50'
                    : isCompleted
                    ? 'bg-[#252525] border-[#3E3E3E] text-gray-200 hover:bg-[#333333] hover:border-[#FFCD11]/60 hover:text-white'
                    : 'bg-[#1E1E1E] border-[#333333] text-gray-300 hover:bg-[#2A2A2A] hover:border-[#FFCD11]/60 hover:text-white'
                }`}
              >
                <span className={`px-1.5 py-0.5 rounded text-[10px] font-black ${
                  isActive ? 'bg-black text-[#FFCD11]' : 'bg-[#2A2A2A] text-gray-300'
                }`}>
                  {s.num}
                </span>
                <span className="whitespace-nowrap">{s.label}</span>
              </button>
            );
          })}
        </div>

        {/* Controls: Prev / Next / Reset on desktop */}
        <div className="hidden md:flex items-center space-x-2 shrink-0">
          {loading && (
            <span className="text-[10px] text-[#FFCD11] animate-pulse hidden xl:inline mr-1 font-mono">
              ● syncing
            </span>
          )}
          <button
            type="button"
            onClick={() => onStepChange(Math.max(1, currentStep - 1))}
            disabled={currentStep <= 1}
            className="p-1.5 rounded bg-[#2A2A2A] hover:bg-[#333333] text-gray-200 disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer transition"
            title="Previous Step"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={() => onStepChange(Math.min(10, currentStep + 1))}
            disabled={currentStep >= 10}
            className="flex items-center space-x-1 px-3 py-1.5 rounded bg-[#FFCD11] hover:bg-[#E0A800] text-[#111111] font-bold disabled:opacity-30 disabled:cursor-not-allowed cursor-pointer shadow transition"
            title="Advance to Next Step"
          >
            <span>Next</span>
            <ChevronRight className="w-4 h-4" />
          </button>
          <button
            type="button"
            onClick={onReset}
            className="flex items-center space-x-1 px-2.5 py-1.5 rounded bg-[#2A2A2A] hover:bg-rose-900/50 hover:text-rose-300 text-gray-300 border border-[#3A3A3A] font-semibold cursor-pointer transition"
            title="Reset Scenario to Step 1"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        </div>
      </div>
    </div>
  );
};

