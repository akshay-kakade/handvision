export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Landmark {
  x: number;
  y: number;
  z: number;
}

export interface HandDetection {
  track_id: number;
  handedness: 'Left' | 'Right' | string | null;
  handedness_confidence: number | null;
  gesture: string;
  gesture_confidence: number | null;
  bounding_box: BoundingBox;
  landmarks: Landmark[];
}

export interface DetectionResult {
  type: 'detection_result';
  timestamp: number;
  processing_ms: number;
  frame_width: number;
  frame_height: number;
  hands_detected: number;
  hands: HandDetection[];
}

export type VisualizationMode = 'skeleton' | 'bounding_box' | 'heatmap';

export type SocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export type CameraStatus = 'idle' | 'requesting' | 'active' | 'error';

export interface BackendStats {
  backendMs: number;
  roundtripMs: number;
  clientFps: number;
  handsCount: number;
  activeTracks: number[];
  recognizedGestures: string[];
}
