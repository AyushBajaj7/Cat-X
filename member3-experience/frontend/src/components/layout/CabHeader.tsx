import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Shield,
  Compass,
  CheckSquare,
  Activity,
  Cpu,
  BookOpen,
  Brain,
  Sliders,
  AlertTriangle,
} from 'lucide-react';
import { AttentionMode } from '../../types';

interface CabHeaderProps {
  attentionMode?: AttentionMode;
  attentionReason?: string;
  operatorId?: string;
  machineId?: string;
}

export const CabHeader: React.FC<CabHeaderProps> = ({
  attentionMode = 'NORMAL',
  attentionReason = 'Nominal operating parameters.',
  operatorId = 'OP1001',
  machineId = 'EXC-CAT-349D',
}) => {
  const getAttentionBadge = (mode: AttentionMode) => {
    switch (mode) {
      case 'SAFETY_FOCUS':
        return {
          bg: 'bg-rose-950/80 border-rose-500 text-rose-300 animate-pulse',
          label: 'SAFETY FOCUS',
          icon: <AlertTriangle className="w-3.5 h-3.5 mr-1 text-rose-400" />,
        };
      case 'DECISION_FOCUS':
        return {
          bg: 'bg-amber-950/80 border-[#FFCD11] text-[#FFCD11] animate-pulse',
          label: 'DECISION FOCUS',
          icon: <Compass className="w-3.5 h-3.5 mr-1 text-[#FFCD11]" />,
        };
      case 'EFFICIENCY_FOCUS':
        return {
          bg: 'bg-emerald-950/80 border-emerald-500 text-emerald-300',
          label: 'EFFICIENCY FOCUS',
          icon: <Activity className="w-3.5 h-3.5 mr-1 text-emerald-400" />,
        };
      case 'PLANNING_FOCUS':
        return {
          bg: 'bg-sky-950/80 border-sky-500 text-sky-300',
          label: 'PLANNING FOCUS',
          icon: <Sliders className="w-3.5 h-3.5 mr-1 text-sky-400" />,
        };
      case 'TRAINING_FOCUS':
        return {
          bg: 'bg-purple-950/80 border-purple-500 text-purple-300',
          label: 'TRAINING FOCUS',
          icon: <BookOpen className="w-3.5 h-3.5 mr-1 text-purple-400" />,
        };
      case 'NORMAL':
      default:
        return {
          bg: 'bg-[#222222] border-[#3E3E3E] text-gray-300',
          label: 'BALANCED COCKPIT',
          icon: <Activity className="w-3.5 h-3.5 mr-1 text-emerald-400" />,
        };
    }
  };

  const badge = getAttentionBadge(attentionMode);

  const navItems = [
    { to: '/shift', label: 'Shift Cockpit', icon: <Activity className="w-4 h-4" /> },
    { to: '/trajectory', label: 'CAT Trajectory', icon: <Compass className="w-4 h-4 text-[#FFCD11]" />, highlight: true },
    { to: '/tasks', label: 'Tasks', icon: <CheckSquare className="w-4 h-4" /> },
    { to: '/safety', label: 'Safety', icon: <Shield className="w-4 h-4" /> },
    { to: '/machine', label: 'Machine', icon: <Cpu className="w-4 h-4" /> },
    { to: '/insights', label: 'Shift Twin', icon: <Brain className="w-4 h-4" /> },
    { to: '/decisions', label: 'Decision Memory', icon: <Compass className="w-4 h-4" /> },
    { to: '/what-if', label: 'What-If', icon: <Sliders className="w-4 h-4" /> },
    { to: '/training', label: 'Training Hub', icon: <BookOpen className="w-4 h-4" /> },
  ];

  return (
    <header className="border-b border-[#2D2D2D] bg-[#161616] sticky top-0 z-40 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-3 flex flex-col md:flex-row md:items-center justify-between gap-3">
        {/* Left: Brand & Machine Details */}
        <div className="flex items-center space-x-4">
          <div className="bg-[#FFCD11] text-[#111111] font-black px-3 py-1 text-base tracking-wider uppercase rounded shadow-sm">
            CAT
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-black tracking-tight text-white uppercase">
                Operator Shift Twin
              </h1>
              <span className="text-[10px] px-2 py-0.5 rounded bg-[#2D2D2D] text-[#FFCD11] font-bold uppercase tracking-wider">
                Cab Companion
              </span>
            </div>
            <div className="flex items-center space-x-3 text-xs text-gray-400 mt-0.5">
              <span>Op: <strong className="text-white font-mono">{operatorId} (J. Miller)</strong></span>
              <span>•</span>
              <span>Machine: <strong className="text-[#FFCD11] font-mono">{machineId}</strong></span>
              <span>•</span>
              <span className="flex items-center text-emerald-400 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse mr-1"></span>
                Twin Synced
              </span>
            </div>
          </div>
        </div>

        {/* Right: Adaptive Attention Mode Indicator */}
        <div className="flex items-center space-x-3">
          <div
            className={`flex items-center px-3 py-1.5 rounded-lg border text-xs font-bold ${badge.bg}`}
            title={attentionReason}
          >
            {badge.icon}
            <span>{badge.label}</span>
          </div>
        </div>
      </div>

      {/* Navigation Bar */}
      <div className="border-t border-[#242424] bg-[#1A1A1A] px-4">
        <nav className="max-w-7xl mx-auto flex items-center space-x-1 overflow-x-auto py-1 text-xs">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center space-x-1.5 px-3 py-2 rounded-md font-bold transition whitespace-nowrap ${
                  isActive
                    ? 'bg-[#FFCD11] text-[#111111] shadow'
                    : item.highlight
                    ? 'text-[#FFCD11] hover:bg-[#282828]'
                    : 'text-gray-300 hover:text-white hover:bg-[#252525]'
                }`
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
};

