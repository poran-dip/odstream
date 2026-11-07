// Live video panel: MJPEG <img>, live/recording pills and the readout strip
// (FPS, latency, objects, elapsed) attached to its bottom edge.

import type { RefObject } from "react";
import { formatElapsedTime } from "../../utils/formatters";
import VideoContainer from "../VideoContainer";

interface DetectionVideoProps {
  isDetecting: boolean;
  isRecording: boolean;
  detectionStartTime: number;
  /** Live metrics from the backend's "perf_update" event */
  currentFps: number;
  latencyMs: number | null;
  detectionCount: number;
  /** The MJPEG stream is attached to this <img> by useDetectionSocket */
  imgRef: RefObject<HTMLImageElement | null>;
}

export default function DetectionVideo({
  isDetecting,
  isRecording,
  detectionStartTime,
  currentFps,
  latencyMs,
  detectionCount,
  imgRef,
}: DetectionVideoProps) {
  // "—" until the camera is on and the first perf_update has arrived
  const readouts = [
    {
      label: "frames per second",
      value: isDetecting && currentFps > 0 ? currentFps.toFixed(1) : "—",
    },
    {
      label: "ms pipeline latency",
      value: isDetecting && latencyMs !== null ? latencyMs.toFixed(1) : "—",
    },
    {
      label: "objects in view",
      value: isDetecting ? String(detectionCount) : "—",
    },
    {
      label: "elapsed",
      value: isDetecting ? formatElapsedTime(detectionStartTime) : "—",
    },
  ];

  return (
    <VideoContainer
      showPlaceholder={!isDetecting}
      placeholderTitle="Camera is off"
      placeholderDescription="Turn the camera on to start the live feed. Detection runs while you record."
      statusIndicators={
        <>
          {isDetecting && <StatusPill dotClass="bg-kelp">Live</StatusPill>}
          {isRecording && (
            <StatusPill dotClass="bg-signal motion-safe:animate-pulse">
              Recording
            </StatusPill>
          )}
        </>
      }
      bottomContent={
        <dl className="grid grid-cols-2 sm:grid-cols-4">
          {readouts.map(({ label, value }) => (
            <div
              key={label}
              className="border-line px-4 py-3 not-first:border-l max-sm:nth-3:border-l-0 max-sm:nth-[n+3]:border-t"
            >
              {/* Condensed Archivo with fixed-width digits so values don't jitter */}
              <dd
                className={`font-stretch-75% text-3xl font-semibold leading-none tabular-nums sm:text-4xl ${
                  value === "—" ? "text-silt" : "text-foam"
                }`}
              >
                {value}
              </dd>
              <dt className="mt-1.5 text-sm text-silt">{label}</dt>
            </div>
          ))}
        </dl>
      }
    >
      <img
        ref={imgRef}
        alt="Live camera feed"
        className="h-full w-full object-contain"
      />
    </VideoContainer>
  );
}

/** Small pill over the video, e.g. "● Live". */
function StatusPill({
  dotClass,
  children,
}: {
  dotClass: string;
  children: string;
}) {
  return (
    <span className="flex items-center gap-2 rounded-full bg-deep/85 px-3 py-1 text-sm font-medium">
      <span className={`size-2 rounded-full ${dotClass}`} aria-hidden="true" />
      {children}
    </span>
  );
}
