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
    <div className="bg-[#181818] border-b border-[#2E2E2E] px-4 py-2 text-xs">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-3">
        {/* Scenario title and indicator */}
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-[#FFCD11]/10 border border-[#FFCD11]/30 text-[#FFCD11] font-bold">
            <Sparkles className="w-3.5 h-3.5 animate-pulse" />
            <span className="uppercase tracking-wider">Demo Scenario: "The 17-Minute Trap"</span>
          </div>
          <span className="text-gray-400 font-medium hidden sm:inline">
            Step {currentStep} of 10: <span className="text-white font-bold">{demoState?.step_name || 'STATE 1: NORMAL'}</span>
          </span>
        </div>

        {/* Step selector pills */}
        <div className="flex items-center space-x-1 overflow-x-auto py-1">
          {stepsList.map((s) => {
            const isActive = s.num === currentStep;
            const isCompleted = s.num < currentStep;
            return (
              <button
                key={s.num}
                type="button"
                onClick={() => onStepChange(s.num)}
                title={`Jump to Step ${s.num}: ${s.label}`}
                className={`px-2.5 py-1 rounded text-xs font-semibold transition cursor-pointer select-none flex items-center space-x-1 ${
                  isActive
                    ? 'bg-[#FFCD11] text-[#111111] shadow-md font-bold scale-105 ring-1 ring-[#FFCD11]'
                    : isCompleted
                    ? 'bg-[#2A2A2A] text-gray-300 hover:bg-[#383838] hover:text-white'
                    : 'bg-[#1C1C1C] text-gray-500 hover:text-gray-200 hover:bg-[#252525]'
                }`}
              >
                <span>{s.num}.</span>
                <span className="hidden md:inline">{s.label}</span>
              </button>
            );
          })}
        </div>

        {/* Controls: Prev / Next / Reset */}
        <div className="flex items-center space-x-2">
          {loading && (
            <span className="text-[10px] text-[#FFCD11] animate-pulse hidden lg:inline mr-1 font-mono">
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

