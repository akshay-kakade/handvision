/**
 * Utility functions for browser-based video recording composed from
 * the webcam feed and HTML5 detection overlay canvas.
 */

const PREFERRED_MIME_TYPES = [
  'video/webm;codecs=vp9',
  'video/webm;codecs=vp8',
  'video/webm',
  'video/mp4',
];

export function getSupportedMimeType(): string {
  if (typeof MediaRecorder === 'undefined') {
    return '';
  }
  for (const mimeType of PREFERRED_MIME_TYPES) {
    if (MediaRecorder.isTypeSupported(mimeType)) {
      return mimeType;
    }
  }
  return '';
}

export function downloadBlob(blob: Blob, filename?: string): void {
  const actualFilename = filename || `handvision-recording-${new Date().toISOString().replace(/[:.]/g, '-')}.webm`;
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.style.display = 'none';
  a.href = url;
  a.download = actualFilename;
  document.body.appendChild(a);
  a.click();

  // Cleanup object URL after a brief delay
  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 1000);
}
