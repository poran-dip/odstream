// Live video panel: MJPEG <img>, RUNNING/RECORDING badges and stats footer.

import type { RefObject } from "react";
import { formatElapsedTime } from "../../utils/formatters";
import VideoContainer from "../VideoContainer";

interface DetectionVideoProps {
  isDetecting: boolean;
  isRecording: boolean;
  detectionStartTime: number;
  /** The MJPEG stream is attached to this <img> by useDetectionSocket */
  imgRef: RefObject<HTMLImageElement | null>;
}

export default function DetectionVideo({
  isDetecting,
  isRecording,
  detectionStartTime,
  imgRef,
}: DetectionVideoProps) {
  return (
    <VideoContainer
      showPlaceholder={!isDetecting}
      placeholderTitle="AI Detection Ready"
      placeholderDescription="Click 'Start Detection' to begin real-time object detection"
      statusIndicators={
        <>
          {isDetecting && (
            <div className="bg-green-500/20 border border-green-500/50 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-medium text-green-400 animate-pulse">
              ● RUNNING
            </div>
          )}
          {isRecording && (
            <div className="bg-red-500/20 border border-red-500/50 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-medium text-red-400 animate-pulse">
              ● RECORDING
            </div>
          )}
        </>
      }
      bottomContent={
        isDetecting ? (
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-200 mb-1">
                Detection Active
              </h3>
              <p className="text-slate-400">
                Time elapsed: {formatElapsedTime(detectionStartTime)}
              </p>
            </div>
            {/* Placeholders until object count / FPS are sent by the backend */}
            <div className="text-right">
              <p className="text-sm text-slate-400">
                Objects detected: 0 {/*detectedObjects.length*/}
              </p>
              <p className="text-sm text-slate-400">
                FPS: 0.0 {/*currentFPS*/}
              </p>
            </div>
          </div>
        ) : (
          <p className="text-slate-400 text-center">
            Start detection to view real-time statistics
          </p>
        )
      }
    >
      <img
        ref={imgRef}
        alt="Video Stream"
        className="w-full h-full object-cover"
      />
    </VideoContainer>
  );
}
