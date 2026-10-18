import React from 'react';
import { VisualizationMode } from '../types/detection';
import { GitBranch, Box, Flame } from 'lucide-react';

interface DetectionModeSelectorProps {
  currentMode: VisualizationMode;
  onModeChange: (mode: VisualizationMode) => void;
}

export const DetectionModeSelector: React.FC<DetectionModeSelectorProps> = ({
  currentMode,
  onModeChange,
}) => {
  const modes: { id: VisualizationMode; label: string; icon: React.ReactNode; desc: string }[] = [
    {
      id: 'skeleton',
      label: 'Skeleton',
      icon: <GitBranch className="w-4 h-4" />,
      desc: '21 joint landmarks & bone connections'
    },
    {
      id: 'bounding_box',
      label: 'Bounding Box',
      icon: <Box className="w-4 h-4" />,
      desc: 'Enclosing boundary & tracking tags'
    },
    {
      id: 'heatmap',
      label: 'Heatmap',
      icon: <Flame className="w-4 h-4" />,
      desc: 'Landmark spatial intensity density'
    }
  ];

  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
        Visualization Overlay Mode
      </label>
      <div className="grid grid-cols-3 gap-2 bg-surface p-1.5 rounded-lg border border-surface-border">
        {modes.map((mode) => {
          const isActive = currentMode === mode.id;
          return (
            <button
              key={mode.id}
              onClick={() => onModeChange(mode.id)}
              className={`flex items-center justify-center gap-2 px-3 py-2 rounded-md text-xs font-medium transition-all ${
                isActive
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-950'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-surface-raised border border-transparent'
              }`}
              title={mode.desc}
            >
              {mode.icon}
              <span>{mode.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
