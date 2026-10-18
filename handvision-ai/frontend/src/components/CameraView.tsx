import React, { useEffect, useRef } from 'react';
import { CameraStatus, HandDetection, VisualizationMode } from '../types/detection';
import { drawDetections, clearCanvas } from '../utils/drawing';
import { Camera, AlertTriangle, Eye, Video } from 'lucide-react';

interface CameraViewProps {
  videoRef: React.RefObject<HTMLVideoElement>;
  overlayCanvasRef: React.RefObject<HTMLCanvasElement>;
  cameraStatus: CameraStatus;
  cameraError: string | null;
  hands: HandDetection[];
  visualizationMode: VisualizationMode;
  isMirrored: boolean;
  isDetecting: boolean;
  isRecording: boolean;
  onStartCamera: () => void;
}

export const CameraView: React.FC<CameraViewProps> = ({
  videoRef,
  overlayCanvasRef,
  cameraStatus,
  cameraError,
  hands,
  visualizationMode,
  isMirrored,
  isDetecting,
  isRecording,
  onStartCamera,
}) => {
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Sync canvas dimensions with video feed and render overlays on detection updates
  useEffect(() => {
    const video = videoRef.current;
    const canvas = overlayCanvasRef.current;

    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (cameraStatus !== 'active' || !video) {
      clearCanvas(ctx, canvas.width, canvas.height);
      return;
    }

    const vw = video.videoWidth || 640;
    const vh = video.videoHeight || 480;

    if (canvas.width !== vw || canvas.height !== vh) {
      canvas.width = vw;
      canvas.height = vh;
    }

    if (isDetecting) {
      drawDetections(ctx, hands, visualizationMode, vw, vh, isMirrored);
    } else {
      clearCanvas(ctx, vw, vh);
    }
  }, [cameraStatus, hands, isDetecting, isMirrored, overlayCanvasRef, videoRef, visualizationMode]);

  return (
    <div
      ref={containerRef}
      className="relative w-full aspect-[4/3] max-h-[580px] bg-slate-950 rounded-2xl overflow-hidden border border-surface-border shadow-2xl flex items-center justify-center group"
    >
      {/* Video element */}
      <video
        ref={videoRef}
        playsInline
        muted
        autoPlay
        className={`w-full h-full object-contain ${isMirrored ? 'scale-x-[-1]' : ''} ${
          cameraStatus === 'active' ? 'block' : 'hidden'
        }`}
      />

      {/* HTML5 Canvas overlay for skeletons, boxes, heatmaps */}
      <canvas
        ref={overlayCanvasRef}
        className={`absolute inset-0 w-full h-full object-contain pointer-events-none ${
          cameraStatus === 'active' ? 'block' : 'hidden'
        }`}
      />

      {/* Standby / Inactive Overlay */}
      {cameraStatus !== 'active' && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-surface/90 backdrop-blur-sm p-6 text-center z-10">
          {cameraStatus === 'error' ? (
            <div className="flex flex-col items-center max-w-sm">
              <div className="w-14 h-14 rounded-full bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400 mb-3">
                <AlertTriangle className="w-7 h-7" />
              </div>
              <h3 className="text-base font-bold text-slate-100 mb-1">Camera Feed Unavailable</h3>
              <p className="text-xs text-rose-300 mb-4">{cameraError || 'Unable to access webcam.'}</p>
              <button
                onClick={onStartCamera}
                className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold shadow-md transition-colors"
              >
                Retry Access
              </button>
            </div>
          ) : (
            <div className="flex flex-col items-center max-w-sm">
              <div className="w-16 h-16 rounded-full bg-surface-raised border border-cyan-500/30 flex items-center justify-center text-cyan-400 mb-4 shadow-inner">
                <Video className="w-8 h-8" />
              </div>
              <h3 className="text-base font-bold text-slate-100 mb-1">Interactive Vision Feed Ready</h3>
              <p className="text-xs text-slate-400 mb-5 leading-relaxed">
                Connect your webcam to enable real-time hand detection, persistent tracking IDs, and geometric gesture recognition.
              </p>
              <button
                onClick={onStartCamera}
                className="flex items-center gap-2 px-5 py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs shadow-lg shadow-cyan-950/50 transition-all hover:scale-105"
              >
                <Camera className="w-4 h-4" />
                <span>Initialize Webcam</span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* Floating Status Badges inside the frame */}
      {cameraStatus === 'active' && (
        <>
          {/* Top-Left: Overlay Mode & Tracking Badge */}
          <div className="absolute top-3 left-3 flex items-center gap-2 z-20">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-900/80 backdrop-blur-md border border-slate-700/60 text-[11px] font-mono text-cyan-300 shadow">
              <Eye className="w-3.5 h-3.5 text-cyan-400" />
              <span className="capitalize">{visualizationMode.replace('_', ' ')} Mode</span>
            </div>
            {isDetecting && (
              <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-emerald-950/80 backdrop-blur-md border border-emerald-500/40 text-[11px] font-mono text-emerald-400 shadow">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>Inferring</span>
              </div>
            )}
          </div>

          {/* Top-Right: Recording Status Indicator */}
          {isRecording && (
            <div className="absolute top-3 right-3 flex items-center gap-1.5 px-3 py-1 rounded-md bg-rose-950/90 backdrop-blur-md border border-rose-500 text-rose-300 text-xs font-mono font-semibold animate-pulse z-20 shadow-lg shadow-rose-950">
              <span className="h-2 w-2 rounded-full bg-rose-500"></span>
              <span>REC (Composed Overlay)</span>
            </div>
          )}

          {/* Bottom Watermark */}
          <div className="absolute bottom-3 right-3 text-[10px] font-mono text-slate-400/70 select-none pointer-events-none px-2 py-0.5 rounded bg-slate-950/60 backdrop-blur-sm border border-slate-800">
            HANDVISION AI · 640×480
          </div>
        </>
      )}
    </div>
  );
};
