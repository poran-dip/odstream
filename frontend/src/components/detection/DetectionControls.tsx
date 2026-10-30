// Right-hand sidebar: camera controls, recording controls and system status.
//
// NOTE: components/ControlsPanel.tsx is an older, currently unused variant of
// this panel (different button labels); it is left untouched.

import { Camera, Play, Square } from "lucide-react";
import type { CameraSource } from "../../utils/storage";

interface DetectionControlsProps {
  isDetecting: boolean;
  isRecording: boolean;
  loading: boolean;
  selectedSource: CameraSource;
  onStartCamera: () => void;
  onStopCamera: () => void;
  onStartRecording: () => void;
  onStopRecording: () => void;
  onTakeSnapshot: () => void;
}

const CARD =
  "bg-slate-800/30 backdrop-blur-sm border border-slate-600/30 rounded-2xl p-6";
const CARD_TITLE = "text-lg font-semibold mb-4 text-slate-200";

export default function DetectionControls({
  isDetecting,
  isRecording,
  loading,
  selectedSource,
  onStartCamera,
  onStopCamera,
  onStartRecording,
  onStopRecording,
  onTakeSnapshot,
}: DetectionControlsProps) {
  return (
    <div className="space-y-4">
      {/* Detection Controls */}
      <div className={CARD}>
        <h3 className={CARD_TITLE}>Detection Controls</h3>

        <div className="space-y-3">
          <button
            type="button"
            onClick={onStartCamera}
            disabled={loading || isDetecting}
            className="w-full bg-linear-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 hover:scale-105 disabled:hover:scale-100"
          >
            <Play className="w-5 h-5" />
            <span>{loading ? "Starting..." : "Start Camera"}</span>
          </button>

          <button
            type="button"
            onClick={onStopCamera}
            disabled={loading || !isDetecting}
            className="w-full bg-linear-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 hover:scale-105 disabled:hover:scale-100"
          >
            <Square className="w-5 h-5" />
            <span>{loading ? "Stopping..." : "Stop Camera"}</span>
          </button>
        </div>
      </div>

      {/* Recording Controls */}
      <div className={CARD}>
        <h3 className={CARD_TITLE}>Recording</h3>

        {/* Single toggle button: Start <-> Stop */}
        <button
          type="button"
          onClick={isRecording ? onStopRecording : onStartRecording}
          className={`w-full font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 hover:scale-105 mb-3 ${
            isRecording
              ? "bg-linear-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700"
              : "bg-linear-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700"
          }`}
        >
          {isRecording ? (
            <>
              <Square className="w-5 h-5" />
              <span>Stop Recording</span>
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              <span>Start Recording</span>
            </>
          )}
        </button>

        <button
          type="button"
          onClick={onTakeSnapshot}
          className="w-full font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 hover:scale-105 bg-linear-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700"
        >
          <Camera className="w-5 h-5" />
          <span>Take Snapshot</span>
        </button>
      </div>

      {/* Quick Stats */}
      <div className={CARD}>
        <h3 className={CARD_TITLE}>System Status</h3>

        <div className="space-y-3">
          <StatusRow
            label="Detection"
            value={isDetecting ? "Active" : "Inactive"}
            valueClass={isDetecting ? "text-green-400" : "text-slate-400"}
          />
          <StatusRow
            label="Recording"
            value={isRecording ? "Recording" : "Stopped"}
            valueClass={isRecording ? "text-red-400" : "text-slate-400"}
          />
          <StatusRow
            label="Source"
            value={selectedSource.name}
            valueClass="text-blue-400"
          />
        </div>
      </div>
    </div>
  );
}

/** "Label ........ Value" row in the System Status card. */
function StatusRow({
  label,
  value,
  valueClass,
}: {
  label: string;
  value: string;
  valueClass: string;
}) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-slate-400">{label}</span>
      <span className={`font-semibold ${valueClass}`}>{value}</span>
    </div>
  );
}
