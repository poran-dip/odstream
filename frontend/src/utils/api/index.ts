// Backend API client. Import from "utils/api" - this barrel re-exports
// everything from the modules in this folder:
//   types.ts         - shared response/data types
//   requestQueue.ts  - serializes requests that must not race
//   detectionApi.ts  - camera, recording, snapshot, video settings
//   videosApi.ts     - recorded videos + config (videosApi, configApi)

export { detectionApi } from "./detectionApi";
export type { ApiResponse, StopRecordingResponse, VideoFile } from "./types";
export { configApi, videosApi } from "./videosApi";
