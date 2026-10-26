// Inline rename of a recording in the library list.

import { useState, type Dispatch, type SetStateAction } from "react";
import type { VideoFile } from "../../utils/api";
import { API_BASE_URL } from "./constants";

interface UseVideoRenameArgs {
  currentVideo: VideoFile | null;
  setCurrentVideo: Dispatch<SetStateAction<VideoFile | null>>;
  setError: (error: string | null) => void;
  loadVideos: (selectVideoId?: string) => Promise<void>;
}

export function useVideoRename({
  currentVideo,
  setCurrentVideo,
  setError,
  loadVideos,
}: UseVideoRenameArgs) {
  // ID of the video currently being renamed (null = not editing)
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState("");

  const handleRenameStart = (video: VideoFile) => {
    setEditingId(video.id);
    setEditingName(video.name);
  };

  const handleRenameConfirm = async () => {
    if (!editingId || !editingName.trim()) {
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/videos/${editingId}/rename`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            new_name: editingName.trim(),
          }),
        },
      );

      const data = await response.json();

      if (data.success) {
        // Reload videos after rename
        await loadVideos(editingId);

        // Update current video if it was renamed
        if (currentVideo?.id === editingId) {
          setCurrentVideo((prev) =>
            prev ? { ...prev, name: data.new_name, id: data.new_name } : null,
          );
        }
      } else {
        setError(data.error || "Failed to rename video");
      }
    } catch (error) {
      setError("Failed to rename video");
      console.error("Error renaming video:", error);
    } finally {
      setEditingId(null);
      setEditingName("");
    }
  };

  const handleRenameCancel = () => {
    setEditingId(null);
    setEditingName("");
  };

  return {
    editingId,
    editingName,
    setEditingName,
    handleRenameStart,
    handleRenameConfirm,
    handleRenameCancel,
  };
}
