// Right-hand library panel: folder + refresh controls and the list of
// recordings.

import { FolderOpen, RefreshCw } from "lucide-react";
import type { VideoFile } from "../../utils/api";
import VideoListItem from "./VideoListItem";

interface VideoLibraryProps {
  recordings: VideoFile[];
  currentVideo: VideoFile | null;
  currentPath: string;
  loading: boolean;
  onRefresh: () => void;
  onChangeDirectory: () => void;

  // Row actions / rename state
  editingId: string | null;
  editingName: string;
  setEditingName: (value: string) => void;
  onPlay: (video: VideoFile) => void;
  onRenameStart: (video: VideoFile) => void;
  onRenameConfirm: () => void;
  onRenameCancel: () => void;
  onDelete: (videoId: string) => void;
}

export default function VideoLibrary({
  recordings,
  currentVideo,
  currentPath,
  loading,
  onRefresh,
  onChangeDirectory,
  editingId,
  ...rowProps
}: VideoLibraryProps) {
  const count = recordings.length;

  return (
    <aside className="panel flex min-h-0 flex-col self-start lg:max-h-[calc(100vh-7rem)]">
      {/* Panel header */}
      <div className="border-b border-line p-4">
        <div className="flex items-center justify-between gap-2">
          <h2 className="font-semibold">
            Library{" "}
            <span className="font-normal text-silt tabular-nums">
              {count} {count === 1 ? "recording" : "recordings"}
            </span>
          </h2>
          <button
            type="button"
            onClick={onRefresh}
            disabled={loading}
            title="Refresh"
            aria-label="Refresh recordings"
            className="icon-btn size-8"
          >
            <RefreshCw
              className={`size-4 ${loading ? "motion-safe:animate-spin" : ""}`}
            />
          </button>
        </div>

        {/* Folder the backend reads recordings from */}
        <button
          type="button"
          onClick={onChangeDirectory}
          title={currentPath}
          className="mt-3 flex w-full items-center gap-2 rounded-md border border-line px-3 py-2 text-left text-sm transition-colors hover:bg-raised"
        >
          <FolderOpen className="size-4 shrink-0 text-silt" />
          <span className="min-w-0 flex-1 truncate text-silt" dir="rtl">
            {/* rtl keeps the end of long paths (the folder name) visible */}
            <bdi>{currentPath || "No folder set"}</bdi>
          </span>
          <span className="shrink-0 font-medium">Change</span>
        </button>
      </div>

      {/* List (or empty state) */}
      {count === 0 ? (
        <div className="p-6 text-center">
          <p className="font-medium">
            {loading ? "Loading recordings…" : "This folder has no recordings"}
          </p>
          {!loading && (
            <p className="mt-1 text-sm text-silt">
              Record on the live page, or point the library at another folder.
            </p>
          )}
        </div>
      ) : (
        <ul className="min-h-0 flex-1 divide-y divide-line overflow-y-auto">
          {recordings.map((video) => (
            <VideoListItem
              key={video.id}
              video={video}
              isSelected={currentVideo?.id === video.id}
              isEditing={editingId === video.id}
              {...rowProps}
            />
          ))}
        </ul>
      )}
    </aside>
  );
}
