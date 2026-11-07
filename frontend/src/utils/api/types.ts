// Shared types for the backend REST API.

export interface VideoFile {
  id: string;
  name: string;
  path: string;
  size: number;
  lastModified: number;
}

/** Generic response envelope returned by most backend endpoints. */
export interface ApiResponse<T = unknown> {
  success: boolean;
  error?: string;
  message?: string;
  data?: T;
}

export interface StopRecordingResponse {
  filename: string;
  message?: string;
}
