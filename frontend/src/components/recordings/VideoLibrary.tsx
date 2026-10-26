// Right-hand "Video Library" panel: refresh / change-directory buttons and
// the list of recordings.

import { Folder, RefreshCw, Settings } from "lucide-react";
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
  return (
    <div className="lg:col-span-1 flex flex-col h-full">
      <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-600/30 rounded-2xl overflow-hidden h-full flex flex-col">
        {/* Panel header */}
        <div className="p-6 border-b border-slate-600/30">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-slate-200">
              Video Library
            </h3>
            <span className="text-sm text-slate-400">
              {recordings.length} videos
            </span>
          </div>

          <p className="text-sm text-slate-400 mb-4 truncate">
            Path: {currentPath}
          </p>

          <div className="space-y-2">
            <button
              onClick={onRefresh}
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 hover:scale-105 disabled:opacity-50"
            >
              <RefreshCw
                className={`w-5 h-5 ${loading ? "animate-spin" : ""}`}
              />
              <span>{loading ? "Loading..." : "Refresh Videos"}</span>
            </button>

            <button
              onClick={onChangeDirectory}
              className="w-full bg-slate-700 hover:bg-slate-600 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 hover:scale-105"
            >
              <Settings className="w-5 h-5" />
              <span>Change Directory</span>
            </button>
          </div>
        </div>

        {/* List (or empty state) */}
        {recordings.length === 0 ? (
          <div className="flex flex-col items-center justify-center text-center h-full p-6">
            <Folder className="w-16 h-16 text-slate-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-slate-300 mb-2">
              {loading ? "Loading Videos..." : "No Videos Found"}
            </h3>
            <p className="text-slate-400 text-sm">
              {loading
                ? "Please wait..."
                : "Check your directory path or refresh to load videos"}
            </p>
          </div>
        ) : (
          <div className="max-h-100 h-full overflow-y-auto">
            {recordings.map((video) => (
              <VideoListItem
                key={video.id}
                video={video}
                isSelected={currentVideo?.id === video.id}
                isEditing={editingId === video.id}
                {...rowProps}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
