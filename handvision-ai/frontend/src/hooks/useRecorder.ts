import { useState, useRef, useCallback, useEffect } from 'react';
import { getSupportedMimeType, downloadBlob } from '../utils/recording';

interface UseRecorderOptions {
  videoRef: React.RefObject<HTMLVideoElement>;
  overlayCanvasRef: React.RefObject<HTMLCanvasElement>;
}

export type RecordingState = 'idle' | 'recording' | 'recorded';

interface UseRecorderReturn {
  state: RecordingState;
  durationSeconds: number;
  recordedBlob: Blob | null;
  startRecording: () => boolean;
  stopRecording: () => void;
  downloadLatestRecording: () => void;
  error: string | null;
  isSupported: boolean;
}

export function useRecorder({ videoRef, overlayCanvasRef }: UseRecorderOptions): UseRecorderReturn {
  const [state, setState] = useState<RecordingState>('idle');
  const [durationSeconds, setDurationSeconds] = useState<number>(0);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const animationFrameRef = useRef<number | null>(null);
  const timerIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const compositionCanvasRef = useRef<HTMLCanvasElement | null>(null);

  const isSupported = typeof MediaRecorder !== 'undefined';

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && state === 'recording') {
      try {
        mediaRecorderRef.current.stop();
      } catch (e) {
        console.warn('Error stopping media recorder:', e);
      }
    }

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }
  }, [state]);

  const startRecording = useCallback((): boolean => {
    setError(null);
    setRecordedBlob(null);

    const video = videoRef.current;
    const overlay = overlayCanvasRef.current;

    if (!video || !overlay || video.readyState < 2) {
      setError('Cannot record: Video stream is not active.');
      return false;
    }

    const mimeType = getSupportedMimeType();
    if (!mimeType) {
      setError('MediaRecorder is not supported or no compatible MIME format found.');
      return false;
    }

    const width = video.videoWidth || 640;
    const height = video.videoHeight || 480;

    // Create composition canvas
    const compCanvas = document.createElement('canvas');
    compCanvas.width = width;
    compCanvas.height = height;
    compositionCanvasRef.current = compCanvas;
    const compCtx = compCanvas.getContext('2d');

    if (!compCtx) {
      setError('Failed to create canvas rendering context for video composition.');
      return false;
    }

    // Continuous composition render loop (merges video frame + overlay canvas)
    const renderComposition = () => {
      if (video && compCtx) {
        compCtx.drawImage(video, 0, 0, width, height);
        if (overlay) {
          compCtx.drawImage(overlay, 0, 0, width, height);
        }
      }
      animationFrameRef.current = requestAnimationFrame(renderComposition);
    };
    renderComposition();

    try {
      const stream = compCanvas.captureStream(30);
      const recorder = new MediaRecorder(stream, {
        mimeType,
        videoBitsPerSecond: 2500000,
      });

      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const fullBlob = new Blob(chunksRef.current, { type: mimeType });
        setRecordedBlob(fullBlob);
        setState('recorded');
      };

      recorder.onerror = (e) => {
        console.error('MediaRecorder error:', e);
        setError('An error occurred during video recording.');
        stopRecording();
      };

      recorder.start(100); // Record chunks every 100ms
      mediaRecorderRef.current = recorder;
      setState('recording');
      setDurationSeconds(0);

      const startTime = performance.now();
      timerIntervalRef.current = setInterval(() => {
        setDurationSeconds(Math.floor((performance.now() - startTime) / 1000));
      }, 1000);

      return true;
    } catch (err: unknown) {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
      setError(`Failed to initialize recorder: ${err instanceof Error ? err.message : String(err)}`);
      return false;
    }
  }, [overlayCanvasRef, stopRecording, videoRef]);

  const downloadLatestRecording = useCallback(() => {
    if (recordedBlob) {
      downloadBlob(recordedBlob);
    }
  }, [recordedBlob]);

  // Clean up timers on unmount
  useEffect(() => {
    return () => {
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
      if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
        try { mediaRecorderRef.current.stop(); } catch {}
      }
    };
  }, []);

  return {
    state,
    durationSeconds,
    recordedBlob,
    startRecording,
    stopRecording,
    downloadLatestRecording,
    error,
    isSupported
  };
}
