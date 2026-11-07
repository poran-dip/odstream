// One row in the video library: name + meta, or an inline rename input,
// with play / rename / delete actions.

import { Check, PencilLine, Play, Trash2, X } from "lucide-react";
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

const ROW_ACTION =
  "rounded-md p-1.5 text-silt transition-colors hover:bg-deep hover:text-foam";

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
    <li>
      {/* biome-ignore lint/a11y/useKeyWithClickEvents: row click is a mouse shortcut; the Play button is the keyboard path */}
      {/* biome-ignore lint/a11y/noStaticElementInteractions: row click is a mouse shortcut; the Play button is the keyboard path */}
      <div
        className={`flex cursor-pointer items-center gap-2 border-l-2 py-3 pr-2 pl-3.5 transition-colors hover:bg-raised ${
          isSelected ? "border-l-foam bg-raised" : "border-l-transparent"
        }`}
        onClick={() => onPlay(video)}
        aria-current={isSelected ? "true" : undefined}
      >
        <div className="min-w-0 flex-1">
          {isEditing ? (
            // Inline rename (clicks here must not select the row)
            // biome-ignore lint/a11y/useKeyWithClickEvents: only stops click propagation to the row
            // biome-ignore lint/a11y/noStaticElementInteractions: only stops click propagation to the row
            <div
              className="flex items-center gap-1"
              onClick={(e) => e.stopPropagation()}
            >
              <input
                type="text"
                value={editingName}
                aria-label="New name"
                onChange={(e) => setEditingName(e.target.value)}
                className="field h-8 flex-1 px-2 text-sm"
                onKeyDown={(e) => e.key === "Enter" && onRenameConfirm()}
              />
              <button
                type="button"
                onClick={onRenameConfirm}
                aria-label="Save name"
                title="Save name"
                className={`${ROW_ACTION} hover:text-kelp`}
              >
                <Check className="size-4" />
              </button>
              <button
                type="button"
                onClick={onRenameCancel}
                aria-label="Cancel rename"
                title="Cancel"
                className={ROW_ACTION}
              >
                <X className="size-4" />
              </button>
            </div>
          ) : (
            <>
              <p className="truncate text-sm font-medium">{video.name}</p>
              <p className="mt-0.5 flex gap-3 text-sm text-silt tabular-nums">
                <span>{formatFileSize(video.size)}</span>
                <span>{formatDate(video.lastModified)}</span>
              </p>
            </>
          )}
        </div>

        {/* Row actions (hidden while renaming) */}
        {!isEditing && (
          // biome-ignore lint/a11y/useKeyWithClickEvents: only stops click propagation to the row
          // biome-ignore lint/a11y/noStaticElementInteractions: only stops click propagation to the row
          <div
            className="flex shrink-0 items-center"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onPlay(video);
              }}
              className={ROW_ACTION}
              title="Play video"
              aria-label={`Play ${video.name}`}
            >
              <Play className="size-4" />
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onRenameStart(video);
              }}
              className={ROW_ACTION}
              title="Rename video"
              aria-label={`Rename ${video.name}`}
            >
              <PencilLine className="size-4" />
            </button>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(video.id);
              }}
              className={`${ROW_ACTION} hover:text-signal`}
              title="Delete video"
              aria-label={`Delete ${video.name}`}
            >
              <Trash2 className="size-4" />
            </button>
          </div>
        )}
      </div>
    </li>
  );
}
