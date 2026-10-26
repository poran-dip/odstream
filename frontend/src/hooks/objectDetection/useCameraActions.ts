// Camera-level actions: start, stop (with confirmation), switch source,
// and save video settings.
//
// Most of these only send the request; the resulting state change arrives
// via the socket (see useDetectionSocket) so all clients stay in sync.

import { detectionApi } from "../../utils/api";
import type { CameraSource, VideoSettings } from "../../utils/storage";
import type { DetectionContext } from "./types";

export function useCameraActions(ctx: DetectionContext) {
  const {
    selectedSource,
    setLoading,
    setToast,
    setSelectedSource,
    setShowSourceDropdown,
    setShowStopConfirmation,
    setIsDetecting,
    showToast,
  } = ctx;

  const startDetection = async () => {
    setLoading(true);

    if (!selectedSource) {
      showToast("Unable to start detection: No source was provided", "error");
      return;
    }

    try {
      const response = await detectionApi.startCamera(selectedSource);

      if (response.message && !response.error) {
        console.log("Detection start request sent");
      } else {
        showToast(response.error || response.message || "Something went wrong");
      }
    } catch (err) {
      console.error("Start detection error:", err);
      showToast("Failed to connect to backend");
    } finally {
      setLoading(false);
    }
  };

  // Stopping affects every connected client, so ask for confirmation first
  const handleStopDetectionClick = () => {
    setShowStopConfirmation(true);
  };

  const confirmStopDetection = async () => {
    setShowStopConfirmation(false);
    setLoading(true);

    try {
      await detectionApi.stopCamera();
      // Don't set state here - let the socket event handle it
      console.log("Detection stop request sent");
    } catch (err) {
      console.error("Stop camera error:", err);
      showToast("Failed to stop camera");
    } finally {
      setLoading(false);
    }
  };

  const handleSourceChange = async (source: CameraSource) => {
    setLoading(true);
    try {
      const response = await detectionApi.changeSource(source);

      if (response.success) {
        console.log(response.message ?? "Camera source changed");
        setToast(null);
        setSelectedSource(source); // Update UI state
        setShowSourceDropdown(false);

        setTimeout(() => {
          setIsDetecting(true);
        }, 100);
      } else {
        console.error(response.error ?? response.message);
        showToast(`Failed to change source to ${source.name}`);
      }
    } catch (err) {
      console.error("Change camera source error:", err);
      showToast("Failed to connect to backend");
    } finally {
      setLoading(false);
    }
  };

  const updateVideoSettings = async (newSettings: Partial<VideoSettings>) => {
    try {
      setLoading(true);
      const response = await detectionApi.updateVideoSettings(newSettings);

      if (response.success) {
        showToast("Video settings updated successfully!", "success");
      } else {
        showToast(response.error || "Failed to update video settings", "error");
      }
    } catch (error) {
      console.error("Error updating video settings:", error);
      showToast("Failed to update video settings", "error");
    } finally {
      setLoading(false);
    }
  };

  return {
    startDetection,
    handleStopDetectionClick,
    confirmStopDetection,
    handleSourceChange,
    updateVideoSettings,
  };
}
