// One row in the video library: name + meta, or an inline rename input,
// with play / rename / delete actions.

import { Check, Edit2, Play, Trash2, X } from "lucide-react";
import type { VideoFile } from "../../utils/api";
import { formatDate, formatFileSize } from "../../utils/formatters";

interface VideoListItemProps {
  video: VideoFile;
  isSelected: boolean;
  isEditing: boolean;
  editingName: string;
  setEditingName: (value: string) => void;
  onPlay: (video: VideoFile) => void;
  onRenameStart: (video: VideoFile) => void;
  onRenameConfirm: () => void;
  onRenameCancel: () => void;
  onDelete: (videoId: string) => void;
}

export default function VideoListItem({
  video,
  isSelected,
  isEditing,
  editingName,
  setEditingName,
  onPlay,
  onRenameStart,
  onRenameConfirm,
  onRenameCancel,
  onDelete,
}: VideoListItemProps) {
  return (
    // biome-ignore lint/a11y/useKeyWithClickEvents: row click is a mouse shortcut; the Play button is the keyboard path
    // biome-ignore lint/a11y/noStaticElementInteractions: row click is a mouse shortcut; the Play button is the keyboard path
    <div
      className={`p-4 border-b border-slate-600/30 last:border-b-0 hover:bg-slate-700/30 transition-colors cursor-pointer ${
        isSelected ? "bg-slate-700/50" : ""
      }`}
      onClick={() => onPlay(video)}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1 min-w-0">
          {isEditing ? (
            // Inline rename (clicks here must not select the row)
            // biome-ignore lint/a11y/useKeyWithClickEvents: only stops click propagation to the row
            // biome-ignore lint/a11y/noStaticElementInteractions: only stops click propagation to the row
            <div
              className="flex items-center space-x-2"
              onClick={(e) => e.stopPropagation()}
            >
              <input
                type="text"
                value={editingName}
                onChange={(e) => setEditingName(e.target.value)}
                className="flex-1 px-2 py-1 border border-slate-600 rounded bg-slate-800 text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                onKeyDown={(e) => e.key === "Enter" && onRenameConfirm()}
              />
              <button
                type="button"
                onClick={onRenameConfirm}
                className="p-1 text-green-400 hover:text-green-300 transition-colors"
              >
                <Check className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={onRenameCancel}
                className="p-1 text-red-400 hover:text-red-300 transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div>
              <p className="text-sm font-medium text-slate-200 truncate mb-1">
                {video.name}
              </p>
              <div className="flex items-center space-x-2 text-xs text-slate-400">
                <span>{formatFileSize(video.size)}</span>
                <span>•</span>
                <span>{formatDate(video.lastModified)}</span>
              </div>
            </div>
          )}
        </div>

        {/* Row actions (hidden while renaming) */}
        {!isEditing && (
          // biome-ignore lint/a11y/useKeyWithClickEvents: only stops click propagation to the row
          // biome-ignore lint/a11y/noStaticElementInteractions: only stops click propagation to the row
          <div
            className="flex items-center space-x-1 ml-2"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onPlay(video);
              }}
              className="p-2 text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 rounded-full transition-colors"
              title="Play video"
            >
              <Play className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onRenameStart(video);
              }}
              className="p-2 text-slate-400 hover:text-slate-300 hover:bg-slate-500/10 rounded-full transition-colors"
              title="Rename video"
            >
              <Edit2 className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(video.id);
              }}
              className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-full transition-colors"
              title="Delete video"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
