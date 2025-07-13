import { Play, Square, Camera } from 'lucide-react';
import type { CameraSource } from '../utils/storage';

interface ControlsPanelProps {
  isDetecting: boolean;
  isRecording: boolean;
  loading: boolean;
  selectedSource: CameraSource;
  onStartDetection: () => void;
  onStopDetection: () => void;
  onStartRecording: () => void;
  onStopRecording: () => void;
  onTakeSnapshot: () => void;
}

const ControlsPanel: React.FC<ControlsPanelProps> = ({
  isDetecting,
  isRecording,
  loading,
  selectedSource,
  onStartDetection,
  onStopDetection,
  onStartRecording,
  onStopRecording,
  onTakeSnapshot
}) => {
  return (
    <div className="space-y-4">
      {/* Detection Controls */}
      <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-600/30 rounded-2xl p-6">
        <h3 className="text-lg font-semibold mb-4 text-slate-200">Detection Controls</h3>
        
        <div className="space-y-3">
          <button
            onClick={onStartDetection}
            disabled={loading || isDetecting}
            className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 hover:scale-105 disabled:hover:scale-100"
          >
            <Play className="w-5 h-5" />
            <span>{loading ? 'Starting...' : 'Start Detection'}</span>
          </button>
          
          <button
            onClick={onStopDetection}
            disabled={loading || !isDetecting}
            className="w-full bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 hover:scale-105 disabled:hover:scale-100"
          >
            <Square className="w-5 h-5" />
            <span>{loading ? 'Stopping...' : 'Stop Detection'}</span>
          </button>
        </div>
      </div>

      {/* Recording Controls */}
      <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-600/30 rounded-2xl p-6">
        <h3 className="text-lg font-semibold mb-4 text-slate-200">Recording</h3>
        
        <button
          onClick={isRecording ? onStopRecording : onStartRecording}
          className={`w-full font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 hover:scale-105 mb-3 ${
            isRecording
              ? 'bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700'
              : 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700'
          }`}
        >
          {isRecording ? (
            <>
              <Square className="w-5 h-5" />
              <span>Stop Recording</span>
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              <span>Start Recording</span>
            </>
          )}
        </button>

        <button
          onClick={onTakeSnapshot}
          className="w-full font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 hover:scale-105 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700"
        >
          <Camera className="w-5 h-5" />
          <span>Take Snapshot</span>
        </button>
      </div>

      {/* Quick Stats */}
      <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-600/30 rounded-2xl p-6">
        <h3 className="text-lg font-semibold mb-4 text-slate-200">System Status</h3>
              
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-slate-400">Detection</span>
            <span className={`font-semibold ${isDetecting ? 'text-green-400' : 'text-slate-400'}`}>
              {isDetecting ? 'Active' : 'Inactive'}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-slate-400">Recording</span>
            <span className={`font-semibold ${isRecording ? 'text-red-400' : 'text-slate-400'}`}>
              {isRecording ? 'Recording' : 'Stopped'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Source</span>
                  <span className="font-semibold text-blue-400">{selectedSource.name}</span>
                </div>
                {/*
                <div className="flex justify-between items-center">
                  <span className="text-slate-400">Recordings</span>
                  <span className="font-semibold text-blue-400">{recordings.length}</span>
                </div>
                */}
              </div>
            </div>
    </div>
  );
};

export default ControlsPanel;