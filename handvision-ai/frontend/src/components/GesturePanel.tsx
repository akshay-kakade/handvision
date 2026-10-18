import React from 'react';
import { HandDetection } from '../types/detection';
import { Sparkles, Hand, HelpCircle } from 'lucide-react';

interface GesturePanelProps {
  hands: HandDetection[];
}

export const GesturePanel: React.FC<GesturePanelProps> = ({ hands }) => {
  const getGestureIcon = (gesture: string) => {
    switch (gesture) {
      case 'Thumbs Up':
        return '👍';
      case 'Peace Sign':
        return '✌️';
      case 'Open Palm':
        return '✋';
      case 'Fist':
        return '✊';
      case 'Pointing':
        return '☝️';
      case 'Three-Finger Gesture':
        return '🤟';
      default:
        return '❓';
    }
  };

  const getGestureColor = (gesture: string) => {
    switch (gesture) {
      case 'Thumbs Up':
        return 'text-emerald-400 border-emerald-500/30 bg-emerald-950/40';
      case 'Peace Sign':
        return 'text-cyan-400 border-cyan-500/30 bg-cyan-950/40';
      case 'Open Palm':
        return 'text-blue-400 border-blue-500/30 bg-blue-950/40';
      case 'Fist':
        return 'text-amber-400 border-amber-500/30 bg-amber-950/40';
      case 'Pointing':
        return 'text-purple-400 border-purple-500/30 bg-purple-950/40';
      case 'Three-Finger Gesture':
        return 'text-pink-400 border-pink-500/30 bg-pink-950/40';
      default:
        return 'text-slate-400 border-slate-700 bg-slate-800/40';
    }
  };

  return (
    <div className="bg-surface rounded-xl border border-surface-border p-4 flex flex-col gap-3 shadow-lg h-full">
      <div className="flex items-center justify-between border-b border-surface-border/60 pb-2">
        <div className="flex items-center gap-2 text-slate-200 font-semibold text-sm">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <span>Recognized Hand Gestures</span>
        </div>
        <span className="text-[11px] font-mono text-slate-400">
          {hands.length} {hands.length === 1 ? 'Hand' : 'Hands'} Active
        </span>
      </div>

      {hands.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-8 text-center text-slate-500">
          <Hand className="w-10 h-10 mb-2 stroke-[1.2] opacity-40 animate-pulse" />
          <p className="text-xs font-medium">No hands detected</p>
          <p className="text-[11px] text-slate-600 mt-0.5">Show hands to the camera feed</p>
        </div>
      ) : (
        <div className="flex flex-col gap-2.5 overflow-y-auto max-h-[360px] pr-1">
          {hands.map((hand) => {
            const badgeStyle = getGestureColor(hand.gesture);
            const icon = getGestureIcon(hand.gesture);

            return (
              <div
                key={hand.track_id}
                className="bg-surface-raised rounded-lg border border-surface-border p-3 flex flex-col gap-2 transition-all hover:border-cyan-500/30"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded text-xs font-bold font-mono bg-cyan-950 text-cyan-400 border border-cyan-500/40">
                      ID #{hand.track_id}
                    </span>
                    <span className="text-xs font-medium text-slate-300">
                      {hand.handedness || 'Hand'}
                    </span>
                  </div>
                  {hand.handedness_confidence !== null && (
                    <span className="text-[10px] font-mono text-slate-500">
                      {(hand.handedness_confidence * 100).toFixed(0)}% conf
                    </span>
                  )}
                </div>

                <div className={`flex items-center justify-between px-3 py-2 rounded-md border ${badgeStyle}`}>
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{icon}</span>
                    <span className="text-sm font-semibold tracking-wide">
                      {hand.gesture}
                    </span>
                  </div>
                  {hand.gesture_confidence !== null && (
                    <span className="text-[11px] font-mono font-semibold">
                      {(hand.gesture_confidence * 100).toFixed(0)}%
                    </span>
                  )}
                </div>

                <div className="flex items-center justify-between text-[10px] font-mono text-slate-500 px-1">
                  <span>
                    BBox: [{(hand.bounding_box.x * 100).toFixed(0)}%, {(hand.bounding_box.y * 100).toFixed(0)}%]
                  </span>
                  <span>
                    Size: {(hand.bounding_box.width * 100).toFixed(0)}% × {(hand.bounding_box.height * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Supported Gestures Reference Cheat Sheet */}
      <div className="mt-auto pt-3 border-t border-surface-border/60">
        <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1">
          <HelpCircle className="w-3.5 h-3.5" />
          <span>Supported Gestures</span>
        </div>
        <div className="grid grid-cols-3 gap-1.5 text-[11px] text-slate-300 font-medium">
          <div className="bg-surface-raised px-2 py-1 rounded border border-surface-border/50 flex items-center gap-1">
            <span>👍</span> Thumbs Up
          </div>
          <div className="bg-surface-raised px-2 py-1 rounded border border-surface-border/50 flex items-center gap-1">
            <span>✌️</span> Peace Sign
          </div>
          <div className="bg-surface-raised px-2 py-1 rounded border border-surface-border/50 flex items-center gap-1">
            <span>✋</span> Open Palm
          </div>
          <div className="bg-surface-raised px-2 py-1 rounded border border-surface-border/50 flex items-center gap-1">
            <span>✊</span> Fist
          </div>
          <div className="bg-surface-raised px-2 py-1 rounded border border-surface-border/50 flex items-center gap-1">
            <span>☝️</span> Pointing
          </div>
          <div className="bg-surface-raised px-2 py-1 rounded border border-surface-border/50 flex items-center gap-1">
            <span>🤟</span> 3-Fingers
          </div>
        </div>
      </div>
    </div>
  );
};
