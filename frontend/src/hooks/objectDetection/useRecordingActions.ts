// Recording and snapshot actions.
// Recording state itself is updated by the socket "recording_status" event.

import { detectionApi } from "../../utils/api";
import type { DetectionContext } from "./types";

/** "Error <action>: <message>" for an unknown thrown value. */
const describeError = (action: string, error: unknown) =>
  `Error ${action}: ` +
  (error instanceof Error ? error.message : String(error));

export function useRecordingActions(ctx: DetectionContext) {
  const { isDetecting, setToast, showToast } = ctx;

  const handleStartRecording = async () => {
    if (!isDetecting) {
      showToast("Please start detection first before recording");
      return;
    }

    try {
      setToast(null);
      const response = await detectionApi.startRecording();

      if (response.success) {
        // Don't set state here - let the socket event handle it
        console.log("Recording start request sent");
      } else {
        showToast(response.error || "Failed to start recording");
      }
    } catch (error) {
      console.error("Error starting recording:", error);
      showToast(describeError("starting recording", error));
    }
  };

  const handleStopRecording = async () => {
    try {
      setToast(null);
      const response = await detectionApi.stopRecording();

      if (response.success) {
        console.log("Recording stop request sent");
      } else {
        showToast(response.error || "Failed to stop recording");
      }
    } catch (error) {
      console.error("Error stopping recording:", error);
      showToast(describeError("stopping recording", error));
    }
  };

  const handleTakeSnapshot = async () => {
    try {
      const response = await detectionApi.takeSnapshot();

      if (response.success) {
        // Show success message or notification
        console.log("Snapshot taken:", response.message);
        showToast("Snapshot taken!", "success");
      } else {
        showToast(response.error || "Snapshot failed");
        console.error("Snapshot failed:", response.error);
      }
    } catch (error) {
      console.error("Error taking snapshot:", error);
      showToast(describeError("taking snapshot", error));
    }
  };

  return { handleStartRecording, handleStopRecording, handleTakeSnapshot };
}
