import { io } from 'socket.io-client';
import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom';
import { Settings, Play, Square, Folder, Camera, ChevronDown, Plus, Trash2 } from 'lucide-react'
import ToastDisplay, { type ToastDisplayProps, type ToastType } from '../components/ui/ToastDisplay'
import PageHeader from '../components/PageHeader';
import VideoContainer from '../components/VideoContainer';
import { formatElapsedTime } from '../utils/formatters';
import { detectionApi } from '../utils/api';
import { storageUtils, DEFAULT_SETTINGS, type CameraSource, type VideoSettings } from '../utils/storage';
import { API_BASE_URL, DEFAULT_SOURCES } from '../utils/config';

function ObjectDetectionPage() {
  const [isDetecting, setIsDetecting] = useState<boolean>(false)
  const [loading, setLoading] = useState<boolean>(false)
  const [toast, setToast] = useState<ToastDisplayProps | null>(null)
  const [showSettings, setShowSettings] = useState<boolean>(false)
  const [isRecording, setIsRecording] = useState<boolean>(false)
  const [showSourceDropdown, setShowSourceDropdown] = useState<boolean>(false)
  const [selectedSource, setSelectedSource] = useState<CameraSource | null>(null);
  const [isLoadingSource, setIsLoadingSource] = useState<boolean>(true);
  const [customSources, setCustomSources] = useState<CameraSource[]>([])
  const [newSourceName, setNewSourceName] = useState<string>('')
  const [newSourceUrl, setNewSourceUrl] = useState<string>('')
  const [settings, setSettings] = useState<VideoSettings>(DEFAULT_SETTINGS);
  const [detectionStartTime, setDetectionStartTime] = useState(Number);
  const [showStopConfirmation, setShowStopConfirmation] = useState<boolean>(false);
  
  const imgRef = useRef<HTMLImageElement>(null)
  const navigate = useNavigate()

  const showToast = (message: string, type: ToastType = 'error') => {
    setToast({ message, type })
  }
  
  const findMatchingSource = (backendSource: any, availableSources: CameraSource[]): CameraSource | null => {
    return availableSources.find(src => {
      if (src.type === 'local' && backendSource.type === 'local') {
        return src.index === backendSource.index;
      }
      if (src.type === 'remote' && backendSource.type === 'remote') {
        return src.url === backendSource.url;
      }
      return false;
    }) || null;
  };

  // Load current source from backend on component mount
  useEffect(() => {
    const loadCurrentSource = async () => {
      setIsLoadingSource(true);
      try {
        // First load custom sources so we have the complete list
        const loadedCustomSources = storageUtils.getCustomSources();
        setCustomSources(loadedCustomSources);
        
        const response = await detectionApi.getCameraStatus();
        
        if (response.source) {
          // Find matching source from all available sources (including newly loaded custom ones)
          const allSources = [...DEFAULT_SOURCES, ...loadedCustomSources];
          const matchedSource = findMatchingSource(response.source, allSources);

          if (matchedSource) {
            console.log('Loaded current source from backend:', matchedSource);
            setSelectedSource(matchedSource);
          } else {
            console.warn('Backend source not found in available sources:', response.source);
            console.log('Available sources:', allSources);
            
            // Create a temporary source object if it's not in our predefined list
            // This handles cases where backend has a source not in our DEFAULT_SOURCES
            const tempSource: CameraSource = response.source.type === 'local' 
              ? {
                  id: `temp-local-${response.source.index}`,
                  name: `Camera ${response.source.index}`,
                  type: 'local',
                  index: response.source.index
                }
              : {
                  id: `temp-remote-${Date.now()}`,
                  name: 'Remote Camera',
                  type: 'remote',
                  url: response.source.url
                };
            
            console.log('Using temporary source:', tempSource);
            setSelectedSource(tempSource);
          }
          
          // Also set initial states from the camera status
          setIsDetecting(response.active || false);
          setIsRecording(response.recording || false);
          if (response.active) {
            setDetectionStartTime(Date.now());
          }
        } else {
          console.warn('No source in camera status response, using default');
          setSelectedSource(DEFAULT_SOURCES[0]);
        }

        try {
          const settingsResponse = await detectionApi.getVideoSettings();
          if (settingsResponse.success && settingsResponse.data) {
            setSettings(settingsResponse.data);
          }
        } catch (error) {
          console.error('Error loading video settings:', error);
        }
        
      } catch (error) {
        console.error('Error loading camera status:', error);
        setSelectedSource(DEFAULT_SOURCES[0]);
      } finally {
        setIsLoadingSource(false);
      }
    };

    loadCurrentSource();
  }, []);

  const getAllSources = (): CameraSource[] => {
    return [...DEFAULT_SOURCES, ...customSources]
  }

  const addCustomSource = () => {
    const name = newSourceName.trim()
    const url = newSourceUrl.trim()

    if (!name || !url) {
      return showToast("Name and URL are required", "warning")
    }
    if (!url.includes(".")) return showToast("URL looks wrong?", "warning")

    const newSource = storageUtils.addCustomSource(name, url)
    setCustomSources(prev => [...prev, newSource])
    showToast(`${name} added!`, 'success')
    setNewSourceName('')
    setNewSourceUrl('')
  }

  const deleteCustomSource = (id: string) => {
    const sourceToDelete = customSources.find(source => source.id === id)

    storageUtils.removeCustomSource(id)
    setCustomSources(prev => prev.filter(source => source.id !== id))

    // If the deleted source was selected, switch to webcam
    if (selectedSource?.id === id) {
      setSelectedSource(DEFAULT_SOURCES[0])
    }
    
    const name = sourceToDelete?.name || 'Source'
    showToast(`"${name}" deleted!`, 'success')
  }

  const updateVideoSettings = async (newSettings: Partial<VideoSettings>) => {
    try {
      setLoading(true);
      const response = await detectionApi.updateVideoSettings(newSettings);
      
      if (response.success) {
        showToast('Video settings updated successfully!', 'success');
      } else {
        showToast(response.error || 'Failed to update video settings', 'error');
      }
    } catch (error) {
      console.error('Error updating video settings:', error);
      showToast('Failed to update video settings', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isLoadingSource || !selectedSource) return;

    const newSocket = io(API_BASE_URL.replace('/api', ''));

    newSocket.on('connect', () => {
      console.log('Connected to backend socket');
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from backend socket');
    });

    newSocket.on('camera_status', (data) => {
      console.log('Camera status update:', data);
      
      // Find matching source from all available sources
      const allSources = [...DEFAULT_SOURCES, ...customSources];
      const matchedSource = findMatchingSource(data.source, allSources);

      if (matchedSource && matchedSource.id !== selectedSource?.id) {
        console.log('Backend source changed, updating frontend to match:', matchedSource);
        setSelectedSource(matchedSource);
      } else if (!matchedSource && data.source) {
        // Handle case where backend source is not in our predefined sources
        console.log('Backend using unknown source, creating temporary source:', data.source);
        
        const tempSource: CameraSource = data.source.type === 'local' 
          ? {
              id: `temp-local-${data.source.index}`,
              name: `Camera ${data.source.index}`,
              type: 'local',
              index: data.source.index
            }
          : {
              id: `temp-remote-${Date.now()}`,
              name: 'Remote Camera',
              type: 'remote',
              url: data.source.url
            };
        
        setSelectedSource(tempSource);
      }

      if (data.active) {
        setIsDetecting(true);
        setDetectionStartTime(Date.now());
        
        console.log("Camera active logged");
        
        setTimeout(() => {
          if (imgRef.current) {
            const videoUrl = `${API_BASE_URL}/video_feed`;
            
            console.log("Setting up MJPEG stream:", videoUrl);
            
            imgRef.current.src = videoUrl;
            
            imgRef.current.onload = () => {
              console.log('MJPEG stream connected successfully');
            };
            
            imgRef.current.onerror = (e) => {
              console.error('MJPEG stream error:', e);
              
              setTimeout(() => {
                if (imgRef.current && isDetecting) {
                  console.log("Retrying MJPEG stream connection...");
                  imgRef.current.src = videoUrl;
                }
              }, 2000);
            };
          }
        }, 100);
      } else {
        setIsDetecting(false);
        if (imgRef.current) {
          imgRef.current.src = '';
        }
      }
    });

    newSocket.on('recording_status', (data) => {
      console.log('Recording status update:', data);
      setIsRecording(data.recording);
    });

    newSocket.on('video_settings_updated', (data) => {
      console.log('Video settings update from socket:', data);
      if (data.data) {
        setSettings(prev => ({ ...prev, ...data.data }));
        // Show toast only if it's from another user (you can add logic to detect this)
        if (data.message) {
          showToast(data.message, 'info');
        }
      }
    });

    return () => {
      newSocket.disconnect();
    };
  }, [customSources, selectedSource, isLoadingSource]);

  const startDetection = async () => {
    setLoading(true);
    
    if (!selectedSource) {
      showToast('Unable to start detection: No source was provided', 'error');
      return;
    }

    try {
      const response = await detectionApi.startCamera(selectedSource);
      
      if (response.message && !response.error) {
        console.log('Detection start request sent');
      } else {
        showToast(response.error || response.message || "Something went wrong");
      }
    } catch (err) {
      console.error('Start detection error:', err);
      showToast('Failed to connect to backend');
    } finally {
      setLoading(false);
    }
  };

  const handleStopDetectionClick = () => {
    setShowStopConfirmation(true);
  };

  const confirmStopDetection = async () => {
    setShowStopConfirmation(false);
    setLoading(true);
    
    try {
      await detectionApi.stopCamera();
      // Don't set state here - let the socket event handle it
      console.log('Detection stop request sent');
    } catch (err) {
      console.error('Stop camera error:', err);
      showToast('Failed to stop camera');
    } finally {
      setLoading(false);
    }
  };

  const handleStartRecording = async () => {
    if (!isDetecting) {
      showToast("Please start detection first before recording");
      return;
    }
    
    try {
      setToast(null);
      const response = await detectionApi.startRecording();
      
      if (response.success) {
        // Don't set state here - let the socket event handle it
        console.log('Recording start request sent');
      } else {
        showToast(response.error || "Failed to start recording");
      }
    } catch (error) {
      console.error('Error starting recording:', error);
      showToast("Error starting recording: " + (error instanceof Error ? error.message : String(error)));
    }
  };

  const handleStopRecording = async () => {
    try {
      setToast(null);
      const response = await detectionApi.stopRecording();
      
      if (response.success) {
        console.log('Recording stop request sent');
      } else {
        showToast(response.error || "Failed to stop recording");
      }
    } catch (error) {
      console.error('Error stopping recording:', error);
      showToast("Error stopping recording: " + (error instanceof Error ? error.message : String(error)));
    }
  };

  const handleTakeSnapshot = async () => {
    try {
      const response = await detectionApi.takeSnapshot()
      
      if (response.success) {
        // Show success message or notification
        console.log('Snapshot taken:', response.message);
        showToast("Snapshot taken!", 'success')
      } else {
        showToast(response.error || "Snapshot failed")
        console.error('Snapshot failed:', response.error);
      }
    } catch (error) {
        console.error('Error taking snapshot:', error)
        if (error instanceof Error) {
          showToast("Error taking snapshot: " + error.message);
        } else {
          showToast("Error taking snapshot: " + String(error));
      }
    }
  };
  
  const handleSourceChange = async (source: CameraSource) => {
    setLoading(true);
    try {
      const response = await detectionApi.changeSource(source);

      if (response.success) {
        console.log(response.message ?? 'Camera source changed');
        setToast(null);
        setSelectedSource(source); // Update UI state
        setShowSourceDropdown(false);
        
        setTimeout(() => {
          setIsDetecting(true);
        }, 100);
      } else {
        console.error(response.error ?? response.message)
        showToast(`Failed to change source to ${source.name}`);
      }
    } catch (err) {
      console.error('Change camera source error:', err);
      showToast('Failed to connect to backend');
    } finally {
      setLoading(false);
    }
  };

  if (isLoadingSource || !selectedSource) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 
                      text-white flex items-center justify-center animate-fade-in">
        <div className="text-center space-y-4">
          <div className="relative flex items-center justify-center">
            <div className="absolute animate-ping rounded-full h-16 w-16 bg-blue-500 opacity-50"></div>
            <svg 
              className="h-12 w-12 text-blue-400 animate-pulse" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                    d="M3 5h2l.4 2M7 13h10l1-2H6.4M7 13l1.6 8h6.8l1.6-8M7 13l1-2m3-5h4" />
            </svg>
          </div>
          <p className="text-slate-300 text-lg font-light">
            Initializing camera settings...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <PageHeader 
          title="ODStream"
          description="Real-time object detection & live streaming"
          rightActions={
            <div className="w-full flex justify-between gap-3">
              {/* Camera Source Dropdown - takes most space */}
              <div className="relative flex-1 lg:w-64 min-w-0">
                <button
                  onClick={() => setShowSourceDropdown(!showSourceDropdown)}
                  disabled={isLoadingSource}
                  aria-expanded={showSourceDropdown}
                  className="w-full bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-sm border border-slate-600/50 p-3 rounded-xl transition-all duration-200 hover:scale-105 flex items-center justify-between disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <div className="flex items-center space-x-2 truncate">
                    <Camera className="w-5 h-5 text-slate-300 flex-shrink-0" />
                    <span className="text-sm text-slate-300 truncate">
                      {isLoadingSource ? 'Loading...' : selectedSource?.name || 'Unknown'}
                    </span>
                  </div>
                  <ChevronDown className="w-4 h-4 text-slate-400 flex-shrink-0" />
                </button>
                
                {showSourceDropdown && !isLoadingSource && (
                  <div className="absolute top-full left-0 mt-2 w-full lg:w-64 bg-slate-800/90 backdrop-blur-md border border-slate-600/50 rounded-xl shadow-xl z-10">
                    {getAllSources().map((source) => (
                      <button
                        key={source.id}
                        onClick={() => handleSourceChange(source)}
                        className={`w-full text-left px-4 py-2 text-sm transition-colors first:rounded-t-xl last:rounded-b-xl hover:bg-slate-700/50 ${
                          selectedSource?.id === source.id ? 'bg-blue-600/20 text-blue-300' : 'text-slate-300'
                        }`}
                      >
                        {source.name}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Settings and Folder buttons container */}
              <div className="flex items-center space-x-3 flex-shrink-0">
                <button
                  onClick={() => setShowSettings(true)}
                  className="bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-sm border border-slate-600/50 p-3 rounded-xl transition-all duration-200 hover:scale-105"
                >
                  <Settings className="w-5 h-5 text-slate-300" />
                </button>
                <button
                  onClick={() => navigate('/recordings')}
                  className="bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-sm border border-slate-600/50 p-3 rounded-xl transition-all duration-200 hover:scale-105"
                >
                  <Folder className="w-5 h-5 text-slate-300" />
                </button>
              </div>
            </div>
          }
        />

        {toast && (
          <ToastDisplay
            message={toast.message}
            type={toast.type}
            onClose={() => setToast(null)}
          />
        )}

        {/* Stop Camera Confirmation Dialog */}
        {showStopConfirmation && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-slate-800/90 backdrop-blur-md border border-slate-600/50 rounded-2xl p-6 w-[500px] max-w-[90vw]">
              <h2 className="text-xl font-bold mb-4 text-slate-100">Stop Camera</h2>
              <p className="text-slate-300 mb-6">
                This will stop camera for <strong>EVERY computer</strong> connected to this network. Are you sure you want to proceed?
              </p>
              
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowStopConfirmation(false)}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmStopDetection}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                >
                  Stop Camera
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Video Player */}
          <VideoContainer
            showPlaceholder={!isDetecting}
            placeholderTitle="AI Detection Ready"
            placeholderDescription="Click 'Start Detection' to begin real-time object detection"
            statusIndicators={
              <>
                {isDetecting && (
                  <div className="bg-green-500/20 border border-green-500/50 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-medium text-green-400 animate-pulse">
                    ● RUNNING
                  </div>
                )}
                {isRecording && (
                  <div className="bg-red-500/20 border border-red-500/50 backdrop-blur-sm px-3 py-1 rounded-full text-sm font-medium text-red-400 animate-pulse">
                    ● RECORDING
                  </div>
                )}
              </>
            }
            bottomContent={
              isDetecting ? (
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-200 mb-1">Detection Active</h3>
                    <p className="text-slate-400">Time elapsed: {formatElapsedTime(detectionStartTime)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-slate-400">Objects detected: 0 {/*detectedObjects.length*/}</p>
                    <p className="text-sm text-slate-400">FPS: 0.0 {/*currentFPS*/}</p>
                  </div>
                </div>
              ) : (
                <p className="text-slate-400 text-center">Start detection to view real-time statistics</p>
              )
            }
          >
            <img
              ref={imgRef}
              alt="Video Stream"
              className="w-full h-full object-cover"
            />
          </VideoContainer>

          {/* Controls Panel */}
          <div className="space-y-4">
            {/* Detection Controls */}
            <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-600/30 rounded-2xl p-6">
              <h3 className="text-lg font-semibold mb-4 text-slate-200">Detection Controls</h3>
              
              <div className="space-y-3">
                <button
                  onClick={startDetection}
                  disabled={loading || isDetecting}
                  className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 hover:scale-105 disabled:hover:scale-100"
                >
                  <Play className="w-5 h-5" />
                  <span>{loading ? 'Starting...' : 'Start Camera'}</span>
                </button>
                
                <button
                  onClick={handleStopDetectionClick}
                  disabled={loading || !isDetecting}
                  className="w-full bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold py-3 px-4 rounded-xl transition-all duration-200 flex items-center justify-center space-x-2 hover:scale-105 disabled:hover:scale-100"
                >
                  <Square className="w-5 h-5" />
                  <span>{loading ? 'Stopping...' : 'Stop Camera'}</span>
                </button>
              </div>
            </div>

            {/* Recording Controls */}
            <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-600/30 rounded-2xl p-6">
              <h3 className="text-lg font-semibold mb-4 text-slate-200">Recording</h3>
              
              <button
                onClick={isRecording ? handleStopRecording : handleStartRecording}
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
                onClick={handleTakeSnapshot}
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
              </div>
            </div>
          </div>
        </div>

        {/* Settings Modal */}
        {showSettings && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-slate-800/90 backdrop-blur-md border border-slate-600/50 rounded-2xl p-6 w-[800px] max-w-[90vw] max-h-[80vh] overflow-y-auto">
              <h2 className="text-xl font-bold mb-6 text-slate-100">Settings</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Left Side - Display Settings */}
                <div>
                  <h3 className="text-lg font-semibold mb-4 text-slate-200">Display Settings</h3>
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium mb-2 text-slate-300">Brightness</label>
                      <input
                        type="range"
                        min="-100"
                        max="100"
                        value={settings.brightness}
                        onChange={(e) => {
                          const brightness = parseInt(e.target.value);
                          setSettings(prev => ({ ...prev, brightness }));
                        }}
                        className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                      />
                      <span className="text-sm text-slate-400 mt-1 block">{settings.brightness}</span>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2 text-slate-300">Contrast</label>
                      <input
                        type="range"
                        min="0"
                        max="300"
                        step="10"
                        value={Math.round(settings.contrast * 100)}
                        onChange={(e) => {
                          const contrast = parseInt(e.target.value) / 100;
                          setSettings(prev => ({ ...prev, contrast }));
                        }}
                        className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                      />
                      <span className="text-sm text-slate-400 mt-1 block">{(settings.contrast * 100).toFixed(0)}%</span>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2 text-slate-300">Saturation</label>
                      <input
                        type="range"
                        min="0"
                        max="200"
                        step="10"
                        value={Math.round(settings.saturation * 100)}
                        onChange={(e) => {
                          const saturation = parseInt(e.target.value) / 100;
                          setSettings(prev => ({ ...prev, saturation }));
                        }}
                        className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                      />
                      <span className="text-sm text-slate-400 mt-1 block">{(settings.saturation * 100).toFixed(0)}%</span>
                    </div>
                    
                    <div className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        id="annotateYOLO"
                        checked={true}
                        disabled={true}
                        className="w-4 h-4 text-blue-600 bg-slate-700 border-slate-600 rounded focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                      />
                      <label htmlFor="annotateYOLO" className="text-sm text-slate-400">
                        Enable YOLO Annotations
                      </label>
                    </div>
                  </div>
                </div>

                {/* Right Side - Camera Sources */}
                <div>
                  <h3 className="text-lg font-semibold mb-4 text-slate-200">Camera Sources</h3>
                  
                  {/* Add New Source */}
                  <div className="bg-slate-700/30 rounded-xl p-4 mb-4">
                    <h4 className="text-sm font-medium mb-3 text-slate-300">Add Custom Source</h4>
                    <div className="space-y-3">
                      <input
                        type="text"
                        placeholder="Source name"
                        value={newSourceName}
                        onChange={(e) => setNewSourceName(e.target.value)}
                        className="w-full bg-slate-800/50 border border-slate-600/50 rounded-lg px-3 py-2 text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <input
                        type="url"
                        placeholder="Stream URL"
                        value={newSourceUrl}
                        onChange={(e) => setNewSourceUrl(e.target.value)}
                        className="w-full bg-slate-800/50 border border-slate-600/50 rounded-lg px-3 py-2 text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                      <button
                        onClick={addCustomSource}
                        disabled={!newSourceName.trim() || !newSourceUrl.trim()}
                        className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white py-2 px-4 rounded-lg transition-colors flex items-center justify-center space-x-2"
                      >
                        <Plus className="w-4 h-4" />
                        <span>Add Source</span>
                      </button>
                    </div>
                  </div>

                  {/* Sources List */}
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium text-slate-300">Available Sources</h4>
                    
                    {/* Default Sources */}
                    {DEFAULT_SOURCES.map((source) => (
                      <div key={source.id} className="bg-slate-700/20 rounded-lg p-3 flex items-center justify-between">
                        <div>
                          <div className="font-medium text-slate-200">{source.name}</div>
                          <div className="text-xs text-slate-400 truncate">
                            {source.type === 'local' ? `Device ${source.index}` : source.url}
                          </div>
                        </div>
                        <div className="text-xs text-slate-500 capitalize">{source.type}</div>
                      </div>
                    ))}
                    
                    {/* Custom Sources */}
                    {customSources.map((source) => (
                      <div key={source.id} className="bg-slate-700/20 rounded-lg p-3 flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="font-medium text-slate-200">{source.name}</div>
                          <div className="text-xs text-slate-400 truncate">
                            {source.type === 'local' ? `Device ${source.index}` : source.url}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <div className="text-xs text-slate-500 capitalize">{source.type}</div>
                          <button
                            onClick={() => deleteCustomSource(source.id)}
                            className="text-red-400 hover:text-red-300 transition-colors"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                    
                    {customSources.length === 0 && (
                      <div className="text-center py-4 text-slate-500 text-sm">
                        No custom sources added yet
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="flex justify-between mt-8">
                <button
                  onClick={() => {
                    updateVideoSettings({
                      brightness: settings.brightness,
                      contrast: settings.contrast,
                      saturation: settings.saturation
                    });
                  }}
                  disabled={loading}
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
                >
                  {loading ? 'Saving...' : 'Save Settings'}
                </button>
                <button
                  onClick={() => setShowSettings(false)}
                  className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ObjectDetectionPage