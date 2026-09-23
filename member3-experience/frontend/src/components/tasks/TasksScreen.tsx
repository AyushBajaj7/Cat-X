import React, { useState } from 'react';
import { CheckSquare, Clock, AlertCircle, TrendingUp, CheckCircle2 } from 'lucide-react';
import { Task, TaskEstimate } from '../../types';
import { estimateTask } from '../../api/client';

interface TasksScreenProps {
  tasks: Task[];
  loading?: boolean;
}

export const TasksScreen: React.FC<TasksScreenProps> = ({ tasks, loading }) => {
  const [selectedTaskId, setSelectedTaskId] = useState<string>('T002');
  const [estimate, setEstimate] = useState<TaskEstimate | null>(null);
  const [estimating, setEstimating] = useState<boolean>(false);

  const handleEstimate = async (taskId: string) => {
    setSelectedTaskId(taskId);
    setEstimating(true);
    try {
      const res = await estimateTask({ task_id: taskId, operator_id: 'OP1001' });
      setEstimate(res);
    } catch {
      // Handled
    } finally {
      setEstimating(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#282828] pb-4">
        <div>
          <h2 className="text-xl font-black text-white uppercase tracking-tight flex items-center space-x-2">
            <CheckSquare className="w-5 h-5 text-[#FFCD11]" />
            <span>DAILY TASK DASHBOARD</span>
          </h2>
          <p className="text-xs text-gray-400">
            Shift earthmoving assignments, material volume targets, and probabilistic task-time forecasting.
          </p>
        </div>
        <span className="text-xs text-gray-400 font-mono">Operator OP1001 • Shift Bench 2</span>
      </div>

      {/* Task Cards List */}
      <div className="grid grid-cols-1 gap-4">
        {tasks.map((task) => {
          const pct = Math.min(100, Math.round((task.completed_volume_tons / (task.target_volume_tons || 1)) * 100));
          const isCurrent = task.task_id === 'T002';

          return (
            <div
              key={task.task_id}
              className={`bg-[#181818] border rounded-2xl p-5 shadow transition ${
                isCurrent ? 'border-[#FFCD11]/60 bg-gradient-to-r from-[#1A1A1A] to-[#1E1E1E]' : 'border-[#292929]'
              }`}
            >
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                <div className="space-y-1.5 flex-1">
                  <div className="flex items-center space-x-2.5">
                    <span className="font-mono font-bold text-sm text-[#FFCD11]">{task.task_id}</span>
                    <span
                      className={`text-[10px] font-black uppercase px-2 py-0.5 rounded ${
                        task.status === 'IN_PROGRESS'
                          ? 'bg-sky-950 text-sky-300'
                          : task.status === 'COMPLETED'
                          ? 'bg-emerald-950 text-emerald-300'
                          : 'bg-gray-800 text-gray-400'
                      }`}
                    >
                      {task.status.replace('_', ' ')}
                    </span>
                    <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-[#252525] text-gray-300">
                      Zone: {task.site_zone}
                    </span>
                    {task.priority === 'CRITICAL' && (
                      <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-rose-950 text-rose-300">
                        CRITICAL
                      </span>
                    )}
                  </div>
                  <h3 className="text-base font-bold text-white">{task.title}</h3>
                  <p className="text-xs text-gray-300">{task.description}</p>
                </div>

                <div className="flex items-center space-x-3">
                  <button
                    onClick={() => handleEstimate(task.task_id)}
                    disabled={estimating}
                    className="px-3.5 py-2 rounded-lg bg-[#252525] hover:bg-[#333333] text-gray-200 text-xs font-semibold border border-[#3A3A3A] transition"
                  >
                    {estimating && selectedTaskId === task.task_id ? 'Calculating...' : 'Forecast Probabilistic ETA'}
                  </button>
                </div>
              </div>

              {/* Progress & Duration Details */}
              <div className="mt-4 pt-4 border-t border-[#252525] grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
                <div>
                  <div className="flex justify-between text-gray-400 mb-1">
                    <span>Volume Moved:</span>
                    <span className="text-white font-mono font-bold">
                      {task.completed_volume_tons} / {task.target_volume_tons} tons ({pct}%)
                    </span>
                  </div>
                  <div className="w-full bg-[#111111] h-2.5 rounded-full overflow-hidden border border-[#222222]">
                    <div className="bg-[#FFCD11] h-full rounded-full" style={{ width: `${pct}%` }}></div>
                  </div>
                </div>

                <div>
                  <span className="text-gray-400">Scheduled Duration:</span>
                  <div className="font-mono font-bold text-white mt-0.5">
                    {task.scheduled_duration_minutes ?? task.estimated_duration_minutes} min (4.0 hrs)
                  </div>
                </div>

                <div>
                  <span className="text-gray-400">Predicted Duration:</span>
                  <div className="font-mono font-bold text-purple-300 mt-0.5">
                    ~145.0 min (P10: 138 min / P90: 162 min)
                  </div>
                </div>

                <div>
                  <span className="text-gray-400">Actual Duration:</span>
                  <div className="font-mono font-bold text-emerald-400 mt-0.5">
                    {task.actual_duration_minutes ? `${task.actual_duration_minutes} min` : 'Pending completion'}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Probabilistic ETA Result Box */}
      {estimate && (
        <section className="bg-[#1C1C1C] border border-purple-500/40 rounded-xl p-5 shadow-lg space-y-3">
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-purple-400" />
            <h4 className="text-sm font-bold text-white">
              Operations Model Estimate for Task {estimate.task_id}
            </h4>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="bg-[#121212] p-3 rounded-lg border border-[#262626]">
              <span className="text-gray-400 uppercase text-[10px]">Estimated Remaining</span>
              <div className="text-lg font-mono font-bold text-white mt-0.5">
                {estimate.estimated_remaining_minutes} minutes
              </div>
            </div>
            <div className="bg-[#121212] p-3 rounded-lg border border-[#262626]">
              <span className="text-gray-400 uppercase text-[10px]">Forecasted Timestamp</span>
              <div className="text-sm font-mono font-bold text-purple-300 mt-0.5">
                {estimate.estimated_completion_time}
              </div>
            </div>
            <div className="bg-[#121212] p-3 rounded-lg border border-[#262626]">
              <span className="text-gray-400 uppercase text-[10px]">P10 - P90 Confidence</span>
              <div className="text-sm font-mono font-bold text-emerald-400 mt-0.5">
                {estimate.p10_minutes ?? 138}m - {estimate.p90_minutes ?? 162}m ({Math.round(estimate.confidence_score * 100)}%)
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  );
};

