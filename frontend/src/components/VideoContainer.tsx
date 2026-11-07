// Video frame shared by the live view and the recordings player.
// Status pills sit over the top-left corner, optional actions (e.g. the
// full-screen button) over the top-right; bottomContent is attached to the
// bottom edge of the same frame (the readout strip / file details).

import { Camera } from "lucide-react";
import type { ReactNode, RefObject } from "react";

interface VideoContainerProps {
  children?: ReactNode;
  showPlaceholder: boolean;
  placeholderTitle: string;
  placeholderDescription: string;
  statusIndicators?: ReactNode;
  topRightActions?: ReactNode;
  bottomContent?: ReactNode;
  className?: string;
  /** Element passed to useFullscreen */
  containerRef?: RefObject<HTMLElement | null>;
  /** Fill the whole screen (native full screen or the fallback overlay) */
  fullscreen?: boolean;
}

const VideoContainer: React.FC<VideoContainerProps> = ({
  children,
  showPlaceholder,
  placeholderTitle,
  placeholderDescription,
  statusIndicators = null,
  topRightActions = null,
  bottomContent = null,
  className = "",
  containerRef,
  fullscreen = false,
}) => {
  return (
    <section
      ref={containerRef}
      className={`panel min-w-0 overflow-hidden ${
        fullscreen
          ? "fixed inset-0 z-100 flex flex-col rounded-none border-0 bg-well"
          : ""
      } ${className}`}
    >
      {/* Fixed 16:9 in the page; fills the remaining height in full screen */}
      <div
        className={`relative bg-well ${fullscreen ? "min-h-0 flex-1" : "aspect-video"}`}
      >
        {showPlaceholder ? (
          <div className="absolute inset-0 grid place-items-center p-6 text-center">
            <div>
              <Camera
                className="mx-auto mb-3 size-10 text-silt"
                strokeWidth={1.5}
              />
              <h2 className="text-lg font-semibold">{placeholderTitle}</h2>
              <p className="mt-1 max-w-sm text-sm text-silt">
                {placeholderDescription}
              </p>
            </div>
          </div>
        ) : (
          children
        )}

        {statusIndicators && (
          <div className="absolute left-3 top-3 flex gap-2">
            {statusIndicators}
          </div>
        )}

        {topRightActions && (
          <div className="absolute right-3 top-3 flex gap-2">
            {topRightActions}
          </div>
        )}
      </div>

      {bottomContent && (
        <div
          className={`border-t border-line ${fullscreen ? "shrink-0 bg-hull" : ""}`}
        >
          {bottomContent}
        </div>
      )}
    </section>
  );
};

export default VideoContainer;
