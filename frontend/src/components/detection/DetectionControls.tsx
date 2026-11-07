// Right-hand control rail: camera on/off, the Record button and Snapshot.
//
// NOTE: components/ControlsPanel.tsx is an older, currently unused variant of
// this panel; it is left untouched.

import { Camera, Circle, Square } from "lucide-react";

interface DetectionControlsProps {
  isDetecting: boolean;
  isRecording: boolean;
  loading: boolean;
  onStartCamera: () => void;
  onStopCamera: () => void;
  onStartRecording: () => void;
  onStopRecording: () => void;
  onTakeSnapshot: () => void;
}

export default function DetectionControls({
  isDetecting,
  isRecording,
  loading,
  onStartCamera,
  onStopCamera,
  onStartRecording,
  onStopRecording,
  onTakeSnapshot,
}: DetectionControlsProps) {
  // Same handlers as before: turning off still goes through the
  // "stop for everyone?" confirmation.
  const cameraStatus = loading
    ? isDetecting
      ? "Stopping…"
      : "Starting…"
    : isDetecting
      ? "On"
      : "Off";

  return (
    <aside className="panel flex flex-col divide-y divide-line self-start">
      {/* Camera on/off */}
      <div className="flex items-center justify-between gap-4 p-4">
        <div>
          <p className="font-medium" id="camera-switch-label">
            Camera
          </p>
          <p className="text-sm text-silt">{cameraStatus}</p>
        </div>
        <button
          type="button"
          role="switch"
          aria-checked={isDetecting}
          aria-labelledby="camera-switch-label"
          onClick={isDetecting ? onStopCamera : onStartCamera}
          disabled={loading}
          className={`relative h-7 w-12 shrink-0 rounded-full border transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${
            isDetecting ? "border-kelp bg-kelp/25" : "border-line bg-deep"
          }`}
        >
          <span
            aria-hidden="true"
            className={`absolute top-1/2 size-5 -translate-y-1/2 rounded-full transition-[left] ${
              isDetecting
                ? "left-[calc(100%-1.375rem)] bg-kelp"
                : "left-0.5 bg-silt"
            }`}
          />
        </button>
      </div>

      {/* Recording: the one orange (or red, while recording) button */}
      <div className="space-y-3 p-4">
        <button
          type="button"
          onClick={isRecording ? onStopRecording : onStartRecording}
          className={`flex h-14 w-full items-center justify-center gap-2.5 rounded-md text-lg font-semibold text-deep transition-[filter] hover:brightness-110 ${
            isRecording ? "bg-signal" : "bg-buoy"
          }`}
        >
          {isRecording ? (
            <>
              <Square className="size-5 fill-current" />
              Stop recording
            </>
          ) : (
            <>
              <Circle className="size-5 fill-current" />
              Record
            </>
          )}
        </button>

        <button
          type="button"
          onClick={onTakeSnapshot}
          className="btn-secondary w-full"
        >
          <Camera className="size-5" />
          Take snapshot
        </button>

        <p className="text-sm text-silt">
          {isDetecting
            ? "Recordings include detection boxes and a detection log."
            : "Turn the camera on to record or take snapshots."}
        </p>
      </div>
    </aside>
  );
}
