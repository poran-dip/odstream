// Camera, recording, snapshot and video-settings endpoints.

import { API_BASE_URL } from "../config";
import type { CameraSource, VideoSettings } from "../storage";
import { RequestQueue } from "./requestQueue";
import type { ApiResponse, StopRecordingResponse } from "./types";

// Separate queues so camera and recording requests are each serialized
const cameraQueue = new RequestQueue();
const recordingQueue = new RequestQueue();

export const detectionApi = {
  // --- Camera ---

  startCamera: async (source: CameraSource): Promise<ApiResponse> => {
    return cameraQueue.add(async () => {
      const response = await fetch(`${API_BASE_URL}/start_camera`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source }),
      });
      return response.json();
    });
  },

  stopCamera: async (): Promise<ApiResponse> => {
    return cameraQueue.add(async () => {
      const response = await fetch(`${API_BASE_URL}/stop_camera`);
      return response.json();
    });
  },

  isCameraActive: async (): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE_URL}/is_camera_active`);
    return response.json();
  },

  /** Never throws: returns `{ active: false, error }` on failure. */
  getCameraStatus: async (): Promise<{
    active: boolean;
    source?: CameraSource;
    detection_enabled?: boolean;
    recording?: boolean;
    model_loaded?: boolean;
    error?: string;
  }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/camera_status`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error("Get camera status error:", error);
      return { active: false, error: "Failed to get camera status" };
    }
  },

  changeSource: async (source: CameraSource): Promise<ApiResponse> => {
    return cameraQueue.add(async () => {
      const res = await fetch(`${API_BASE_URL}/change_camera_source`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source }),
      });
      return res.json();
    });
  },

  // --- Recording & snapshots ---

  startRecording: async (outputPath?: string): Promise<ApiResponse> => {
    return recordingQueue.add(async () => {
      const response = await fetch(`${API_BASE_URL}/start_recording`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          output_path: outputPath,
        }),
      });
      return response.json();
    });
  },

  stopRecording: async (): Promise<ApiResponse<StopRecordingResponse>> => {
    return recordingQueue.add(async () => {
      const response = await fetch(`${API_BASE_URL}/stop_recording`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      return response.json();
    });
  },

  takeSnapshot: async (): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE_URL}/snapshot`, {
      method: "POST",
    });
    return response.json();
  },

  // --- Video settings ---

  updateVideoSettings: async (
    settings: Partial<VideoSettings>,
  ): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE_URL}/update_video_settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    });
    return response.json();
  },

  getVideoSettings: async (): Promise<ApiResponse<VideoSettings>> => {
    const response = await fetch(`${API_BASE_URL}/video_settings`);
    return response.json();
  },
};
