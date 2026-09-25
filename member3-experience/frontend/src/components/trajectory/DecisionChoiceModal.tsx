import React, { useState } from 'react';
import { X, Check, Compass, ShieldAlert } from 'lucide-react';
import { TrajectoryScenario } from '../../types';

interface DecisionChoiceModalProps {
  scenario: TrajectoryScenario | null;
  operatorId: string;
  onConfirm: (scenarioId: string, reason: string, reasonCategory: string) => void;
  onClose: () => void;
  loading?: boolean;
}

export const DecisionChoiceModal: React.FC<DecisionChoiceModalProps> = ({
  scenario,
  operatorId,
  onConfirm,
  onClose,
  loading = false,
}) => {
  const [reasonCategory, setReasonCategory] = useState<string>('schedule');
  const [customReason, setCustomReason] = useState<string>('');

  if (!scenario) return null;

  const categories = [
    { id: 'site instruction', label: 'Site Instruction' },
    { id: 'safety concern', label: 'Safety Concern' },
    { id: 'equipment limitation', label: 'Equipment Limitation' },
    { id: 'experience', label: 'Operator Experience' },
    { id: 'schedule', label: 'Schedule & Rain Deadline' },
    { id: 'other', label: 'Other' },
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const finalReason =
      customReason.trim() ||
      `Operator selected ${scenario.title} due to ${reasonCategory} prioritization.`;
    onConfirm(scenario.scenario_id, finalReason, reasonCategory);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-[#1C1C1C] border border-[#3E3E3E] rounded-2xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-5 sm:p-6 shadow-2xl relative space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#2C2C2C] pb-3">
          <div className="flex items-center space-x-2.5">
            <div className="p-2 rounded-lg bg-[#FFCD11] text-[#111111]">
              <Compass className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Commit Tactical Trajectory</h3>
              <p className="text-xs text-gray-400">Human-in-the-Loop Decision Support</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-[#2C2C2C] transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Selected Scenario Preview */}
        <div className="bg-[#141414] p-4 rounded-xl border border-[#2B2B2B] space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#FFCD11]">
              Selected Alternative
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-300">
              FEASIBLE
            </span>
          </div>
          <h4 className="text-sm font-black text-white">{scenario.title}</h4>
          <p className="text-xs text-gray-300">{scenario.explanation}</p>

          <div className="grid grid-cols-3 gap-2 pt-2 border-t border-[#222222] text-xs">
            <div>
              <span className="text-[10px] text-gray-400">Duration:</span>
              <div className="font-mono font-bold text-white">
                {scenario.predicted_outcome.duration_minutes ?? 145} mins
              </div>
            </div>
            <div>
              <span className="text-[10px] text-gray-400">Fuel:</span>
              <div className="font-mono font-bold text-emerald-400">
                {scenario.predicted_outcome.fuel_liters}L
              </div>
            </div>
            <div>
              <span className="text-[10px] text-gray-400">Shift Delta:</span>
              <div className="font-mono font-bold text-[#FFCD11]">
                {scenario.predicted_outcome.shift_delay_minutes > 0
                  ? `+${scenario.predicted_outcome.shift_delay_minutes}m delay`
                  : `${Math.abs(scenario.predicted_outcome.shift_delay_minutes)}m saved`}
              </div>
            </div>
          </div>
        </div>

        {/* Operator Rationale Input */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-gray-300 mb-1.5">
              Why did you choose this trajectory? <span className="text-gray-500 font-normal">(Decision Memory)</span>
            </label>
            <div className="grid grid-cols-2 gap-2 mb-3">
              {categories.map((cat) => (
                <button
                  type="button"
                  key={cat.id}
                  onClick={() => setReasonCategory(cat.id)}
                  className={`px-3 py-2 rounded-lg text-xs font-semibold text-left transition border ${
                    reasonCategory === cat.id
                      ? 'bg-[#FFCD11]/20 border-[#FFCD11] text-[#FFCD11]'
                      : 'bg-[#141414] border-[#2A2A2A] text-gray-300 hover:bg-[#222222]'
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            <textarea
              value={customReason}
              onChange={(e) => setCustomReason(e.target.value)}
              placeholder="Optional tactical note for decision memory log (e.g. Bypassed haul truck queue before rain onset)..."
              className="w-full bg-[#121212] border border-[#2D2D2D] rounded-lg p-2.5 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-[#FFCD11]"
              rows={2}
            />
          </div>

          {/* Advisory Notice */}
          <div className="flex items-start space-x-2 bg-amber-950/30 border border-amber-800/40 p-2.5 rounded-lg text-[11px] text-amber-200">
            <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
            <span>
              <strong>Decision Support Only:</strong> Committing this trajectory logs the tactical choice into
              Shift Twin memory. It does NOT execute autonomous machine controls. The operator retains full physical control.
            </span>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end space-x-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg bg-[#262626] hover:bg-[#303030] text-gray-300 text-xs font-bold transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center space-x-1.5 px-5 py-2 rounded-lg bg-[#FFCD11] hover:bg-[#E0A800] text-[#111111] text-xs font-black uppercase tracking-wider transition shadow"
            >
              <Check className="w-4 h-4" />
              <span>{loading ? 'Recording...' : 'Commit Choice'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

