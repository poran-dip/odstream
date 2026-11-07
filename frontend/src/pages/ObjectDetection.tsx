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

function ObjectDetectionPage() {
  const navigate = useNavigate();
  const d = useObjectDetection();
  const { selectedSource, isLoadingSource, sources } = d;

  if (isLoadingSource || !selectedSource) {
    return <LoadingScreen />;
  }

  return (
    <div className="mx-auto max-w-350 px-4 pt-4 sm:px-6 sm:pt-5">
      <PageHeader
        title="ODStream"
        description="Live object detection"
        rightActions={
          <>
            <SourceDropdown
              isOpen={d.showSourceDropdown}
              onToggle={() => d.setShowSourceDropdown(!d.showSourceDropdown)}
              isLoading={isLoadingSource}
              selectedSource={selectedSource}
              sources={sources.getAllSources()}
              onSelect={d.handleSourceChange}
            />
            <button
              type="button"
              title="Settings"
              aria-label="Settings"
              onClick={() => d.setShowSettings(true)}
              className="icon-btn"
            >
              <Settings className="size-5" />
            </button>
            <button
              type="button"
              title="Recordings"
              onClick={() => navigate("/recordings")}
              className="btn-secondary shrink-0 bg-hull px-3"
            >
              <Folder className="size-5" />
              <span className="max-sm:sr-only">Recordings</span>
            </button>
          </>
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

      {/* Video first; the control rail sits beside it on wide screens */}
      <main className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1fr)_300px]">
        <DetectionVideo
          isDetecting={d.isDetecting}
          isRecording={d.isRecording}
          detectionStartTime={d.detectionStartTime}
          currentFps={d.currentFps}
          latencyMs={d.latencyMs}
          detectionCount={d.detectionCount}
          imgRef={d.imgRef}
        />

        <DetectionControls
          isDetecting={d.isDetecting}
          isRecording={d.isRecording}
          loading={d.loading}
          onStartCamera={d.startDetection}
          onStopCamera={d.handleStopDetectionClick}
          onStartRecording={d.handleStartRecording}
          onStopRecording={d.handleStopRecording}
          onTakeSnapshot={d.handleTakeSnapshot}
        />
      </main>

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
  );
}

export default ObjectDetectionPage;
