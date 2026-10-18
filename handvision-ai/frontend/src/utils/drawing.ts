import { HandDetection, VisualizationMode } from '../types/detection';

// MediaPipe 21 Hand Landmark connections
export const HAND_CONNECTIONS: [number, number][] = [
  // Thumb
  [0, 1], [1, 2], [2, 3], [3, 4],
  // Index finger
  [0, 5], [5, 6], [6, 7], [7, 8],
  // Middle finger
  [9, 10], [10, 11], [11, 12],
  // Ring finger
  [13, 14], [14, 15], [15, 16],
  // Pinky
  [0, 17], [17, 18], [18, 19], [19, 20],
  // Palm connections
  [5, 9], [9, 13], [13, 17]
];

// Color palette for distinct track IDs
const TRACK_COLORS = [
  { primary: '#00f2fe', secondary: '#4facfe', glow: 'rgba(0, 242, 254, 0.4)' }, // Cyan
  { primary: '#10b981', secondary: '#34d399', glow: 'rgba(16, 185, 129, 0.4)' }, // Emerald
  { primary: '#f59e0b', secondary: '#fbbf24', glow: 'rgba(245, 158, 11, 0.4)' }, // Amber
  { primary: '#ec4899', secondary: '#f472b6', glow: 'rgba(236, 72, 153, 0.4)' }, // Pink
  { primary: '#8b5cf6', secondary: '#a78bfa', glow: 'rgba(139, 92, 246, 0.4)' }, // Purple
];

function getTrackColor(trackId: number) {
  const index = Math.abs(trackId - 1) % TRACK_COLORS.length;
  return TRACK_COLORS[index];
}

/**
 * Clears canvas with optional slight fade for trail effects.
 */
export function clearCanvas(ctx: CanvasRenderingContext2D, width: number, height: number): void {
  ctx.clearRect(0, 0, width, height);
}

/**
 * Draws detection overlays on the provided canvas context.
 */
export function drawDetections(
  ctx: CanvasRenderingContext2D,
  hands: HandDetection[],
  mode: VisualizationMode,
  canvasWidth: number,
  canvasHeight: number,
  mirrored: boolean = false
): void {
  clearCanvas(ctx, canvasWidth, canvasHeight);

  if (!hands || hands.length === 0) {
    return;
  }

  // Coordinate mapper with optional horizontal flip
  const mapX = (normX: number) => {
    const clamped = Math.max(0, Math.min(1, normX));
    return (mirrored ? 1.0 - clamped : clamped) * canvasWidth;
  };
  const mapY = (normY: number) => {
    const clamped = Math.max(0, Math.min(1, normY));
    return clamped * canvasHeight;
  };

  switch (mode) {
    case 'skeleton':
      drawSkeletonOverlay(ctx, hands, mapX, mapY, canvasWidth, canvasHeight);
      break;
    case 'bounding_box':
      drawBoundingBoxOverlay(ctx, hands, canvasWidth, canvasHeight, mirrored);
      break;
    case 'heatmap':
      drawHeatmapOverlay(ctx, hands, mapX, mapY, canvasWidth, canvasHeight);
      break;
  }
}

function drawSkeletonOverlay(
  ctx: CanvasRenderingContext2D,
  hands: HandDetection[],
  mapX: (x: number) => number,
  mapY: (y: number) => number,
  canvasWidth: number,
  canvasHeight: number
): void {
  hands.forEach(hand => {
    const colors = getTrackColor(hand.track_id);
    const landmarks = hand.landmarks;

    if (!landmarks || landmarks.length < 21) return;

    // 1. Draw connections
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    HAND_CONNECTIONS.forEach(([i, j]) => {
      const p1 = landmarks[i];
      const p2 = landmarks[j];
      const x1 = mapX(p1.x);
      const y1 = mapY(p1.y);
      const x2 = mapX(p2.x);
      const y2 = mapY(p2.y);

      // Outer glow line
      ctx.strokeStyle = colors.glow;
      ctx.lineWidth = 6;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();

      // Sharp inner line
      ctx.strokeStyle = colors.primary;
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    });

    // 2. Draw landmark joints
    landmarks.forEach((lm, idx) => {
      const x = mapX(lm.x);
      const y = mapY(lm.y);
      const isTip = [4, 8, 12, 16, 20].includes(idx);
      const radius = isTip ? 5 : 3.5;

      // Glow circle
      ctx.fillStyle = colors.primary;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, 2 * Math.PI);
      ctx.fill();

      // Center bright pip
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(x, y, isTip ? 2.5 : 1.5, 0, 2 * Math.PI);
      ctx.fill();
    });

    // 3. Draw Track & Gesture label
    const wrist = landmarks[0];
    const labelX = Math.max(20, Math.min(canvasWidth - 140, mapX(wrist.x) - 40));
    const labelY = Math.max(30, Math.min(canvasHeight - 20, mapY(wrist.y) + 30));

    drawLabelPill(
      ctx,
      labelX,
      labelY,
      `ID ${hand.track_id} · ${hand.gesture}`,
      colors.primary,
      hand.handedness
    );
  });
}

