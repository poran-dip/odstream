export const ERROR_MESSAGES = {
  CAMERA_CONNECTION: "Failed to connect to camera",
  BACKEND_CONNECTION: "Failed to connect to backend",
  RECORDING_START: "Please start detection first before recording",
  VIDEO_LOAD: "Failed to load video stream",
  SERVER_CONNECTION:
    "Failed to connect to server. Make sure the Flask backend is running.",
  DELETE_CONFIRM:
    "Are you sure you want to delete this video? This action cannot be undone.",
} as const;
