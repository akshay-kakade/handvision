import React from 'react';
import { SocketStatus, CameraStatus } from '../types/detection';
import { Wifi, WifiOff, Camera, VideoOff, RefreshCw } from 'lucide-react';

interface StatusIndicatorProps {
  socketStatus: SocketStatus;
  cameraStatus: CameraStatus;
  onReconnect?: () => void;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  socketStatus,
  cameraStatus,
  onReconnect,
}) => {
  const getSocketBadge = () => {
    switch (socketStatus) {
      case 'connected':
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-950/60 border border-emerald-500/40 text-emerald-400">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <Wifi className="w-3.5 h-3.5" />
            <span>Backend Connected</span>
          </div>
        );
      case 'connecting':
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-950/60 border border-amber-500/40 text-amber-400">
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            <span>Connecting...</span>
          </div>
        );
      case 'error':
      case 'disconnected':
      default:
        return (
          <div
            onClick={onReconnect}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-rose-950/60 border border-rose-500/40 text-rose-400 cursor-pointer hover:bg-rose-900/60 transition-colors"
            title="Click to reconnect"
          >
            <WifiOff className="w-3.5 h-3.5" />
            <span>Backend Offline</span>
          </div>
        );
    }
  };

  const getCameraBadge = () => {
    switch (cameraStatus) {
      case 'active':
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-cyan-950/60 border border-cyan-500/40 text-cyan-400">
            <span className="h-2 w-2 rounded-full bg-cyan-400"></span>
            <Camera className="w-3.5 h-3.5" />
            <span>Camera Active</span>
          </div>
        );
      case 'requesting':
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-950/60 border border-amber-500/40 text-amber-400">
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            <span>Opening Camera...</span>
          </div>
        );
      case 'error':
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-rose-950/60 border border-rose-500/40 text-rose-400">
            <VideoOff className="w-3.5 h-3.5" />
            <span>Camera Error</span>
          </div>
        );
      case 'idle':
      default:
        return (
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800/80 border border-slate-700 text-slate-400">
            <VideoOff className="w-3.5 h-3.5" />
            <span>Camera Standby</span>
          </div>
        );
    }
  };

  return (
    <div className="flex items-center gap-2">
      {getSocketBadge()}
      {getCameraBadge()}
    </div>
  );
};
