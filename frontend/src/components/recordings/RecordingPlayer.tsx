// Video player area with the selected recording's details attached below.

import { getVideoUrl } from "../../hooks/recordings/constants";
import type { VideoFile } from "../../utils/api";
import { formatDate, formatFileSize } from "../../utils/formatters";
import VideoContainer from "../VideoContainer";

interface RecordingPlayerProps {
  currentVideo: VideoFile | null;
  /** Used to pick the placeholder hint when nothing is selected */
  hasRecordings: boolean;
}

export default function RecordingPlayer({
  currentVideo,
  hasRecordings,
}: RecordingPlayerProps) {
  return (
    <VideoContainer
      showPlaceholder={!currentVideo}
      placeholderTitle={
        hasRecordings ? "Pick a recording" : "No recordings yet"
      }
      placeholderDescription={
        hasRecordings
          ? "Choose a recording from the library to play it here."
          : "Recordings you make on the live page show up in the library."
      }
      bottomContent={
        currentVideo && (
          <div className="flex flex-col gap-1 px-4 py-3 sm:flex-row sm:items-baseline sm:justify-between sm:gap-6">
            <h2 className="min-w-0 truncate font-medium">
              {currentVideo.name}
            </h2>
            <dl className="flex shrink-0 gap-5 text-sm">
              <div className="flex gap-1.5">
                <dt className="text-silt">Size</dt>
                <dd className="tabular-nums">
                  {formatFileSize(currentVideo.size)}
                </dd>
              </div>
              <div className="flex gap-1.5">
                <dt className="text-silt">Recorded</dt>
                <dd className="tabular-nums">
                  {formatDate(currentVideo.lastModified)}
                </dd>
              </div>
            </dl>
          </div>
        )
      }
    >
      {/* key forces a fresh <video> element when the selection changes */}
      {currentVideo && (
        // biome-ignore lint/a11y/useMediaCaption: no caption tracks
        <video
          key={currentVideo.id}
          controls
          className="h-full w-full object-contain"
          src={getVideoUrl(currentVideo.name)}
        >
          Your browser does not support the video tag.
        </video>
      )}
    </VideoContainer>
  );
}
