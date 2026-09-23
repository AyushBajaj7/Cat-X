import React from 'react';

export const CabFooter: React.FC = () => {
  return (
    <footer className="border-t border-[#262626] bg-[#141414] px-6 py-3 text-[11px] text-gray-500 mt-auto">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
        <div className="flex items-center space-x-2">
          <span className="font-bold text-gray-400">Caterpillar Hackathon 2026</span>
          <span>•</span>
          <span>CAT Operator Shift Twin & CAT Trajectory</span>
        </div>
        <div className="flex items-center space-x-4 font-mono text-gray-400">
          <span>Gateway: <strong className="text-emerald-400">:8080</strong></span>
          <span>Safety: <strong className="text-emerald-400">:8001</strong></span>
          <span>Operations: <strong className="text-emerald-400">:8002</strong></span>
          <span>Training: <strong className="text-emerald-400">:8003</strong></span>
        </div>
      </div>
    </footer>
  );
};

