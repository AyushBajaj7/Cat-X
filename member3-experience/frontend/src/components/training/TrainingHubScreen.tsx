import React from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, CheckCircle2, Clock, Sparkles, Award, ArrowRight, ShieldCheck } from 'lucide-react';
import { TrainingModule, TrainingProgress, TrainingRecommendation } from '../../types';

interface TrainingHubScreenProps {
  modules: TrainingModule[];
  recommendations: TrainingRecommendation[];
  progress: TrainingProgress | null;
  loading?: boolean;
}

export const TrainingHubScreen: React.FC<TrainingHubScreenProps> = ({
  modules,
  recommendations,
  progress,
  loading,
}) => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#282828] pb-4">
        <div>
          <h2 className="text-xl font-black text-white uppercase tracking-tight flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-[#FFCD11]" />
            <span>OPERATOR TRAINING HUB & MICRO-LEARNING</span>
          </h2>
          <p className="text-xs text-gray-400">
            Interactive shift prep, situational hazard responses, efficiency scenarios, and decision awareness.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs px-2.5 py-1 rounded-lg bg-[#252525] border border-[#3A3A3A] text-gray-300 font-mono">
            Deterministic Evaluation (No Certification Pretension)
          </span>
        </div>
      </div>

      {/* Recommended Modules (Triggered by Contextual Signals) */}
      <section className="space-y-3">
        <div className="flex items-center space-x-2">
          <Sparkles className="w-4 h-4 text-[#FFCD11]" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Context-Triggered Recommendations
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recommendations.map((rec) => (
            <div
              key={rec.recommendation_id}
              className="bg-[#1A1A1A] border border-[#FFCD11]/40 rounded-2xl p-5 shadow-lg flex flex-col justify-between space-y-3 hover:border-[#FFCD11] transition"
            >
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold text-[#FFCD11] uppercase tracking-wider">
                    {rec.module_id}
                  </span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#FFCD11]/20 text-[#FFCD11] uppercase">
                    {rec.urgency} URGENCY
                  </span>
                </div>
                <h4 className="text-base font-bold text-white">{rec.module_title}</h4>
                <p className="text-xs text-gray-300 leading-relaxed">{rec.reason}</p>
              </div>
              <button
                onClick={() => navigate(`/training/${rec.module_id}`)}
                className="w-full py-2 px-3 rounded-lg bg-[#FFCD11] hover:bg-[#E0A800] text-[#111111] text-xs font-black uppercase tracking-wider shadow transition flex items-center justify-center space-x-1.5"
              >
                <span>Launch Interactive Scenario</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Training Progress & Skills Tracking */}
      {progress && (
        <section className="bg-[#181818] border border-[#2B2B2B] rounded-2xl p-5 shadow space-y-4">
          <div className="flex items-center justify-between border-b border-[#242424] pb-3">
            <div className="flex items-center space-x-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Operator Skill & Compliance Record
              </h3>
            </div>
            <span className="text-xs text-gray-400 font-mono">Operator {progress.operator_id}</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="bg-[#121212] p-3 rounded-lg border border-[#252525]">
              <span className="text-gray-400 uppercase text-[10px] font-semibold">Completed Modules</span>
              <div className="text-xl font-mono font-black text-white mt-0.5">
                {progress.completed_modules_count} modules
              </div>
            </div>
            <div className="bg-[#121212] p-3 rounded-lg border border-[#252525]">
              <span className="text-gray-400 uppercase text-[10px] font-semibold">Average Passing Score</span>
              <div className="text-xl font-mono font-black text-emerald-400 mt-0.5">
                {progress.average_score_pct}%
              </div>
            </div>
            <div className="bg-[#121212] p-3 rounded-lg border border-[#252525]">
              <span className="text-gray-400 uppercase text-[10px] font-semibold">Proficiency Badges</span>
              <div className="text-xs font-bold text-gray-200 mt-1">
                {progress.certifications_earned.join(' • ')}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Module Catalog Library */}
      <section className="space-y-3">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">
          Module Library Catalog ({modules.length})
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {modules.map((m) => (
            <div
              key={m.module_id}
              className="bg-[#181818] border border-[#282828] rounded-2xl p-5 shadow space-y-3 hover:border-[#3A3A3A] transition flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold text-[#FFCD11]">{m.module_id}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#262626] text-gray-300 uppercase">
                      {m.difficulty}
                    </span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#262626] text-gray-300 flex items-center space-x-1">
                      <Clock className="w-3 h-3" />
                      <span>{m.estimated_minutes}m</span>
                    </span>
                  </div>
                </div>

                <h4 className="text-base font-bold text-white">{m.title}</h4>
                <p className="text-xs text-gray-300 leading-relaxed">{m.description}</p>

                <div className="bg-[#121212] p-2.5 rounded-lg border border-[#222222] text-xs">
                  <span className="text-gray-400 text-[10px] font-semibold uppercase">Objective:</span>
                  <div className="text-white mt-0.5">{m.objective}</div>
                </div>

                <div className="flex flex-wrap gap-1.5 pt-1">
                  {m.skills?.map((sk, idx) => (
                    <span
                      key={idx}
                      className="text-[10px] px-2 py-0.5 rounded bg-[#222222] text-gray-300 border border-[#333333]"
                    >
                      {sk}
                    </span>
                  ))}
                </div>
              </div>

              <button
                onClick={() => navigate(`/training/${m.module_id}`)}
                className="w-full mt-3 py-2 px-3 rounded-lg bg-[#252525] hover:bg-[#FFCD11] hover:text-[#111111] text-gray-200 text-xs font-bold transition flex items-center justify-center space-x-1.5"
              >
                <span>Start Module Simulator</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

