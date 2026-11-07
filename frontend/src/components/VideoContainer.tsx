// Video frame shared by the live view and the recordings player.
// Status pills sit over the top-left corner; bottomContent is attached to the
// bottom edge of the same frame (the readout strip / file details).

import { Camera } from "lucide-react";
import type { ReactNode } from "react";

interface VideoContainerProps {
  children?: ReactNode;
  showPlaceholder: boolean;
  placeholderTitle: string;
  placeholderDescription: string;
  statusIndicators?: ReactNode;
  bottomContent?: ReactNode;
  className?: string;
}

const VideoContainer: React.FC<VideoContainerProps> = ({
  children,
  showPlaceholder,
  placeholderTitle,
  placeholderDescription,
  statusIndicators = null,
  bottomContent = null,
  className = "",
}) => {
  return (
    <section className={`panel min-w-0 overflow-hidden ${className}`}>
      <div className="relative aspect-video bg-well">
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
      </div>

      {bottomContent && (
        <div className="border-t border-line">{bottomContent}</div>
      )}
    </section>
  );
};

export default VideoContainer;
