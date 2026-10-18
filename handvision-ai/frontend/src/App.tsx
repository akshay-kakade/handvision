import React, { useState, useRef } from 'react';
import { useWebcam } from './hooks/useWebcam';
import { useDetectionSocket } from './hooks/useDetectionSocket';
import { useRecorder } from './hooks/useRecorder';
import { CameraView } from './components/CameraView';
import { StatsPanel } from './components/StatsPanel';
import { ControlPanel } from './components/ControlPanel';
import { GesturePanel } from './components/GesturePanel';
import { StatusIndicator } from './components/StatusIndicator';
import { VisualizationMode } from './types/detection';
import { ScanEye } from 'lucide-react';

export const App: React.FC = () => {
  const [visualizationMode, setVisualizationMode] = useState<VisualizationMode>('skeleton');
  const [isDetecting, setIsDetecting] = useState<boolean>(true);
  const [isMirrored, setIsMirrored] = useState<boolean>(true);

  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);

  // 1. Webcam hook
  const {
    videoRef,
    status: cameraStatus,
    error: cameraError,
    startCamera,
    stopCamera,
  } = useWebcam();

  // 2. WebSocket detection hook
  const {
    status: socketStatus,
    latestResult,
    stats,
    connect: reconnectSocket,
    error: socketError,
  } = useDetectionSocket({
    isDetecting: isDetecting && cameraStatus === 'active',
    videoRef,
    targetFps: 20
  });

  // 3. Composed canvas video recorder hook
  const {
    state: recordingState,
    durationSeconds: recordingDuration,
    startRecording,
    stopRecording,
    downloadLatestRecording,
    error: recordingError,
  } = useRecorder({
    videoRef,
    overlayCanvasRef,
  });

  const handleToggleCamera = () => {
    if (cameraStatus === 'active') {
      if (recordingState === 'recording') stopRecording();
      stopCamera();
    } else {
      startCamera();
    }
  };

  const handleToggleDetection = () => {
    setIsDetecting(prev => !prev);
  };

  const handleToggleRecording = () => {
    if (recordingState === 'recording') {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const activeHands = latestResult?.hands || [];
  const combinedError = cameraError || socketError || recordingError;

  return (
    <div className="min-h-screen bg-background text-slate-100 flex flex-col">
      {/* Top Navigation Bar */}
      <header className="border-b border-surface-border bg-surface/80 backdrop-blur-md sticky top-0 z-50 px-4 lg:px-8 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-slate-950 shadow-md shadow-cyan-950/40">
              <ScanEye className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-sm font-bold tracking-tight text-white font-mono">
                  HANDVISION<span className="text-cyan-400">.AI</span>
                </h1>
                <span className="text-[10px] uppercase font-mono px-1.5 py-0.5 rounded bg-surface-raised border border-surface-border text-slate-400">
                  v1.0-prod
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                Real-Time Hand Detection, Tracking & Gesture Recognition
              </p>
            </div>
          </div>

          <StatusIndicator
            socketStatus={socketStatus}
            cameraStatus={cameraStatus}
            onReconnect={reconnectSocket}
          />
        </div>
      </header>

      {/* Main Computer Vision Workstation Grid */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Video Feed & Telemetry (7/12 on large screens) */}
          <section className="lg:col-span-7 flex flex-col gap-5">
            <CameraView
              videoRef={videoRef}
              overlayCanvasRef={overlayCanvasRef}
              cameraStatus={cameraStatus}
              cameraError={cameraError}
              hands={activeHands}
              visualizationMode={visualizationMode}
              isMirrored={isMirrored}
              isDetecting={isDetecting}
              isRecording={recordingState === 'recording'}
              onStartCamera={startCamera}
            />

            <StatsPanel
              stats={stats}
              cameraStatus={cameraStatus}
              socketStatus={socketStatus}
            />
          </section>

          {/* Right Column: Workstation Controls & Gesture Cards (5/12 on large screens) */}
          <section className="lg:col-span-5 flex flex-col gap-5">
            <ControlPanel
              cameraStatus={cameraStatus}
              isDetecting={isDetecting}
              visualizationMode={visualizationMode}
              recordingState={recordingState}
              recordingDuration={recordingDuration}
              isMirrored={isMirrored}
              onToggleCamera={handleToggleCamera}
              onToggleDetection={handleToggleDetection}
              onModeChange={setVisualizationMode}
              onToggleRecording={handleToggleRecording}
              onDownloadRecording={downloadLatestRecording}
              onToggleMirrored={() => setIsMirrored(prev => !prev)}
              errorMessage={combinedError}
            />

            <GesturePanel hands={activeHands} />
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-surface-border/60 bg-surface/50 text-[11px] text-slate-500 py-3 px-4 lg:px-8">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>HandVision AI · Computer Vision Assessment Submission for Dheera AI</span>
          <span className="font-mono">MediaPipe Hand Landmarker · OpenCV · FastAPI · React TypeScript</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
