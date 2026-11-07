// State + setters shared between the ObjectDetection page's hooks.
// useObjectDetection owns the state and passes this bundle to the
// smaller hooks so they can read and update it.

import type { Dispatch, RefObject, SetStateAction } from "react";
import type {
  ToastDisplayProps,
  ToastType,
} from "../../components/ui/ToastDisplay";
import type { CameraSource, VideoSettings } from "../../utils/storage";

type Setter<T> = Dispatch<SetStateAction<T>>;

export interface DetectionContext {
  // Camera / recording state (mirrors the backend, updated via socket)
  isDetecting: boolean;
  setIsDetecting: Setter<boolean>;
  isRecording: boolean;
  setIsRecording: Setter<boolean>;
  setDetectionStartTime: Setter<number>;

  // Live performance metrics (from the backend's "perf_update" event)
  setCurrentFps: Setter<number>;
  setLatencyMs: Setter<number | null>;
  setDetectionCount: Setter<number>;

  // Active source
  selectedSource: CameraSource | null;
  setSelectedSource: Setter<CameraSource | null>;
  isLoadingSource: boolean;
  setIsLoadingSource: Setter<boolean>;
  customSources: CameraSource[];
  setCustomSources: Setter<CameraSource[]>;

  // UI state
  setLoading: Setter<boolean>;
  setToast: Setter<ToastDisplayProps | null>;
  setShowSourceDropdown: Setter<boolean>;
  setShowStopConfirmation: Setter<boolean>;
  setSettings: Setter<VideoSettings>;

  /** <img> element showing the MJPEG stream */
  imgRef: RefObject<HTMLImageElement | null>;

  showToast: (message: string, type?: ToastType) => void;
}
