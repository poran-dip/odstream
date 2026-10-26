// All state and behaviour for the ObjectDetection page.
//
// Owns the page state and wires together the smaller hooks in this folder:
//   useCustomSources       - user-added sources (localStorage)
//   useInitialCameraState  - sync with backend on mount
//   useDetectionSocket     - live updates from the backend
//   useCameraActions       - start / stop / change source / save settings
//   useRecordingActions    - record / snapshot

import { useState, useRef } from "react";
import type {
  ToastDisplayProps,
  ToastType,
} from "../../components/ui/ToastDisplay";
import {
  DEFAULT_SETTINGS,
  type CameraSource,
  type VideoSettings,
} from "../../utils/storage";
import type { DetectionContext } from "./types";
import { useCustomSources } from "./useCustomSources";
import { useInitialCameraState } from "./useInitialCameraState";
import { useDetectionSocket } from "./useDetectionSocket";
import { useCameraActions } from "./useCameraActions";
import { useRecordingActions } from "./useRecordingActions";

export function useObjectDetection() {
  // --- Camera / recording status (mirrors the backend) ---
  const [isDetecting, setIsDetecting] = useState<boolean>(false);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [detectionStartTime, setDetectionStartTime] = useState(Number);

  // --- Source selection ---
  const [selectedSource, setSelectedSource] = useState<CameraSource | null>(
    null,
  );
  const [isLoadingSource, setIsLoadingSource] = useState<boolean>(true);

  // --- UI state ---
  const [loading, setLoading] = useState<boolean>(false);
  const [toast, setToast] = useState<ToastDisplayProps | null>(null);
  const [showSettings, setShowSettings] = useState<boolean>(false);
  const [showSourceDropdown, setShowSourceDropdown] = useState<boolean>(false);
  const [showStopConfirmation, setShowStopConfirmation] =
    useState<boolean>(false);
  const [settings, setSettings] = useState<VideoSettings>(DEFAULT_SETTINGS);

  const imgRef = useRef<HTMLImageElement>(null);

  const showToast = (message: string, type: ToastType = "error") => {
    setToast({ message, type });
  };

  const sources = useCustomSources({
    selectedSource,
    setSelectedSource,
    showToast,
  });

  // Bundle passed to the effect/action hooks below
  const ctx: DetectionContext = {
    isDetecting,
    setIsDetecting,
    isRecording,
    setIsRecording,
    setDetectionStartTime,
    selectedSource,
    setSelectedSource,
    isLoadingSource,
    setIsLoadingSource,
    customSources: sources.customSources,
    setCustomSources: sources.setCustomSources,
    setLoading,
    setToast,
    setShowSourceDropdown,
    setShowStopConfirmation,
    setSettings,
    imgRef,
    showToast,
  };

  // Effects run in this order: initial load first, then the socket
  useInitialCameraState(ctx);
  useDetectionSocket(ctx);

  const cameraActions = useCameraActions(ctx);
  const recordingActions = useRecordingActions(ctx);

  return {
    // state
    isDetecting,
    isRecording,
    detectionStartTime,
    selectedSource,
    isLoadingSource,
    loading,
    toast,
    setToast,
    showSettings,
    setShowSettings,
    showSourceDropdown,
    setShowSourceDropdown,
    showStopConfirmation,
    setShowStopConfirmation,
    settings,
    setSettings,
    imgRef,
    // sub-hooks
    sources,
    ...cameraActions,
    ...recordingActions,
  };
}
