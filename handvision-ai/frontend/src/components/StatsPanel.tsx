import React from 'react';
import { BackendStats, CameraStatus, SocketStatus } from '../types/detection';
import { Activity, Clock, Cpu, Gauge, Radio, Layers } from 'lucide-react';

interface StatsPanelProps {
  stats: BackendStats;
  cameraStatus: CameraStatus;
  socketStatus: SocketStatus;
}

export const StatsPanel: React.FC<StatsPanelProps> = ({
  stats,
  cameraStatus,
  socketStatus,
}) => {
  return (
    <div className="bg-surface rounded-xl border border-surface-border p-4 flex flex-col gap-3 shadow-lg">
      <div className="flex items-center justify-between border-b border-surface-border/60 pb-2">
        <div className="flex items-center gap-2 text-slate-200 font-semibold text-sm">
          <Activity className="w-4 h-4 text-cyan-400" />
          <span>Real-Time Telemetry & Performance</span>
        </div>
        <div className="text-[11px] font-mono text-slate-400">
          Client FPS: <span className="text-cyan-400 font-bold">{stats.clientFps}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
        {/* Detected Hands */}
        <div className="bg-surface-raised p-2.5 rounded-lg border border-surface-border/60 flex flex-col">
          <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            <span>Hands Detected</span>
          </div>
          <div className="text-xl font-bold font-mono text-slate-100 mt-1">
            {stats.handsCount}
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            Max limit: 4
          </div>
        </div>

        {/* Backend Latency */}
        <div className="bg-surface-raised p-2.5 rounded-lg border border-surface-border/60 flex flex-col">
          <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            <span>Backend Inference</span>
          </div>
          <div className="text-xl font-bold font-mono text-slate-100 mt-1">
            {stats.backendMs.toFixed(1)} <span className="text-xs font-normal text-slate-400">ms</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            MediaPipe CPU
          </div>
        </div>

        {/* End-to-End Latency */}
        <div className="bg-surface-raised p-2.5 rounded-lg border border-surface-border/60 flex flex-col">
          <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
            <Clock className="w-3.5 h-3.5 text-amber-400" />
            <span>End-to-End Latency</span>
          </div>
          <div className="text-xl font-bold font-mono text-slate-100 mt-1">
            {stats.roundtripMs} <span className="text-xs font-normal text-slate-400">ms</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            Network + Decode + Model
          </div>
        </div>

        {/* Streaming Rate */}
        <div className="bg-surface-raised p-2.5 rounded-lg border border-surface-border/60 flex flex-col">
          <div className="flex items-center gap-1.5 text-slate-400 text-[11px]">
            <Gauge className="w-3.5 h-3.5 text-cyan-400" />
            <span>Frame Rate</span>
          </div>
          <div className="text-xl font-bold font-mono text-slate-100 mt-1">
            {stats.clientFps} <span className="text-xs font-normal text-slate-400">FPS</span>
          </div>
          <div className="text-[10px] text-slate-500 mt-0.5">
            WebSocket sync
          </div>
        </div>
      </div>

      {/* Active Track IDs & Gestures summary bar */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-xs">
        <div className="flex items-center gap-2">
          <span className="text-slate-400 font-mono text-[11px]">Active Track IDs:</span>
          {stats.activeTracks.length > 0 ? (
            <div className="flex items-center gap-1">
              {stats.activeTracks.map((id) => (
                <span
                  key={id}
                  className="px-2 py-0.5 rounded bg-cyan-950 border border-cyan-500/40 text-cyan-300 font-mono font-bold text-[11px]"
                >
                  #{id}
                </span>
              ))}
            </div>
          ) : (
            <span className="text-slate-500 italic text-[11px]">None</span>
          )}
        </div>

        <div className="flex items-center gap-1 text-[11px] text-slate-400">
          <Radio className={`w-3 h-3 ${socketStatus === 'connected' ? 'text-emerald-400 animate-pulse' : 'text-slate-600'}`} />
          <span>Status: {cameraStatus === 'active' ? 'Active stream' : 'Awaiting video'}</span>
        </div>
      </div>
    </div>
  );
};
