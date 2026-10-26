// Socket.IO connection to the backend. The backend broadcasts camera,
// recording and video-settings changes so every open client stays in sync;
// this hook applies those updates to the page state.

import { useEffect, type RefObject } from "react";
import { io } from "socket.io-client";
import { API_BASE_URL, DEFAULT_SOURCES } from "../../utils/config";
import {
  createTempSource,
  findMatchingSource,
} from "../../utils/cameraSources";
import type { DetectionContext } from "./types";

const VIDEO_FEED_URL = `${API_BASE_URL}/video_feed`;

/**
 * Point the <img> at the MJPEG feed, retrying after 2s on error.
 * Takes the ref (not the element) so the retry uses whatever element is
 * mounted at that time.
 */
function attachMjpegStream(imgRef: RefObject<HTMLImageElement | null>) {
  if (!imgRef.current) return;

  const videoUrl = VIDEO_FEED_URL;

  console.log("Setting up MJPEG stream:", videoUrl);

  imgRef.current.src = videoUrl;

  imgRef.current.onload = () => {
    console.log("MJPEG stream connected successfully");
  };

  imgRef.current.onerror = (e) => {
    console.error("MJPEG stream error:", e);

    setTimeout(() => {
      if (imgRef.current) {
        console.log("Retrying MJPEG stream connection...");
        imgRef.current.src = videoUrl;
      }
    }, 2000);
  };
}

export function useDetectionSocket(ctx: DetectionContext) {
  const {
    customSources,
    selectedSource,
    isLoadingSource,
    setSelectedSource,
    setIsDetecting,
    setDetectionStartTime,
    setIsRecording,
    setSettings,
    imgRef,
    showToast,
  } = ctx;

  useEffect(() => {
    // Wait until the initial source has been loaded
    if (isLoadingSource || !selectedSource) return;

    const newSocket = io(API_BASE_URL.replace("/api", ""));

    newSocket.on("connect", () => {
      console.log("Connected to backend socket");
    });

    newSocket.on("disconnect", () => {
      console.log("Disconnected from backend socket");
    });

    // --- Camera started / stopped / source changed ---
    newSocket.on("camera_status", (data) => {
      console.log("Camera status update:", data);

      // Find matching source from all available sources
      const allSources = [...DEFAULT_SOURCES, ...customSources];
      const matchedSource = findMatchingSource(data.source, allSources);

      if (matchedSource && matchedSource.id !== selectedSource?.id) {
        console.log(
          "Backend source changed, updating frontend to match:",
          matchedSource,
        );
        setSelectedSource(matchedSource);
      } else if (!matchedSource && data.source) {
        // Handle case where backend source is not in our predefined sources
        console.log(
          "Backend using unknown source, creating temporary source:",
          data.source,
        );

        setSelectedSource(createTempSource(data.source));
      }

      if (data.active) {
        setIsDetecting(true);
        setDetectionStartTime(Date.now());

        console.log("Camera active logged");

        // Give React a moment to render the <img> before attaching the stream
        setTimeout(() => attachMjpegStream(imgRef), 100);
      } else {
        setIsDetecting(false);
        if (imgRef.current) {
          imgRef.current.src = "";
        }
      }
    });

    // --- Recording started / stopped ---
    newSocket.on("recording_status", (data) => {
      console.log("Recording status update:", data);
      setIsRecording(data.recording);
    });

    // --- Brightness / contrast / saturation changed ---
    newSocket.on("video_settings_updated", (data) => {
      console.log("Video settings update from socket:", data);
      if (data.data) {
        setSettings((prev) => ({ ...prev, ...data.data }));
        // Show toast only if it's from another user (you can add logic to detect this)
        if (data.message) {
          showToast(data.message, "info");
        }
      }
    });

    return () => {
      newSocket.disconnect();
    };
    // Reconnect only when these change (setters/ref are stable)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [customSources, selectedSource, isLoadingSource]);
}
