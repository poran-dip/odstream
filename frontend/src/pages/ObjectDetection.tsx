// Main page: live camera stream with detection, recording and settings.
//
// State and behaviour live in hooks/objectDetection (useObjectDetection);
// the pieces of UI live in components/detection. This file just lays them out.

import { Folder, Settings } from "lucide-react";
import { useNavigate } from "react-router";
import DetectionControls from "../components/detection/DetectionControls";
import DetectionVideo from "../components/detection/DetectionVideo";
import LoadingScreen from "../components/detection/LoadingScreen";
import SourceDropdown from "../components/detection/SourceDropdown";
import StopCameraDialog from "../components/detection/StopCameraDialog";
import SettingsModal from "../components/detection/settings/SettingsModal";
import Footer from "../components/Footer";
import PageHeader from "../components/PageHeader";
import ToastDisplay from "../components/ui/ToastDisplay";
import { useObjectDetection } from "../hooks/objectDetection/useObjectDetection";

const ICON_BUTTON_CLASS =
  "bg-slate-800/50 hover:bg-slate-700/50 backdrop-blur-sm border border-slate-600/50 p-3 rounded-xl transition-all duration-200 hover:scale-105";

function ObjectDetectionPage() {
  const navigate = useNavigate();
  const d = useObjectDetection();
  const { selectedSource, isLoadingSource, sources } = d;

  if (isLoadingSource || !selectedSource) {
    return <LoadingScreen />;
  }

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <PageHeader
          title="ODStream"
          description="Real-time object detection & live streaming"
          rightActions={
            <div className="w-full flex justify-between gap-3">
              {/* Camera Source Dropdown - takes most space */}
              <SourceDropdown
                isOpen={d.showSourceDropdown}
                onToggle={() => d.setShowSourceDropdown(!d.showSourceDropdown)}
                isLoading={isLoadingSource}
                selectedSource={selectedSource}
                sources={sources.getAllSources()}
                onSelect={d.handleSourceChange}
              />

              {/* Settings and Folder buttons container */}
              <div className="flex items-center space-x-3 shrink-0">
                <button
                  type="button"
                  title="Settings"
                  onClick={() => d.setShowSettings(true)}
                  className={ICON_BUTTON_CLASS}
                >
                  <Settings className="w-5 h-5 text-slate-300" />
                </button>
                <button
                  type="button"
                  title="Recordings"
                  onClick={() => navigate("/recordings")}
                  className={ICON_BUTTON_CLASS}
                >
                  <Folder className="w-5 h-5 text-slate-300" />
                </button>
              </div>
            </div>
          }
        />

        {d.toast && (
          <ToastDisplay
            message={d.toast.message}
            type={d.toast.type}
            onClose={() => d.setToast(null)}
          />
        )}

        {/* Stop Camera Confirmation Dialog */}
        {d.showStopConfirmation && (
          <StopCameraDialog
            onCancel={() => d.setShowStopConfirmation(false)}
            onConfirm={d.confirmStopDetection}
          />
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Video Player */}
          <DetectionVideo
            isDetecting={d.isDetecting}
            isRecording={d.isRecording}
            detectionStartTime={d.detectionStartTime}
            imgRef={d.imgRef}
          />

          {/* Controls Panel */}
          <DetectionControls
            isDetecting={d.isDetecting}
            isRecording={d.isRecording}
            loading={d.loading}
            selectedSource={selectedSource}
            onStartCamera={d.startDetection}
            onStopCamera={d.handleStopDetectionClick}
            onStartRecording={d.handleStartRecording}
            onStopRecording={d.handleStopRecording}
            onTakeSnapshot={d.handleTakeSnapshot}
          />
        </div>

        <Footer />

        {/* Settings Modal */}
        {d.showSettings && (
          <SettingsModal
            settings={d.settings}
            setSettings={d.setSettings}
            onSave={d.updateVideoSettings}
            saving={d.loading}
            onClose={() => d.setShowSettings(false)}
            customSources={sources.customSources}
            newSourceName={sources.newSourceName}
            setNewSourceName={sources.setNewSourceName}
            newSourceUrl={sources.newSourceUrl}
            setNewSourceUrl={sources.setNewSourceUrl}
            onAddSource={sources.addCustomSource}
            onDeleteSource={sources.deleteCustomSource}
          />
        )}
      </div>
    </div>
  );
}

export default ObjectDetectionPage;
