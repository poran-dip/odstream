import { API_URL } from "../../../shared/runtime-env";
import type { CameraSource } from "./storage";

export const API_BASE_URL = `http://${API_URL}:5000/api`;
export const JETSON_API_BASE_URL = "http://jetson-nano.local:5000/api";

export const DEFAULT_SOURCES: CameraSource[] = [
  { id: "local-1", name: "Local Cam 1", type: "local", index: 0 },
  { id: "local-2", name: "Local Cam 2", type: "local", index: 1 },
  { id: "local-3", name: "Local Cam 3", type: "local", index: 2 },
  {
    id: "jetson",
    name: "Jetson Nano",
    type: "remote",
    url: `${JETSON_API_BASE_URL}/video_feed`,
  },
];
