// The list of recordings, the currently selected one, and load/delete.

import { useCallback, useState } from "react";
import type { VideoFile } from "../../utils/api";
import { API_BASE_URL } from "./constants";

export function useVideoLibrary() {
  const [recordings, setRecordings] = useState<VideoFile[]>([]);
  const [currentVideo, setCurrentVideo] = useState<VideoFile | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch the video list. Selects `selectVideoId` if given and still
   * present, otherwise the first video (or none if the list is empty).
   */
  const loadVideos = useCallback(async (selectVideoId?: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/videos`);
      const data = await response.json();

      if (data.success) {
        setRecordings(data.videos);
        // Auto-select video by ID if specified, otherwise first video
        if (data.videos.length > 0) {
          let videoToSelect: VideoFile;
          if (selectVideoId) {
            videoToSelect =
              data.videos.find((v: VideoFile) => v.id === selectVideoId) ||
              data.videos[0];
          } else {
            videoToSelect = data.videos[0];
          }
          setCurrentVideo(videoToSelect);
        } else {
          setCurrentVideo(null);
        }
      } else {
        setError("Failed to load videos");
      }
    } catch (error) {
      setError(
        "Failed to connect to server. Make sure the Flask backend is running.",
      );
      console.error("Error loading videos:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleDeleteVideo = async (videoId: string) => {
    if (
      !confirm(
        "Are you sure you want to delete this video? This action cannot be undone.",
      )
    ) {
      return;
    }

    try {
      // Find the index of the video being deleted
      const deletedIndex = recordings.findIndex((v) => v.id === videoId);

      // Determine which video to select after deletion
      let videoToSelectAfterDelete: string | undefined;
      if (recordings.length > 1) {
        if (deletedIndex > 0) {
          // Select the video above (previous in list)
          videoToSelectAfterDelete = recordings[deletedIndex - 1].id;
        } else {
          // If deleting the first video, select the next one (which will become first)
          videoToSelectAfterDelete = recordings[deletedIndex + 1].id;
        }
      }
      // If only one video, videoToSelectAfterDelete stays undefined (will select none)

      const response = await fetch(`${API_BASE_URL}/videos/${videoId}/delete`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (data.success) {
        // Reload videos and select the appropriate one
        await loadVideos(videoToSelectAfterDelete);
      } else {
        setError(data.error || "Failed to delete video");
      }
    } catch (error) {
      setError("Failed to delete video");
      console.error("Error deleting video:", error);
    }
  };

  const handlePlayVideo = (video: VideoFile) => {
    setCurrentVideo(video);
  };

  return {
    recordings,
    currentVideo,
    setCurrentVideo,
    loading,
    error,
    setError,
    loadVideos,
    handleDeleteVideo,
    handlePlayVideo,
  };
}
