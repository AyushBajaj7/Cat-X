import React from 'react';
import { Compass, Sparkles, CheckCircle2, Clock, AlertCircle, ArrowRight, BookOpen } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { DecisionMemory, SimilarContext } from '../../types';

interface DecisionMemoryScreenProps {
  memories: DecisionMemory[];
  similarContext: SimilarContext | null;
}

export const DecisionMemoryScreen: React.FC<DecisionMemoryScreenProps> = ({
  memories,
  similarContext,
}) => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Similar Situation Found Banner */}
      {similarContext && (
        <section className="bg-gradient-to-r from-amber-950/80 via-[#261E0A] to-amber-950/80 border-2 border-[#FFCD11] rounded-2xl p-6 shadow-2xl space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 rounded-xl bg-[#FFCD11] text-[#111111] font-black">
                <Sparkles className="w-5 h-5 animate-pulse" />
              </div>
              <div>
                <span className="text-xs font-black uppercase tracking-wider text-[#FFCD11]">
                  Context Signature Match • {similarContext.similarity_score_pct}% Match
                </span>
                <h3 className="text-xl font-black text-white">{similarContext.banner}</h3>
              </div>
            </div>
            <div className="text-xs font-mono font-bold text-gray-300 bg-black/40 px-3 py-1.5 rounded-lg border border-[#3A3A3A]">
              Signature: {similarContext.context_signature}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-xs bg-black/50 p-4 rounded-xl border border-amber-900/40">
            <div>
              <span className="text-gray-400 uppercase text-[10px] font-semibold">Previous Context</span>
              <div className="font-bold text-white mt-0.5">{similarContext.previous_context.task}</div>
              <div className="text-gray-400 text-[11px]">{similarContext.previous_context.weather}</div>
            </div>
            <div>
              <span className="text-gray-400 uppercase text-[10px] font-semibold">Historical Action Chosen</span>
              <div className="font-bold text-[#FFCD11] mt-0.5">{similarContext.previous_action}</div>
            </div>
            <div>
              <span className="text-gray-400 uppercase text-[10px] font-semibold">Predicted vs Actual</span>
              <div className="text-gray-300 mt-0.5">Pred: {similarContext.previous_prediction}</div>
              <div className="font-bold text-emerald-400">Act: {similarContext.actual_result}</div>
            </div>
            <div>
              <span className="text-gray-400 uppercase text-[10px] font-semibold">Key Learning Preserved</span>
              <div className="text-gray-200 mt-0.5 leading-snug">{similarContext.key_learning}</div>
            </div>
          </div>

          {/* Operator Control Notice & Training Link */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 text-xs">
            <span className="text-amber-200 font-medium">
              ⚠️ {similarContext.operator_in_control_notice}
            </span>
            {similarContext.recommended_training && (
              <button
                onClick={() => navigate(`/training/${similarContext.recommended_training!.module_id}`)}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#FFCD11] hover:bg-[#E0A800] text-[#111111] font-bold transition"
              >
                <BookOpen className="w-3.5 h-3.5" />
                <span>Launch {similarContext.recommended_training.title} Module</span>
              </button>
            )}
          </div>
        </section>
      )}

      {/* Decision Memory List */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-black text-white uppercase tracking-tight flex items-center space-x-2">
              <Compass className="w-5 h-5 text-[#FFCD11]" />
              <span>Historical Decision Memory</span>
            </h3>
            <p className="text-xs text-gray-400">
              Audited operational decisions, context signatures, and prediction-vs-actual outcomes.
            </p>
          </div>
          <span className="text-xs text-gray-400 font-mono">
            {memories.length} decisions logged
          </span>
        </div>

        <div className="space-y-3">
          {memories.map((mem) => (
            <div
              key={mem.decision_id}
              className="bg-[#181818] border border-[#2B2B2B] rounded-xl p-5 shadow hover:border-[#3E3E3E] transition space-y-3"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#242424] pb-2.5">
                <div className="flex items-center space-x-2.5">
                  <div className="p-1.5 rounded-lg bg-[#FFCD11]/20 text-[#FFCD11]">
                    <Compass className="w-4 h-4" />
                  </div>
                  <div>
                    <span className="font-mono font-bold text-white text-sm">{mem.decision_id}</span>
                    <span className="text-xs text-gray-400 ml-2">Operator {mem.operator_id}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-3 text-xs">
                  <span className="font-mono text-gray-400">Context: <strong className="text-white">{mem.context_signature}</strong></span>
                  <span className="text-gray-500">•</span>
                  <span className="text-gray-400">{new Date(mem.timestamp).toLocaleString()}</span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div className="bg-[#121212] p-3 rounded-lg border border-[#222222]">
                  <span className="text-gray-400 uppercase text-[10px] font-semibold">Chosen Trajectory</span>
                  <div className="font-bold text-white mt-1 text-sm">{mem.chosen_scenario}</div>
                  <div className="text-gray-400 mt-1 italic">"{mem.operator_reason}"</div>
                </div>

                <div className="bg-[#121212] p-3 rounded-lg border border-[#222222]">
                  <span className="text-gray-400 uppercase text-[10px] font-semibold">Predicted Outcome</span>
                  <div className="space-y-0.5 mt-1 font-mono text-gray-300">
                    <div>ETA: {mem.predicted_outcome?.eta_minutes ?? 145} min</div>
                    <div>Fuel: {mem.predicted_outcome?.fuel_liters ?? 168} L</div>
                    <div>Delay: {mem.predicted_outcome?.shift_delay_minutes ?? -17} min</div>
                  </div>
                </div>

                <div className="bg-[#121212] p-3 rounded-lg border border-[#222222]">
                  <span className="text-gray-400 uppercase text-[10px] font-semibold">Simulated / Actual Outcome</span>
                  <div className="space-y-0.5 mt-1 font-mono text-emerald-400 font-bold">
                    <div>ETA: {mem.actual_outcome?.eta_minutes ?? 146.5} min</div>
                    <div>Fuel: {mem.actual_outcome?.fuel_liters ?? 167.2} L</div>
                    <div>Saved: 15.8 min ahead of rain</div>
                  </div>
                  {mem.prediction_error && (
                    <div className="text-[10px] text-gray-400 mt-1 pt-1 border-t border-[#222222]">
                      Error: +{mem.prediction_error?.eta_delta_minutes ?? 1.5} min ETA, {mem.prediction_error?.fuel_delta_liters ?? -0.8}L Fuel
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