function drawBoundingBoxOverlay(
  ctx: CanvasRenderingContext2D,
  hands: HandDetection[],
  canvasWidth: number,
  canvasHeight: number,
  mirrored: boolean
): void {
  hands.forEach(hand => {
    const colors = getTrackColor(hand.track_id);
    const box = hand.bounding_box;

    // Calculate canvas rect coords
    let rx = mirrored ? (1.0 - (box.x + box.width)) * canvasWidth : box.x * canvasWidth;
    let ry = box.y * canvasHeight;
    let rw = box.width * canvasWidth;
    let rh = box.height * canvasHeight;

    // Clamp inside canvas
    rx = Math.max(2, Math.min(canvasWidth - rw - 2, rx));
    ry = Math.max(2, Math.min(canvasHeight - rh - 2, ry));

    // Outer glow box
    ctx.strokeStyle = colors.glow;
    ctx.lineWidth = 4;
    ctx.strokeRect(rx, ry, rw, rh);

    // Primary border
    ctx.strokeStyle = colors.primary;
    ctx.lineWidth = 2;
    ctx.strokeRect(rx, ry, rw, rh);

    // Corner brackets for modern CV aesthetic
    const bracketLen = Math.min(18, Math.min(rw, rh) * 0.25);
    ctx.lineWidth = 3.5;
    ctx.strokeStyle = colors.primary;

    // Top-left
    ctx.beginPath();
    ctx.moveTo(rx, ry + bracketLen);
    ctx.lineTo(rx, ry);
    ctx.lineTo(rx + bracketLen, ry);
    ctx.stroke();

    // Top-right
    ctx.beginPath();
    ctx.moveTo(rx + rw - bracketLen, ry);
    ctx.lineTo(rx + rw, ry);
    ctx.lineTo(rx + rw, ry + bracketLen);
    ctx.stroke();

    // Bottom-left
    ctx.beginPath();
    ctx.moveTo(rx, ry + rh - bracketLen);
    ctx.lineTo(rx, ry + rh);
    ctx.lineTo(rx + bracketLen, ry + rh);
    ctx.stroke();

    // Bottom-right
    ctx.beginPath();
    ctx.moveTo(rx + rw - bracketLen, ry + rh);
    ctx.lineTo(rx + rw, ry + rh);
    ctx.lineTo(rx + rw, ry + rh - bracketLen);
    ctx.stroke();

    // Top label badge
    const labelY = ry > 32 ? ry - 8 : ry + rh + 22;
    drawLabelPill(
      ctx,
      rx,
      labelY,
      `ID ${hand.track_id} · ${hand.gesture}`,
      colors.primary,
      hand.handedness
    );
  });
}

function drawHeatmapOverlay(
  ctx: CanvasRenderingContext2D,
  hands: HandDetection[],
  mapX: (x: number) => number,
  mapY: (y: number) => number,
  canvasWidth: number,
  canvasHeight: number
): void {
  // Use additive 'screen' composition for glowing thermal look
  const prevComposite = ctx.globalCompositeOperation;
  ctx.globalCompositeOperation = 'screen';

  hands.forEach(hand => {
    const landmarks = hand.landmarks;
    if (!landmarks) return;

    landmarks.forEach((lm, idx) => {
      const x = mapX(lm.x);
      const y = mapY(lm.y);
      const isTip = [4, 8, 12, 16, 20].includes(idx);
      const radius = isTip ? 45 : 30;

      // Multi-stop radial gradient for thermal look
      const grad = ctx.createRadialGradient(x, y, 0, x, y, radius);
      grad.addColorStop(0.0, 'rgba(255, 60, 0, 0.85)');    // Red core
      grad.addColorStop(0.35, 'rgba(255, 210, 0, 0.65)');  // Yellow mid
      grad.addColorStop(0.70, 'rgba(0, 220, 255, 0.35)');  // Cyan outer
      grad.addColorStop(1.0, 'rgba(0, 50, 255, 0.0)');     // Blue fadeout

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, 2 * Math.PI);
      ctx.fill();
    });
  });

  ctx.globalCompositeOperation = prevComposite;

  // Draw minimal track identifier pills
  hands.forEach(hand => {
    const colors = getTrackColor(hand.track_id);
    if (hand.landmarks && hand.landmarks.length > 0) {
      const wrist = hand.landmarks[0];
      const lx = Math.max(10, Math.min(canvasWidth - 120, mapX(wrist.x)));
      const ly = Math.max(25, Math.min(canvasHeight - 20, mapY(wrist.y) + 25));
      drawLabelPill(ctx, lx, ly, `ID ${hand.track_id} · ${hand.gesture}`, colors.primary, hand.handedness);
    }
  });
}

function drawLabelPill(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  text: string,
  accentColor: string,
  handedness?: string | null
): void {
  const fullText = handedness ? `${text} (${handedness})` : text;
  ctx.font = '600 12px "JetBrains Mono", monospace';
  const textMetrics = ctx.measureText(fullText);
  const paddingX = 8;
  const pillW = textMetrics.width + paddingX * 2;
  const pillH = 22;

  // Background pill
  ctx.fillStyle = 'rgba(9, 13, 22, 0.85)';
  ctx.strokeStyle = accentColor;
  ctx.lineWidth = 1.2;

  ctx.beginPath();
  ctx.roundRect(x, y - pillH + 4, pillW, pillH, 5);
  ctx.fill();
  ctx.stroke();

  // Text
  ctx.fillStyle = '#f8fafc';
  ctx.fillText(fullText, x + paddingX, y - 2);
}
