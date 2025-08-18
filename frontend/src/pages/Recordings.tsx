import React, { useState, useEffect, useCallback } from 'react';
import { Folder, Play, Trash2, Edit2, Check, X, RefreshCw, Settings } from 'lucide-react';
import ToastDisplay from '../components/ui/ToastDisplay';
import PageHeader from '../components/PageHeader';
import VideoContainer from '../components/VideoContainer';
import { formatDate, formatFileSize } from '../utils/formatters';
import Footer from '../components/Footer';

interface VideoFile {
  id: string;
  name: string;
  path: string;
  size: number;
  lastModified: number;
}

interface RecordingsPageProps {
  onBack: () => void;
}

const API_BASE_URL = 'http://localhost:5000/api';

const RecordingsPage: React.FC<RecordingsPageProps> = ({ onBack }) => {
  const [recordings, setRecordings] = useState<VideoFile[]>([]);
  const [currentVideo, setCurrentVideo] = useState<VideoFile | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPathDialog, setShowPathDialog] = useState(false);
  const [newPath, setNewPath] = useState('');
  const [currentPath, setCurrentPath] = useState('');

  const loadVideos = useCallback(async (selectVideoId?: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/videos`);
      const data = await response.json();
      
      if (data.success) {
        setRecordings(data.videos);
        // Auto-select video by ID if specified, otherwise first video
        if (data.videos.length > 0) {
          let videoToSelect;
          if (selectVideoId) {
            videoToSelect = data.videos.find((v: VideoFile) => v.id === selectVideoId) || data.videos[0];
          } else {
            videoToSelect = data.videos[0];
          }
          setCurrentVideo(videoToSelect);
        } else {
          setCurrentVideo(null)
        }
      } else {
        setError('Failed to load videos');
      }
    } catch (error) {
      setError('Failed to connect to server. Make sure the Flask backend is running.');
      console.error('Error loading videos:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load videos on component mount
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/config`);
        const data = await response.json();
        if (data.success) {
          setCurrentPath(data.video_path);
        }
      } catch (error) {
        console.error('Error loading config:', error);
      }
    };
    
    loadVideos();
    loadConfig();
  }, [loadVideos]);

  const handleDeleteVideo = async (videoId: string) => {
    if (!confirm('Are you sure you want to delete this video? This action cannot be undone.')) {
      return;
    }

    try {
      // Find the index of the video being deleted
      const deletedIndex = recordings.findIndex(v => v.id === videoId);
      
      // Determine which video to select after deletion
      let videoToSelectAfterDelete: string | undefined;
      if (recordings.length > 1) {
        if (deletedIndex > 0) {
          // Select the video above (previous in list)
          videoToSelectAfterDelete = recordings[deletedIndex - 1].id;
        } else {
          // If deleting the first video, select the next one (which will become first)
          videoToSelectAfterDelete = recordings[deletedIndex + 1].id;
        }
      }
      // If only one video, videoToSelectAfterDelete stays undefined (will select none)

      const response = await fetch(`${API_BASE_URL}/videos/${videoId}/delete`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Reload videos and select the appropriate one
        await loadVideos(videoToSelectAfterDelete);
      } else {
        setError(data.error || 'Failed to delete video');
      }
    } catch (error) {
      setError('Failed to delete video');
      console.error('Error deleting video:', error);
    }
  };

  const handleRenameStart = (video: VideoFile) => {
    setEditingId(video.id);
    setEditingName(video.name);
  };

  const handleRenameConfirm = async () => {
    if (!editingId || !editingName.trim()) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/videos/${editingId}/rename`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          new_name: editingName.trim()
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Reload videos after rename
        await loadVideos(editingId);
        
        // Update current video if it was renamed
        if (currentVideo?.id === editingId) {
          setCurrentVideo(prev => prev ? { ...prev, name: data.new_name, id: data.new_name } : null);
        }
      } else {
        setError(data.error || 'Failed to rename video');
      }
    } catch (error) {
      setError('Failed to rename video');
      console.error('Error renaming video:', error);
    } finally {
      setEditingId(null);
      setEditingName('');
    }
  };

  const handleRenameCancel = () => {
    setEditingId(null);
    setEditingName('');
  };

  const handlePlayVideo = (video: VideoFile) => {
    setCurrentVideo(video);
  };

  const handlePathChange = async () => {
    if (!newPath.trim()) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/config/path`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          path: newPath.trim()
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        setCurrentPath(data.path);
        setShowPathDialog(false);
        setNewPath('');
        // Reload videos from new path
        await loadVideos();
      } else {
        setError(data.error || 'Failed to change path');
      }
    } catch (error) {
      setError('Failed to change path');
      console.error('Error changing path:', error);
    }
  };

  const getVideoUrl = (filename: string): string => {
    return `${API_BASE_URL}/videos/${encodeURIComponent(filename)}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      <div className="max-w-7xl mx-auto p-6 h-full flex flex-col">
        <PageHeader 
          title='ODReplay'
          description='Browse and play your recorded videos'
          showBackButton
          onBack={onBack}
        />

        {error &&
          <ToastDisplay 
            message={error} 
            type='error'
            onClose={() => setError('')}
          />
        }

        {/* Path Change Dialog */}
        {showPathDialog && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-slate-800 border border-slate-600 rounded-2xl p-6 w-full max-w-md">
              <h3 className="text-xl font-semibold mb-4">Change Video Directory</h3>
              <p className="text-sm text-slate-400 mb-4 truncate">
                Currently in: <span className="font-mono text-slate-300">{currentPath}</span>
              </p>
              <input
                type="text"
                value={newPath ?? ''}
                onChange={(e) => setNewPath(e.target.value)}
                placeholder="Enter directory path (e.g., D:/Videos/)"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-xl text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="flex justify-end space-x-3 mt-4">
                <button
                  onClick={() => setShowPathDialog(false)}
                  className="px-4 py-2 text-slate-400 hover:text-slate-300"
                >
                  Cancel
                </button>
                <button
                  onClick={handlePathChange}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl"
                >
                  Change Path
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-stretch flex-1">
          {/* Video Player Area */}
          <VideoContainer
            showPlaceholder={!currentVideo}
            placeholderTitle="No Video Selected"
            placeholderDescription={
              recordings.length === 0 
                ? "Load videos from your directory" 
                : "Select a video from the library to play"
            }
            bottomContent={
              currentVideo ? (
                <>
                  <h3 className="text-lg font-semibold text-slate-200 mb-2 truncate max-w-full">{currentVideo.name}</h3>
                  <div className="flex items-center space-x-4 text-slate-400">
                    <span>{formatFileSize(currentVideo.size)}</span>
                    <span>•</span>
                    <span>{formatDate(currentVideo.lastModified)}</span>
                  </div>
                </>
              ) : (
                <p className="text-slate-400 text-center">No video playing yet. Pick one from the playlist!</p>
              )
            }
          >
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

          {/* Video Library */}
          <div className="lg:col-span-1 flex flex-col h-full">
            <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-600/30 rounded-2xl overflow-hidden h-full flex flex-col">
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
                    onClick={() => loadVideos()}
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 hover:scale-105 disabled:opacity-50"
                  >
                    <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                    <span>{loading ? 'Loading...' : 'Refresh Videos'}</span>
                  </button>
                  
                  <button
                    onClick={() => {
                      setNewPath(currentPath)
                      setShowPathDialog(true)
                    }}
                    className="w-full bg-slate-700 hover:bg-slate-600 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 hover:scale-105"
                  >
                    <Settings className="w-5 h-5" />
                    <span>Change Directory</span>
                  </button>
                </div>
              </div>

              {recordings.length === 0 ? (
                <div className="flex flex-col items-center justify-center text-center h-full p-6">
                  <Folder className="w-16 h-16 text-slate-500 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-slate-300 mb-2">
                    {loading ? 'Loading Videos...' : 'No Videos Found'}
                  </h3>
                  <p className="text-slate-400 text-sm">
                    {loading ? 'Please wait...' : 'Check your directory path or refresh to load videos'}
                  </p>
                </div>
              ) : (
                <div className="max-h-100 h-full overflow-y-auto">
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

        <Footer />
      </div>
    </div>
  );
};

export default RecordingsPage;