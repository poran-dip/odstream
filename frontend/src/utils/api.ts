import type { CameraSource } from "./storage";
import { API_BASE_URL } from "./config";

export interface VideoFile {
  id: string;
  name: string;
  path: string;
  size: number;
  lastModified: number;
}

export interface ApiResponse<T = any> {
  success: boolean;
  error?: string;
  message?: string;
  data?: T;
}

export interface StopRecordingResponse {
  filename: string;
  message?: string;
}

// Detection API
export const detectionApi = {
  startCamera: async (source: CameraSource): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE_URL}/start_camera`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source })
    });
    return response.json();
  },

  stopCamera: async (): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE_URL}/stop_camera`);
    return response.json();
  },

  isCameraActive: async (): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE_URL}/is_camera_active`);
    return response.json();
  },

  getCameraStatus: async (): Promise<{ 
    active: boolean; 
    source?: any; 
    detection_enabled?: boolean; 
    recording?: boolean; 
    model_loaded?: boolean; 
    error?: string 
  }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/camera_status`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Get camera status error:', error);
      return { active: false, error: 'Failed to get camera status' };
    }
  },

  changeSource: async (source: CameraSource): Promise<ApiResponse> => {
    const res = await fetch(`${API_BASE_URL}/change_camera_source`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source }),
    });
    return res.json();
  },

  startRecording: async (outputPath?: string): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE_URL}/start_recording`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        output_path: outputPath
      })
    });
    return response.json();
  },

  stopRecording: async (): Promise<ApiResponse<StopRecordingResponse>> => {
    const response = await fetch(`${API_BASE_URL}/stop_recording`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    return response.json();
  },

  takeSnapshot: async (): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE_URL}/snapshot`, {
      method: 'POST',
    });
    return response.json();
  }
};

// Videos API
export const videosApi = {
  getVideos: async (): Promise<ApiResponse<{ videos: VideoFile[] }>> => {
    const response = await fetch(`${API_BASE_URL}/videos`);
    return response.json();
  },

  deleteVideo: async (videoId: string): Promise<ApiResponse> => {
    const response = await fetch(`${API_BASE_URL}/videos/${videoId}/delete`, {
      method: 'DELETE'
    });
    return response.json();
  },

  renameVideo: async (videoId: string, newName: string): Promise<ApiResponse<{ new_name: string }>> => {
    const response = await fetch(`${API_BASE_URL}/videos/${videoId}/rename`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ new_name: newName })
    });
    return response.json();
  },

  getVideoUrl: (filename: string): string => {
    return `${API_BASE_URL}/videos/${encodeURIComponent(filename)}`;
  }
};

// Config API
export const configApi = {
  getConfig: async (): Promise<ApiResponse<{ video_path: string }>> => {
    const response = await fetch(`${API_BASE_URL}/config`);
    return response.json();
  },

  setVideoPath: async (path: string): Promise<ApiResponse<{ path: string }>> => {
    const response = await fetch(`${API_BASE_URL}/config/path`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path })
    });
    return response.json();
  }
};