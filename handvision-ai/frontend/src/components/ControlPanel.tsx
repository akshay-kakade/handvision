import React from 'react';
import { VisualizationMode, CameraStatus } from '../types/detection';
import { DetectionModeSelector } from './DetectionModeSelector';
import { RecordingState } from '../hooks/useRecorder';
import {
  Camera,
  VideoOff,
  Play,
  Square,
  Circle,
  Download,
  FlipHorizontal,
  Sliders,
  AlertCircle
} from 'lucide-react';

interface ControlPanelProps {
  cameraStatus: CameraStatus;
  isDetecting: boolean;
  visualizationMode: VisualizationMode;
  recordingState: RecordingState;
  recordingDuration: number;
  isMirrored: boolean;
  onToggleCamera: () => void;
  onToggleDetection: () => void;
  onModeChange: (mode: VisualizationMode) => void;
  onToggleRecording: () => void;
  onDownloadRecording: () => void;
  onToggleMirrored: () => void;
  errorMessage?: string | null;
}

export const ControlPanel: React.FC<ControlPanelProps> = ({
  cameraStatus,
  isDetecting,
  visualizationMode,
  recordingState,
  recordingDuration,
  isMirrored,
  onToggleCamera,
  onToggleDetection,
  onModeChange,
  onToggleRecording,
  onDownloadRecording,
  onToggleMirrored,
  errorMessage,
}) => {
  const isCameraActive = cameraStatus === 'active';
  const isRecording = recordingState === 'recording';
  const hasRecordingToDownload = recordingState === 'recorded';

  const formatSeconds = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const remainder = sec % 60;
    return `${mins.toString().padStart(2, '0')}:${remainder.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-surface rounded-xl border border-surface-border p-4 flex flex-col gap-4 shadow-lg">
      <div className="flex items-center justify-between border-b border-surface-border/60 pb-2">
        <div className="flex items-center gap-2 text-slate-200 font-semibold text-sm">
          <Sliders className="w-4 h-4 text-cyan-400" />
          <span>Workstation Controls</span>
        </div>
      </div>

      {errorMessage && (
        <div className="flex items-start gap-2 bg-rose-950/50 border border-rose-500/40 text-rose-300 p-2.5 rounded-lg text-xs">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Primary Actions: Camera & Detection */}
      <div className="grid grid-cols-2 gap-2.5">
        {/* Camera Toggle */}
        <button
          onClick={onToggleCamera}
          className={`flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-semibold text-xs transition-all shadow-md ${
            isCameraActive
              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40 hover:bg-rose-500/30'
              : 'bg-cyan-500 text-slate-950 hover:bg-cyan-400 font-bold'
          }`}
        >
          {isCameraActive ? (
            <>
              <VideoOff className="w-4 h-4" />
              <span>Stop Camera</span>
            </>
          ) : (
            <>
              <Camera className="w-4 h-4" />
              <span>Start Camera</span>
            </>
          )}
        </button>

        {/* Detection Toggle */}
        <button
          onClick={onToggleDetection}
          disabled={!isCameraActive}
          className={`flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-semibold text-xs transition-all border ${
            !isCameraActive
              ? 'bg-surface-raised text-slate-600 border-surface-border cursor-not-allowed'
              : isDetecting
              ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 hover:bg-amber-500/30'
              : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 hover:bg-emerald-500/30'
          }`}
        >
          {isDetecting ? (
            <>
              <Square className="w-4 h-4 fill-current" />
              <span>Pause Detection</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-current" />
              <span>Start Detection</span>
            </>
          )}
        </button>
      </div>

      {/* Visualization Mode Selector */}
      <DetectionModeSelector
        currentMode={visualizationMode}
        onModeChange={onModeChange}
      />

      {/* Recording Controls */}
      <div className="flex flex-col gap-2 pt-1">
        <label className="text-xs font-semibold uppercase tracking-wider text-slate-400">
          Video Session Recording
        </label>
        <div className="grid grid-cols-2 gap-2">
          {/* Start/Stop Recording */}
          <button
            onClick={onToggleRecording}
            disabled={!isCameraActive}
            className={`flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-medium border transition-all ${
              !isCameraActive
                ? 'bg-surface-raised text-slate-600 border-surface-border cursor-not-allowed'
                : isRecording
                ? 'bg-rose-600 text-white border-rose-500 animate-pulse'
                : 'bg-surface-raised text-slate-300 border-surface-border hover:border-slate-500 hover:text-white'
            }`}
          >
            <Circle className={`w-3.5 h-3.5 ${isRecording ? 'fill-white text-white' : 'text-rose-500 fill-rose-500'}`} />
            <span>{isRecording ? `Recording (${formatSeconds(recordingDuration)})` : 'Start Recording'}</span>
          </button>

          {/* Download Recording */}
          <button
            onClick={onDownloadRecording}
            disabled={!hasRecordingToDownload}
            className={`flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-xs font-medium border transition-all ${
              hasRecordingToDownload
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 hover:bg-cyan-500/30 shadow-sm shadow-cyan-950'
                : 'bg-surface-raised text-slate-600 border-surface-border cursor-not-allowed'
            }`}
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Video</span>
          </button>
        </div>
      </div>

      {/* Feed Settings */}
      <div className="pt-2 border-t border-surface-border/60 flex items-center justify-between">
        <span className="text-xs text-slate-400">Mirror Camera Feed</span>
        <button
          onClick={onToggleMirrored}
          className={`flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium transition-colors ${
            isMirrored
              ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
              : 'bg-surface-raised text-slate-400 hover:text-slate-200 border border-surface-border'
          }`}
        >
          <FlipHorizontal className="w-3.5 h-3.5" />
          <span>{isMirrored ? 'Mirrored (On)' : 'Normal (Off)'}</span>
        </button>
      </div>
    </div>
  );
};
