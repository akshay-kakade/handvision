import { useState, useEffect, useRef, useCallback } from 'react';
import { DetectionResult, SocketStatus, BackendStats } from '../types/detection';

interface UseDetectionSocketOptions {
  wsUrl?: string;
  targetFps?: number;
  isDetecting: boolean;
  videoRef: React.RefObject<HTMLVideoElement>;
}

interface UseDetectionSocketReturn {
  status: SocketStatus;
  latestResult: DetectionResult | null;
  stats: BackendStats;
  connect: () => void;
  disconnect: () => void;
  error: string | null;
}

export function useDetectionSocket({
  wsUrl,
  targetFps = 20,
  isDetecting,
  videoRef,
}: UseDetectionSocketOptions): UseDetectionSocketReturn {
  const [status, setStatus] = useState<SocketStatus>('disconnected');
  const [latestResult, setLatestResult] = useState<DetectionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const isWaitingForResponseRef = useRef<boolean>(false);
  const sendTimestampRef = useRef<number>(0);
  const frameCountRef = useRef<number>(0);
  const lastFpsUpdateRef = useRef<number>(performance.now());
  const canvasCaptureRef = useRef<HTMLCanvasElement | null>(null);

  const [stats, setStats] = useState<BackendStats>({
    backendMs: 0,
    roundtripMs: 0,
    clientFps: 0,
    handsCount: 0,
    activeTracks: [],
    recognizedGestures: []
  });

  const getResolvedWsUrl = useCallback(() => {
    if (wsUrl) return wsUrl;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname || 'localhost';
    const port = import.meta.env.VITE_BACKEND_PORT || '8000';
    return `${protocol}//${host}:${port}/ws/detect`;
  }, [wsUrl]);

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
    setStatus('disconnected');
    isWaitingForResponseRef.current = false;
  }, []);

  const connect = useCallback(() => {
    disconnect();
    const url = getResolvedWsUrl();
    setStatus('connecting');
    setError(null);

    try {
      const ws = new WebSocket(url);
      ws.binaryType = 'arraybuffer';

      ws.onopen = () => {
        setStatus('connected');
        setError(null);
      };

      ws.onmessage = (event) => {
        try {
          const data: DetectionResult = JSON.parse(event.data);
          if (data.type === 'detection_result') {
            const now = performance.now();
            const rtt = sendTimestampRef.current > 0 ? Math.round(now - sendTimestampRef.current) : 0;
            
            setLatestResult(data);
            frameCountRef.current += 1;

            // Update stats
            const activeTracks = data.hands.map(h => h.track_id);
            const recognizedGestures = data.hands.map(h => h.gesture);

            // FPS calculation every 500ms
            if (now - lastFpsUpdateRef.current >= 500) {
              const seconds = (now - lastFpsUpdateRef.current) / 1000;
              const calculatedFps = Math.round(frameCountRef.current / seconds);
              frameCountRef.current = 0;
              lastFpsUpdateRef.current = now;

              setStats({
                backendMs: data.processing_ms,
                roundtripMs: rtt,
                clientFps: calculatedFps,
                handsCount: data.hands_detected,
                activeTracks,
                recognizedGestures
              });
            } else {
              setStats(prev => ({
                ...prev,
                backendMs: data.processing_ms,
                roundtripMs: rtt,
                handsCount: data.hands_detected,
                activeTracks,
                recognizedGestures
              }));
            }
          }
        } catch (e) {
          console.warn('Failed to parse detection message:', e);
        } finally {
          isWaitingForResponseRef.current = false;
        }
      };

      ws.onerror = (e) => {
        console.error('WebSocket connection error:', e);
        setStatus('error');
        setError('Cannot establish connection to backend WebSocket server.');
        isWaitingForResponseRef.current = false;
      };

      ws.onclose = () => {
        setStatus('disconnected');
        isWaitingForResponseRef.current = false;
      };

      socketRef.current = ws;
    } catch (err: unknown) {
      setStatus('error');
      setError(`Failed to connect: ${err instanceof Error ? err.message : String(err)}`);
    }
  }, [disconnect, getResolvedWsUrl]);

  // Frame capture and transmission loop
  useEffect(() => {
    if (!isDetecting || status !== 'connected') {
      return;
    }

    const intervalMs = Math.round(1000 / targetFps);

    // Initialize offscreen capture canvas
    if (!canvasCaptureRef.current) {
      canvasCaptureRef.current = document.createElement('canvas');
    }
    const canvas = canvasCaptureRef.current;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });

    const timer = setInterval(() => {
      const video = videoRef.current;
      const ws = socketRef.current;

      if (!video || !ws || ws.readyState !== WebSocket.OPEN) {
        return;
      }

      if (video.readyState < 2 || video.paused || video.ended) {
        return;
      }

      // Avoid frame backlog: drop frame if previous one is still in-flight
      if (isWaitingForResponseRef.current) {
        return;
      }

      const vw = video.videoWidth || 640;
      const vh = video.videoHeight || 480;

      // Downsample to max 640x480 for fast network transfer
      const scale = Math.min(1.0, 640 / vw, 480 / vh);
      const targetW = Math.round(vw * scale);
      const targetH = Math.round(vh * scale);

      if (canvas.width !== targetW || canvas.height !== targetH) {
        canvas.width = targetW;
        canvas.height = targetH;
      }

      if (ctx) {
        ctx.drawImage(video, 0, 0, targetW, targetH);
        canvas.toBlob(
          (blob) => {
            if (blob && ws.readyState === WebSocket.OPEN) {
              isWaitingForResponseRef.current = true;
              sendTimestampRef.current = performance.now();
              blob.arrayBuffer().then(buffer => {
                ws.send(buffer);
              }).catch(() => {
                isWaitingForResponseRef.current = false;
              });
            }
          },
          'image/jpeg',
          0.75
        );
      }
    }, intervalMs);

    return () => {
      clearInterval(timer);
    };
  }, [isDetecting, status, targetFps, videoRef]);

  // Automatically connect on mount and cleanup on unmount
  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    status,
    latestResult,
    stats,
    connect,
    disconnect,
    error
  };
}
