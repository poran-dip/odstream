import { Camera } from 'lucide-react';
import type { ReactNode } from 'react';

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
  className = ""
}) => {
  return (
    <div className={`lg:col-span-3 ${className}`}>
      <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-600/30 rounded-2xl overflow-hidden">
        <div className="relative aspect-video bg-gradient-to-br from-slate-800 to-slate-900">
          {showPlaceholder ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <Camera className="w-20 h-20 text-slate-500 mx-auto mb-6" />
                <h3 className="text-xl font-semibold text-slate-300 mb-2">
                  {placeholderTitle}
                </h3>
                <p className="text-slate-400">
                  {placeholderDescription}
                </p>
              </div>
            </div>
          ) : (
            children
          )}
          
          {/* Status Indicators */}
          {statusIndicators && (
            <div className="absolute top-4 left-4 flex space-x-2">
              {statusIndicators}
            </div>
          )}
        </div>
      </div>
      
      {/* Bottom Content */}
      {bottomContent && (
        <div className="mt-6 bg-slate-800/30 backdrop-blur-sm border border-slate-600/30 rounded-2xl p-6">
          {bottomContent}
        </div>
      )}
    </div>
  );
};

export default VideoContainer;