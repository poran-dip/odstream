import type { CameraSource } from "./storage";

{/*export const API_BASE_URL = 'http://localhost:5000/api'*/}
export const API_BASE_URL = 'http://192.168.29.203:5000/api'
export const JETSON_API_BASE_URL = 'https://jetson-nano.local:5000/api'

export const DEFAULT_SOURCES: CameraSource[] = [
  { id: 'webcam', name: 'Webcam', url: `${API_BASE_URL}/video_feed` },
  { id: 'jetson', name: 'Jetson Nano', url: `${JETSON_API_BASE_URL}/video_feed` }
];

export const DEFAULT_SETTINGS = {
  brightness: 50,
  contrast: 50,
  saturation: 50,
  annotateYOLO: true
};