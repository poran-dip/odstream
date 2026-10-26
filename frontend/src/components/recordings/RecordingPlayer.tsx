// Video player area with the selected recording's details underneath.

import VideoContainer from "../VideoContainer";
import type { VideoFile } from "../../utils/api";
import { formatDate, formatFileSize } from "../../utils/formatters";
import { getVideoUrl } from "../../hooks/recordings/constants";

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
      placeholderTitle="No Video Selected"
      placeholderDescription={
        !hasRecordings
          ? "Load videos from your directory"
          : "Select a video from the library to play"
      }
      bottomContent={
        currentVideo ? (
          <>
            <h3 className="text-lg font-semibold text-slate-200 mb-2 truncate max-w-full">
              {currentVideo.name}
            </h3>
            <div className="flex items-center space-x-4 text-slate-400">
              <span>{formatFileSize(currentVideo.size)}</span>
              <span>•</span>
              <span>{formatDate(currentVideo.lastModified)}</span>
            </div>
          </>
        ) : (
          <p className="text-slate-400 text-center">
            No video playing yet. Pick one from the playlist!
          </p>
        )
      }
    >
      {/* key forces a fresh <video> element when the selection changes */}
      {currentVideo && (
        <video
          key={currentVideo.id}
          controls
          className="w-full h-full object-cover"
          src={getVideoUrl(currentVideo.name)}
        >
          Your browser does not support the video tag.
        </video>
      )}
    </VideoContainer>
  );
}
