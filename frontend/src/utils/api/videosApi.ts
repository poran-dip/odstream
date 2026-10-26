// Recorded videos and app config endpoints.

import { API_BASE_URL } from "../config";
import { RequestQueue } from "./requestQueue";
import type { ApiResponse, VideoFile } from "./types";

// Serializes delete/rename so they can't interleave
const videoQueue = new RequestQueue();

// Videos API
export const videosApi = {
  getVideos: async (): Promise<ApiResponse<{ videos: VideoFile[] }>> => {
    const response = await fetch(`${API_BASE_URL}/videos`);
    return response.json();
  },

  deleteVideo: async (videoId: string): Promise<ApiResponse> => {
    return videoQueue.add(async () => {
      const response = await fetch(`${API_BASE_URL}/videos/${videoId}/delete`, {
        method: "DELETE",
      });
      return response.json();
    });
  },

  renameVideo: async (
    videoId: string,
    newName: string,
  ): Promise<ApiResponse<{ new_name: string }>> => {
    return videoQueue.add(async () => {
      const response = await fetch(`${API_BASE_URL}/videos/${videoId}/rename`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_name: newName }),
      });
      return response.json();
    });
  },

  getVideoUrl: (filename: string): string => {
    return `${API_BASE_URL}/videos/${encodeURIComponent(filename)}`;
  },
};

// Config API
export const configApi = {
  getConfig: async (): Promise<ApiResponse<{ video_path: string }>> => {
    const response = await fetch(`${API_BASE_URL}/config`);
    return response.json();
  },

  setVideoPath: async (
    path: string,
  ): Promise<ApiResponse<{ path: string }>> => {
    const response = await fetch(`${API_BASE_URL}/config/path`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    });
    return response.json();
  },
};
