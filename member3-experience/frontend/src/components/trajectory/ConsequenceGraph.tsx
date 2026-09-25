import React from 'react';
import { ArrowRight, AlertCircle, CheckCircle2, AlertTriangle, ArrowDown } from 'lucide-react';
import { ConsequenceGraph as IConsequenceGraph, ConsequenceNode } from '../../types';

interface ConsequenceGraphProps {
  graph: IConsequenceGraph;
}

export const ConsequenceGraph: React.FC<ConsequenceGraphProps> = ({ graph }) => {
  const getNodeColor = (node: ConsequenceNode) => {
    switch (node.severity) {
      case 'BENEFICIAL':
        return 'border-emerald-500/70 bg-emerald-950/40 text-emerald-300';
      case 'WARNING':
        return 'border-amber-500/70 bg-amber-950/40 text-amber-300';
      case 'CRITICAL':
        return 'border-rose-500/70 bg-rose-950/40 text-rose-300';
      case 'NEUTRAL':
      default:
        return 'border-gray-600/70 bg-[#202020] text-gray-200';
    }
  };

  const getNodeIcon = (severity: string) => {
    switch (severity) {
      case 'BENEFICIAL':
        return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />;
      case 'WARNING':
        return <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />;
      case 'CRITICAL':
        return <AlertCircle className="w-3.5 h-3.5 text-rose-400" />;
      default:
        return null;
    }
  };

  return (
    <div className="bg-[#121212] rounded-xl border border-[#2B2B2B] p-5 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#222222] pb-3">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-[10px] font-black uppercase px-2 py-0.5 rounded bg-[#FFCD11]/20 text-[#FFCD11]">
              Operational Consequence Chain
            </span>
            <span className="text-xs text-gray-400 font-medium">Multi-Order Effects Modeling</span>
          </div>
          <p className="text-xs text-gray-400 mt-1">{graph.summary}</p>
        </div>
        <div className="text-[11px] text-gray-400 font-mono">
          Root: <span className="text-white font-bold">{graph.root_action}</span>
        </div>
      </div>

      {/* Visual Directed Graph Chain (Desktop: Horizontal Flow / Mobile: Vertical Flow) */}
      <div className="py-2">
        <div className="flex flex-col lg:flex-row items-stretch lg:items-center gap-3 overflow-x-auto pb-2">
          {graph.nodes?.map((node, index) => {
            const edge = graph.edges?.find((e) => e.source === node.node_id);
            return (
              <React.Fragment key={node.node_id}>
                {/* Graph Node */}
                <div
                  className={`flex-1 w-full lg:w-auto lg:min-w-[200px] lg:max-w-[260px] p-3.5 rounded-xl border shadow-sm transition hover:scale-[1.02] ${getNodeColor(
                    node
                  )}`}
                >
                  <div className="flex items-center justify-between text-[10px] uppercase font-bold text-gray-400 mb-1">
                    <span>{node.type.replace('_', ' ')}</span>
                    {getNodeIcon(node.severity)}
                  </div>
                  <div className="text-sm font-black text-white">{node.title}</div>
                  <div className="text-base font-black font-mono my-1 text-white">
                    {node.value} <span className="text-xs text-gray-400 font-normal">{node.unit}</span>
                  </div>
                  <div className="text-[11px] text-gray-300 leading-snug mt-1.5">{node.explanation}</div>
                </div>

                {/* Directed Edge / Arrow */}
                {index < graph.nodes.length - 1 && (
                  <div className="flex lg:flex-col items-center justify-center my-1 lg:my-0 text-[#FFCD11]">
                    <div className="hidden lg:flex items-center">
                      <ArrowRight className="w-5 h-5 animate-pulse" />
                    </div>
                    <div className="lg:hidden flex items-center">
                      <ArrowDown className="w-5 h-5 animate-pulse" />
                    </div>
                    {edge && (
                      <span className="text-[9px] uppercase font-mono font-bold tracking-wider text-gray-400 mt-0.5 ml-2 lg:ml-0">
                        {edge.relationship}
                      </span>
                    )}
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </div>
  );
};
