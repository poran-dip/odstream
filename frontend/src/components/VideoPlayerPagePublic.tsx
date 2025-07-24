{/*
  NOTE: This component is currently NOT in use.
  It's intended for production-level deployments where:
  - File access needs to be secured
  - Users should NOT be able to rename/delete each other's videos
  - The backend is exposed beyond a trusted local network

  For now, the system intentionally allows full local network access
  to simplify collaboration/testing on the same Wi-Fi.

  If going public or multi-user with real data:
  Enable this component and lock down file APIs with proper auth.
*/}

import React, { useState, useRef } from 'react';
import { ArrowLeft, Folder, Play, Trash2, Edit2, FolderOpen, Check, X, Zap, Camera } from 'lucide-react';

interface VideoFile {
  id: string;
  name: string;
  path: string;
  size: number;
  lastModified: number;
}

interface VideoPlayerPublicPageProps {
  onBack: () => void;
}

const VideoPlayerPublicPage: React.FC<VideoPlayerPublicPageProps> = ({ onBack }) => {
  const [recordings, setRecordings] = useState<VideoFile[]>([]);
  const [currentVideo, setCurrentVideo] = useState<VideoFile | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFolderSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    const videoFiles: VideoFile[] = [];
    const videoExtensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
      
      if (videoExtensions.includes(extension)) {
        videoFiles.push({
          id: `${file.name}-${file.lastModified}`,
          name: file.name,
          path: URL.createObjectURL(file),
          size: file.size,
          lastModified: file.lastModified
        });
      }
    }

    setRecordings(videoFiles);
    // Auto-select first video if available
    if (videoFiles.length > 0) {
      setCurrentVideo(videoFiles[0]);
    }
  };

  const handleDeleteVideo = (videoId: string) => {
    const updatedRecordings = recordings.filter(video => video.id !== videoId);
    setRecordings(updatedRecordings);
    
    // If current video was deleted, select first available or null
    if (currentVideo?.id === videoId) {
      setCurrentVideo(updatedRecordings.length > 0 ? updatedRecordings[0] : null);
    }
  };

  const handleRenameStart = (video: VideoFile) => {
    setEditingId(video.id);
    setEditingName(video.name);
  };

  const handleRenameConfirm = () => {
    if (editingId && editingName.trim()) {
      const updatedRecordings = recordings.map(video =>
        video.id === editingId
          ? { ...video, name: editingName.trim() }
          : video
      );
      setRecordings(updatedRecordings);
      
      // Update current video if it's being renamed
      if (currentVideo?.id === editingId) {
        setCurrentVideo({ ...currentVideo, name: editingName.trim() });
      }
    }
    setEditingId(null);
    setEditingName('');
  };

  const handleRenameCancel = () => {
    setEditingId(null);
    setEditingName('');
  };

  const handlePlayVideo = (video: VideoFile) => {
    setCurrentVideo(video);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (timestamp: number): string => {
    return new Date(timestamp).toLocaleDateString();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex items-center space-x-4">
            <button
              onClick={onBack}
              className="bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-sm border border-slate-600/50 p-3 rounded-xl transition-all duration-200 hover:scale-105"
            >
              <ArrowLeft className="w-5 h-5 text-slate-300" />
            </button>
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-3 rounded-xl">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                Video Player
              </h1>
              <p className="text-slate-400 mt-1">Browse and play your recorded videos</p>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Video Player Area */}
          <div className="lg:col-span-3">
            <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-600/30 rounded-2xl overflow-hidden">
              <div className="relative aspect-video bg-gradient-to-br from-slate-800 to-slate-900">
                {currentVideo ? (
                  <video
                    key={currentVideo.id}
                    controls
                    className="w-full h-full object-cover"
                    src={currentVideo.path}
                  >
                    Your browser does not support the video tag.
                  </video>
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="text-center">
                      <Camera className="w-20 h-20 text-slate-500 mx-auto mb-6" />
                      <h3 className="text-xl font-semibold text-slate-300 mb-2">
                        No Video Selected
                      </h3>
                      <p className="text-slate-400">
                        {recordings.length === 0 
                          ? "Load a folder to start playing videos" 
                          : "Select a video from the library to play"}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
              
            {/* Video Info */}
            <div className="mt-6 bg-slate-800/30 backdrop-blur-sm border border-slate-600/30 rounded-2xl p-6">
              {currentVideo ? (
                <>
                  <h3 className="text-lg font-semibold text-slate-200 mb-2">{currentVideo.name}</h3>
                  <div className="flex items-center space-x-4 text-slate-400">
                    <span>{formatFileSize(currentVideo.size)}</span>
                    <span>•</span>
                    <span>{formatDate(currentVideo.lastModified)}</span>
                  </div>
                </>
              ) : (
                <p className="text-slate-400 text-center">No video playing yet. Pick one from the playlist!</p>
              )}
            </div>
          </div>

          {/* Video Library */}
          <div className="lg:col-span-1">
            <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-600/30 rounded-2xl overflow-hidden">
              <div className="p-6 border-b border-slate-600/30">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-slate-200">
                    Video Library
                  </h3>
                  <span className="text-sm text-slate-400">
                    {recordings.length} videos
                  </span>
                </div>
                
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 hover:scale-105"
                >
                  <FolderOpen className="w-5 h-5" />
                  <span>{recordings.length === 0 ? 'Load Folder' : 'Change Folder'}</span>
                </button>
                
                <input
                  ref={fileInputRef}
                  type="file"
                  webkitdirectory="true"
                  className="hidden"
                  onChange={handleFolderSelect}
                />
              </div>

              {recordings.length === 0 ? (
                <div className="p-6 text-center">
                  <Folder className="w-16 h-16 text-slate-500 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-slate-300 mb-2">No Videos Loaded</h3>
                  <p className="text-slate-400 text-sm">
                    Click "Load Folder" to browse your video files
                  </p>
                </div>
              ) : (
                <div className="max-h-96 overflow-y-auto">
                  {recordings.map((video) => (
                    <div
                      key={video.id}
                      className={`p-4 border-b border-slate-600/30 last:border-b-0 hover:bg-slate-700/30 transition-colors cursor-pointer ${
                        currentVideo?.id === video.id ? 'bg-slate-700/50' : ''
                      }`}
                      onClick={() => handlePlayVideo(video)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          {editingId === video.id ? (
                            <div className="flex items-center space-x-2" onClick={(e) => e.stopPropagation()}>
                              <input
                                type="text"
                                value={editingName}
                                onChange={(e) => setEditingName(e.target.value)}
                                className="flex-1 px-2 py-1 border border-slate-600 rounded bg-slate-800 text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                                onKeyDown={(e) => e.key === 'Enter' && handleRenameConfirm()}
                                autoFocus
                              />
                              <button
                                onClick={handleRenameConfirm}
                                className="p-1 text-green-400 hover:text-green-300 transition-colors"
                              >
                                <Check className="h-4 w-4" />
                              </button>
                              <button
                                onClick={handleRenameCancel}
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

                        {editingId !== video.id && (
                          <div className="flex items-center space-x-1 ml-2" onClick={(e) => e.stopPropagation()}>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handlePlayVideo(video);
                              }}
                              className="p-2 text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 rounded-full transition-colors"
                              title="Play video"
                            >
                              <Play className="h-4 w-4" />
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleRenameStart(video);
                              }}
                              className="p-2 text-slate-400 hover:text-slate-300 hover:bg-slate-500/10 rounded-full transition-colors"
                              title="Rename video"
                            >
                              <Edit2 className="h-4 w-4" />
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteVideo(video.id);
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
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayerPublicPage;