import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  BookOpen,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  RotateCcw,
  Sparkles,
  ShieldCheck,
  Award,
} from 'lucide-react';
import { ScenarioChoice, ScenarioStep, TrainingAttempt, TrainingModule } from '../../types';
import { fetchTrainingModule, submitTrainingAttempt } from '../../api/client';

export const TrainingScenarioPlayer: React.FC = () => {
  const { moduleId } = useParams<{ moduleId: string }>();
  const navigate = useNavigate();

  const [module, setModule] = useState<TrainingModule | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [selectedChoiceId, setSelectedChoiceId] = useState<string | null>(null);
  const [isAnswerSubmitted, setIsAnswerSubmitted] = useState<boolean>(false);
  const [mistakesCount, setMistakesCount] = useState<number>(0);
  const [startedAt, setStartedAt] = useState<string>(new Date().toISOString());
  const [isCompleted, setIsCompleted] = useState<boolean>(false);
  const [attemptResult, setAttemptResult] = useState<TrainingAttempt | null>(null);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!moduleId) return;
    setLoading(true);
    fetchTrainingModule(moduleId)
      .then((data) => {
        setModule(data);
        setStartedAt(new Date().toISOString());
      })
      .catch(() => {
        // Fallback demo module if offline
        setModule({
          module_id: moduleId,
          title: 'Interactive Module Simulator',
          description: 'Step-by-step simulator scenario.',
          objective: 'Complete safe and efficient operating decisions.',
          difficulty: 'INTERMEDIATE',
          estimated_minutes: 10,
          skills: ['safety checks', 'operational awareness'],
          steps: ['Identify startup conditions', 'Confirm safety context', 'Make safe decision'],
          scenario_steps: [
            {
              step_number: 1,
              title: 'Identify Startup Conditions',
              prompt: 'What is the required pre-operation check before turning the ignition?',
              choices: [
                {
                  choice_id: 'C1',
                  text: 'Perform 360-degree walkaround and verify machine stance and fluid levels.',
                  is_correct: true,
                  explanation: 'Standard Caterpillar pre-operation procedure.',
                },
                {
                  choice_id: 'C2',
                  text: 'Start engine immediately to warm hydraulic oil.',
                  is_correct: false,
                  explanation: 'Never ignite engine without physical walkaround check.',
                },
              ],
            },
            {
              step_number: 2,
              title: 'Confirm Seatbelt Compliance',
              prompt: 'The cab console displays an unbuckled seatbelt indicator. What is the required response?',
              choices: [
                {
                  choice_id: 'C1',
                  text: 'Fasten the 3-point harness and confirm cab safety light illuminates green.',
                  is_correct: true,
                  explanation: 'Seatbelt compliance is mandatory prior to hydraulic arming.',
                },
                {
                  choice_id: 'C2',
                  text: 'Rev engine throttle to silence the reminder buzzer.',
                  is_correct: false,
                  explanation: 'Overriding safety interlocks violates site rules.',
                },
              ],
            },
            {
              step_number: 3,
              title: 'Make Safe Operational Decision',
              prompt: 'Perimeter check reveals a support utility truck 25m away on the haul road. How do you proceed?',
              choices: [
                {
                  choice_id: 'C1',
                  text: 'Sound two horn blasts, disengage hydraulic lockout, and verify perimeter clearance before swing.',
                  is_correct: true,
                  explanation: 'Standard safe operating procedure.',
                },
                {
                  choice_id: 'C2',
                  text: 'Slew immediately at maximum throttle.',
                  is_correct: false,
                  explanation: 'Aggressive swing risks collision.',
                },
              ],
            },
          ],
        });
      })
      .finally(() => setLoading(false));
  }, [moduleId]);

  const steps: ScenarioStep[] = module?.scenario_steps || [];
  const currentStep = steps[currentStepIndex];

  const handleSelectChoice = (choiceId: string) => {
    if (isAnswerSubmitted) return;
    setSelectedChoiceId(choiceId);
  };

  const handleSubmitStep = () => {
    if (!selectedChoiceId || !currentStep) return;
    setIsAnswerSubmitted(true);
    const chosen = currentStep.choices.find((c) => c.choice_id === selectedChoiceId);
    if (!chosen?.is_correct) {
      setMistakesCount((prev) => prev + 1);
    }
  };

  const handleNextStep = async () => {
    if (currentStepIndex < steps.length - 1) {
      setCurrentStepIndex((prev) => prev + 1);
      setSelectedChoiceId(null);
      setIsAnswerSubmitted(false);
    } else {
      // Scenario complete -> calculate deterministic score
      await finishScenario();
    }
  };

  const finishScenario = async () => {
    setIsCompleted(true);
    setSubmitting(true);
    const completedAt = new Date().toISOString();
    // Deterministic scoring calculation:
    // 0 mistakes = 100%
    // 1 mistake = 80% (Pass threshold >= 80%)
    // 2 mistakes = 60%
    // 3+ mistakes = 40%
    const scoreVal = Math.max(40, 100 - mistakesCount * 20);
    const passed = scoreVal >= 80;

    const payload = {
      operator_id: 'OP1001',
      module_id: moduleId || 'SAFE_START_01',
      score: scoreVal,
      max_score: 100.0,
      mistakes: mistakesCount,
      started_at: startedAt,
      completed_at: completedAt,
      status: passed ? 'PASSED' : 'NEEDS_REVIEW',
    };

    try {
      const res = await submitTrainingAttempt(payload);
      setAttemptResult(res);
    } catch {
      setAttemptResult({
        attempt_id: 'ATT-LOCAL-RECORDED',
        operator_id: 'OP1001',
        module_id: moduleId || 'SAFE_START_01',
        started_at: startedAt,
        completed_at: completedAt,
        score: scoreVal,
        max_score: 100.0,
        percentage: scoreVal,
        mistakes: mistakesCount,
        passed,
        status: passed ? 'PASSED' : 'NEEDS_REVIEW',
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleRestart = () => {
    setCurrentStepIndex(0);
    setSelectedChoiceId(null);
    setIsAnswerSubmitted(false);
    setMistakesCount(0);
    setStartedAt(new Date().toISOString());
    setIsCompleted(false);
    setAttemptResult(null);
  };

  if (loading) {
    return (
      <div className="p-12 text-center text-xs text-gray-400">
        Loading module simulator scenario...
      </div>
    );
  }

  if (!module || steps.length === 0) {
    return (
      <div className="p-12 text-center space-y-3">
        <AlertCircle className="w-8 h-8 text-amber-400 mx-auto" />
        <div className="text-white font-bold text-sm">No interactive scenario available for {moduleId}</div>
        <button
          onClick={() => navigate('/training')}
          className="px-4 py-2 bg-[#2D2D2D] hover:bg-[#3D3D3D] text-white text-xs font-bold rounded-lg transition"
        >
          Return to Training Hub
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#282828] pb-4">
        <div>
          <div className="flex items-center space-x-2 text-xs text-[#FFCD11] font-mono font-bold uppercase">
            <span>{module.module_id}</span>
            <span className="text-gray-500">•</span>
            <span className="text-gray-300">{module.difficulty}</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-black text-white mt-0.5">{module.title}</h2>
          <p className="text-xs text-gray-300 mt-1">{module.objective}</p>
        </div>
        <button
          onClick={() => navigate('/training')}
          className="px-3 py-1.5 rounded-lg bg-[#252525] hover:bg-[#303030] text-gray-300 text-xs font-semibold self-start sm:self-center transition"
        >
          Exit Simulator
        </button>
      </div>

      {!isCompleted ? (
        /* Step Player Card */
        <div className="bg-[#181818] border border-[#2E2E2E] rounded-2xl p-6 shadow-xl space-y-5">
          {/* Progress header */}
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-white uppercase tracking-wider">
              Step {currentStepIndex + 1} of {steps.length}:{' '}
              <strong className="text-[#FFCD11]">{currentStep?.title}</strong>
            </span>
            <div className="flex items-center space-x-2">
              <span className="text-gray-400">Mistakes:</span>
              <span
                className={`font-mono font-bold px-2 py-0.5 rounded text-[11px] ${
                  mistakesCount > 0 ? 'bg-rose-950 text-rose-300' : 'bg-emerald-950 text-emerald-300'
                }`}
              >
                {mistakesCount}
              </span>
            </div>
          </div>

          {/* Step Progress Bar */}
          <div className="w-full bg-[#111111] h-2 rounded-full overflow-hidden border border-[#222222]">
            <div
              className="bg-[#FFCD11] h-full rounded-full transition-all"
              style={{ width: `${Math.round(((currentStepIndex + 1) / steps.length) * 100)}%` }}
            ></div>
          </div>

          {/* Prompt */}
          <div className="bg-[#141414] p-4 rounded-xl border border-[#282828]">
            <span className="text-[10px] uppercase font-bold text-gray-400">Scenario Prompt</span>
            <div className="text-sm font-bold text-white mt-1 leading-relaxed">
              {currentStep?.prompt}
            </div>
          </div>

          {/* Choices */}
          <div className="space-y-3">
            <span className="text-[10px] uppercase font-bold text-gray-400">Select Operational Decision</span>
            <div className="space-y-2">
              {currentStep?.choices.map((choice) => {
                const isSelected = selectedChoiceId === choice.choice_id;
                let choiceStyle = 'bg-[#141414] border-[#2A2A2A] text-gray-200 hover:border-[#FFCD11]/50';

                if (isAnswerSubmitted) {
                  if (choice.is_correct) {
                    choiceStyle = 'bg-emerald-950/60 border-emerald-500 text-emerald-200 font-bold';
                  } else if (isSelected && !choice.is_correct) {
                    choiceStyle = 'bg-rose-950/60 border-rose-500 text-rose-200 font-bold';
                  } else {
                    choiceStyle = 'bg-[#121212] border-[#222222] text-gray-500 opacity-60';
                  }
                } else if (isSelected) {
                  choiceStyle = 'bg-[#FFCD11]/15 border-[#FFCD11] text-[#FFCD11] font-bold shadow';
                }

                return (
                  <button
                    key={choice.choice_id}
                    onClick={() => handleSelectChoice(choice.choice_id)}
                    disabled={isAnswerSubmitted}
                    className={`w-full p-4 rounded-xl border text-left text-xs transition duration-150 flex items-start space-x-3 ${choiceStyle}`}
                  >
                    <span className="font-mono font-bold text-xs uppercase px-2 py-0.5 rounded bg-black/40 mt-0.5">
                      {choice.choice_id}
                    </span>
                    <span className="flex-1 leading-relaxed">{choice.text}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Feedback Area after step submission */}
          {isAnswerSubmitted && selectedChoiceId && (
            <div
              className={`p-4 rounded-xl border space-y-1 text-xs animate-fade-in ${
                currentStep.choices.find((c) => c.choice_id === selectedChoiceId)?.is_correct
                  ? 'bg-emerald-950/60 border-emerald-500 text-emerald-200'
                  : 'bg-rose-950/60 border-rose-500 text-rose-200'
              }`}
            >
              <div className="flex items-center space-x-2 font-bold">
                {currentStep.choices.find((c) => c.choice_id === selectedChoiceId)?.is_correct ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span>Correct Decision Confirmed</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-4 h-4 text-rose-400" />
                    <span>Operational Mistake Logged</span>
                  </>
                )}
              </div>
              <p className="text-[11px] leading-relaxed pt-1">
                {currentStep.choices.find((c) => c.choice_id === selectedChoiceId)?.explanation}
              </p>
            </div>
          )}

          {/* Footer Action */}
          <div className="pt-2 flex justify-end">
            {!isAnswerSubmitted ? (
              <button
                onClick={handleSubmitStep}
                disabled={!selectedChoiceId}
                className="w-full sm:w-auto justify-center px-6 py-2.5 rounded-xl bg-[#FFCD11] hover:bg-[#E0A800] text-[#111111] text-xs font-black uppercase tracking-wider disabled:opacity-40 transition shadow flex items-center"
              >
                Confirm Decision
              </button>
            ) : (
              <button
                onClick={handleNextStep}
                className="w-full sm:w-auto justify-center flex items-center space-x-2 px-6 py-2.5 rounded-xl bg-[#FFCD11] hover:bg-[#E0A800] text-[#111111] text-xs font-black uppercase tracking-wider transition shadow"
              >
                <span>{currentStepIndex < steps.length - 1 ? 'Next Step' : 'Review Results'}</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      ) : (
        /* Scenario Results & Deterministic Score Card */
        <div className="bg-[#181818] border border-[#2E2E2E] rounded-2xl p-6 shadow-2xl space-y-6">
          <div className="text-center space-y-2 border-b border-[#242424] pb-5">
            <div className="inline-flex p-3 rounded-2xl bg-[#FFCD11]/20 text-[#FFCD11] mb-2">
              <ShieldCheck className="w-8 h-8" />
            </div>
            <h3 className="text-2xl font-black text-white">Scenario Evaluation Completed</h3>
            <p className="text-xs text-gray-400">
              Deterministic skill and procedural scoring recorded for operator profile.
            </p>
          </div>

          {/* Score breakdown */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="bg-[#121212] p-3 rounded-xl border border-[#262626] text-center">
              <span className="text-gray-400 uppercase text-[10px] font-semibold">Total Score</span>
              <div className="text-2xl font-black font-mono text-white mt-1">
                {attemptResult?.score ?? 100} / 100
              </div>
            </div>

            <div className="bg-[#121212] p-3 rounded-xl border border-[#262626] text-center">
              <span className="text-gray-400 uppercase text-[10px] font-semibold">Percentage</span>
              <div
                className={`text-2xl font-black font-mono mt-1 ${
                  (attemptResult?.percentage || 100) >= 80 ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {attemptResult?.percentage ?? 100}%
              </div>
            </div>

            <div className="bg-[#121212] p-3 rounded-xl border border-[#262626] text-center">
              <span className="text-gray-400 uppercase text-[10px] font-semibold">Mistakes</span>
              <div className="text-2xl font-black font-mono text-white mt-1">
                {attemptResult?.mistakes ?? mistakesCount}
              </div>
            </div>

            <div className="bg-[#121212] p-3 rounded-xl border border-[#262626] text-center">
              <span className="text-gray-400 uppercase text-[10px] font-semibold">Evaluation Status</span>
              <div
                className={`text-sm font-black uppercase mt-2 ${
                  attemptResult?.passed ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {attemptResult?.passed ? 'PASSED (>= 80%)' : 'NEEDS REVIEW (< 80%)'}
              </div>
            </div>
          </div>

          {/* Deterministic Scoring Notice (Do NOT call it certification) */}
          <div className="bg-[#121212] p-3.5 rounded-xl border border-[#262626] text-[11px] text-gray-400 space-y-1">
            <div className="font-bold text-gray-300">Deterministic Skill Assessment:</div>
            <div>
              Scored deterministically based on verified operational step responses. This exercise reinforces situational awareness and does not certify heavy machinery operation.
            </div>
            <div className="font-mono text-[10px] text-gray-500 pt-1 border-t border-[#202020]">
              Attempt ID: {attemptResult?.attempt_id || 'ATT-RECORDED'} • Timestamp: {attemptResult?.completed_at}
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center justify-end space-x-3 pt-2">
            <button
              onClick={handleRestart}
              className="flex items-center space-x-1.5 px-4 py-2.5 rounded-xl bg-[#252525] hover:bg-[#303030] text-gray-300 text-xs font-bold transition"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Retry Scenario</span>
            </button>
            <button
              onClick={() => navigate('/training')}
              className="px-6 py-2.5 rounded-xl bg-[#FFCD11] hover:bg-[#E0A800] text-[#111111] text-xs font-black uppercase tracking-wider transition shadow"
            >
              Return to Training Hub
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

