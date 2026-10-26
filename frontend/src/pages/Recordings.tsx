// Recordings page ("ODReplay"): browse, play, rename and delete recordings.
//
// State and behaviour live in hooks/recordings (useRecordings); the UI
// pieces live in components/recordings. This file just lays them out.

import React from "react";
import ToastDisplay from "../components/ui/ToastDisplay";
import PageHeader from "../components/PageHeader";
import Footer from "../components/Footer";
import PathDialog from "../components/recordings/PathDialog";
import RecordingPlayer from "../components/recordings/RecordingPlayer";
import VideoLibrary from "../components/recordings/VideoLibrary";
import { useRecordings } from "../hooks/recordings/useRecordings";

interface RecordingsPageProps {
  onBack: () => void;
}

const RecordingsPage: React.FC<RecordingsPageProps> = ({ onBack }) => {
  const { library, rename, directory } = useRecordings();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      <div className="max-w-7xl mx-auto p-6 h-full flex flex-col">
        <PageHeader
          title="ODReplay"
          description="Browse and play your recorded videos"
          showBackButton
          onBack={onBack}
        />

        {library.error && (
          <ToastDisplay
            message={library.error}
            type="error"
            onClose={() => library.setError("")}
          />
        )}

        {/* Path Change Dialog */}
        {directory.showPathDialog && (
          <PathDialog
            currentPath={directory.currentPath}
            newPath={directory.newPath}
            setNewPath={directory.setNewPath}
            onCancel={() => directory.setShowPathDialog(false)}
            onConfirm={directory.handlePathChange}
          />
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-stretch flex-1">
          {/* Video Player Area */}
          <RecordingPlayer
            currentVideo={library.currentVideo}
            hasRecordings={library.recordings.length !== 0}
          />

          {/* Video Library */}
          <VideoLibrary
            recordings={library.recordings}
            currentVideo={library.currentVideo}
            currentPath={directory.currentPath}
            loading={library.loading}
            onRefresh={() => library.loadVideos()}
            onChangeDirectory={directory.openPathDialog}
            editingId={rename.editingId}
            editingName={rename.editingName}
            setEditingName={rename.setEditingName}
            onPlay={library.handlePlayVideo}
            onRenameStart={rename.handleRenameStart}
            onRenameConfirm={rename.handleRenameConfirm}
            onRenameCancel={rename.handleRenameCancel}
            onDelete={library.handleDeleteVideo}
          />
        </div>

        <Footer />
      </div>
    </div>
  );
};

export default RecordingsPage;
