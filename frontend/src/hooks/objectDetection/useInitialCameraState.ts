// On mount: load custom sources and sync the page with the backend's
// current camera source, camera/recording status and video settings.

import { useEffect } from "react";
import { detectionApi } from "../../utils/api";
import {
  createTempSource,
  findMatchingSource,
} from "../../utils/cameraSources";
import { DEFAULT_SOURCES } from "../../utils/config";
import { startTimeFromUptime } from "../../utils/formatters";
import { storageUtils } from "../../utils/storage";
import type { DetectionContext } from "./types";

export function useInitialCameraState(ctx: DetectionContext) {
  const {
    setIsLoadingSource,
    setCustomSources,
    setSelectedSource,
    setIsDetecting,
    setIsRecording,
    setDetectionStartTime,
    setSettings,
  } = ctx;

  // Load current source from backend on component mount
  useEffect(() => {
    const loadCurrentSource = async () => {
      setIsLoadingSource(true);
      try {
        // First load custom sources so we have the complete list
        const loadedCustomSources = storageUtils.getCustomSources();
        setCustomSources(loadedCustomSources);

        const response = await detectionApi.getCameraStatus();

        if (response.source) {
          // Find matching source from all available sources (including newly loaded custom ones)
          const allSources = [...DEFAULT_SOURCES, ...loadedCustomSources];
          const matchedSource = findMatchingSource(response.source, allSources);

          if (matchedSource) {
            console.log("Loaded current source from backend:", matchedSource);
            setSelectedSource(matchedSource);
          } else {
            console.warn(
              "Backend source not found in available sources:",
              response.source,
            );
            console.log("Available sources:", allSources);

            // Create a temporary source object if it's not in our predefined list
            // This handles cases where backend has a source not in our DEFAULT_SOURCES
            const tempSource = createTempSource(response.source);

            console.log("Using temporary source:", tempSource);
            setSelectedSource(tempSource);
          }

          // Also set initial states from the camera status
          setIsDetecting(response.active || false);
          setIsRecording(response.recording || false);
          if (response.active) {
            // Real camera uptime from the backend, not time since page load
            setDetectionStartTime(startTimeFromUptime(response.uptime_seconds));
          }
        } else {
          console.warn("No source in camera status response, using default");
          setSelectedSource(DEFAULT_SOURCES[0]);
        }

        try {
          const settingsResponse = await detectionApi.getVideoSettings();
          if (settingsResponse.success && settingsResponse.data) {
            setSettings(settingsResponse.data);
          }
        } catch (error) {
          console.error("Error loading video settings:", error);
        }
      } catch (error) {
        console.error("Error loading camera status:", error);
        setSelectedSource(DEFAULT_SOURCES[0]);
      } finally {
        setIsLoadingSource(false);
      }
    };

    loadCurrentSource();
    // Run once on mount only (the setters are stable useState setters)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    setSettings,
    setIsRecording,
    setDetectionStartTime,
    setSelectedSource,
    setIsLoadingSource, // Also set initial states from the camera status
    setIsDetecting,
    setCustomSources,
  ]);
}
