import React, { useState } from 'react';
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
  HelpCircle,
  Truck,
} from 'lucide-react';
import { AttentionMode } from '../../types';
import { OperatorGuideModal } from './OperatorGuideModal';

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
  const [isGuideOpen, setIsGuideOpen] = useState(false);

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
    { to: '/shift', label: 'Shift Cockpit', title: 'Shift Cockpit (All-in-One In-Cab HUD)', icon: <Activity className="w-3.5 h-3.5" /> },
    { to: '/trajectory', label: 'Trajectory DAG', title: 'CAT Trajectory & Consequence DAG', icon: <Compass className="w-3.5 h-3.5 text-[#FFCD11]" />, highlight: true },
    { to: '/what-if', label: 'What-If', title: 'What-If Operational Simulator', icon: <Sliders className="w-3.5 h-3.5" /> },
    { to: '/decisions', label: 'Decisions', title: 'Historical Decision Memory & Precedents', icon: <Compass className="w-3.5 h-3.5" /> },
    { to: '/tasks', label: 'Tasks', title: 'Operator Shift Tasks & Production Tonnage', icon: <CheckSquare className="w-3.5 h-3.5" /> },
    { to: '/safety', label: 'Safety', title: 'Real-Time Safety Audit & Perimeter Zones', icon: <Shield className="w-3.5 h-3.5" /> },
    { to: '/machine', label: 'Machine', title: 'Machine Telematics & Hydraulic Pressures', icon: <Cpu className="w-3.5 h-3.5" /> },
    { to: '/insights', label: 'Twin State', title: 'Digital Twin Context & Attention Modes', icon: <Brain className="w-3.5 h-3.5" /> },
    { to: '/training', label: 'Training Hub', title: 'Operator Training Hub & Micro-Learning', icon: <BookOpen className="w-3.5 h-3.5" /> },
  ];

  return (
    <>
      <OperatorGuideModal isOpen={isGuideOpen} onClose={() => setIsGuideOpen(false)} />
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
              <div className="flex flex-wrap items-center gap-x-2.5 gap-y-1 text-xs text-gray-400 mt-0.5">
                <span>Op: <strong className="text-white font-mono">{operatorId} (J. Miller)</strong></span>
                <span>•</span>
                <span>Cab Unit: <strong className="text-[#FFCD11] font-mono">{machineId}</strong> <span className="text-[10px] text-gray-400">(Single Machine)</span></span>
                <span className="hidden sm:inline">•</span>
                <span className="hidden sm:inline text-gray-400">
                  <Truck className="w-3 h-3 inline mr-1 text-sky-400" />
                  Fleet Radar: 4 Trucks active
                </span>
                <span>•</span>
                <span className="flex items-center text-emerald-400 font-medium">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse mr-1"></span>
                  Twin Synced
                </span>
              </div>
            </div>
          </div>

          {/* Right: Adaptive Attention Mode Indicator & Guide button */}
          <div className="flex items-center justify-between sm:justify-end gap-2 w-full md:w-auto">
            <button
              type="button"
              onClick={() => setIsGuideOpen(true)}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#252525] hover:bg-[#333333] hover:text-white text-gray-200 border border-[#3A3A3A] text-xs font-bold transition shadow-sm cursor-pointer"
              title="Click to open the System Guide (explaining machine tracking, workflow, and operator controls)"
            >
              <HelpCircle className="w-4 h-4 text-[#FFCD11]" />
              <span>How It Works</span>
            </button>
            <div
              className={`flex items-center px-3 py-1.5 rounded-lg border text-xs font-bold ${badge.bg}`}
              title={attentionReason}
            >
              {badge.icon}
              <span>{badge.label}</span>
            </div>
          </div>
        </div>

        {/* Navigation Bar - Single-line horizontal scroll on small screens, flex-spaced on larger screens */}
        <div className="border-t border-[#242424] bg-[#1A1A1A] px-2 sm:px-4 py-1.5">
          <nav className="max-w-7xl mx-auto flex items-center gap-1.5 overflow-x-auto no-scrollbar py-0.5 text-xs xl:justify-between">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                title={item.title}
                className={({ isActive }: { isActive: boolean }) =>
                  `flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg font-bold transition whitespace-nowrap text-xs shrink-0 ${
                    isActive
                      ? 'bg-[#FFCD11] text-[#111111] shadow-md font-black'
                      : item.highlight
                      ? 'text-[#FFCD11] hover:bg-[#282828] bg-[#221C06]/40 border border-[#FFCD11]/30'
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
    </>
  );
};

