// Recordings page ("ODReplay"): browse, play, rename and delete recordings.
//
// State and behaviour live in hooks/recordings (useRecordings); the UI
// pieces live in components/recordings. This file just lays them out.

import type React from "react";
import Footer from "../components/Footer";
import PageHeader from "../components/PageHeader";
import PathDialog from "../components/recordings/PathDialog";
import RecordingPlayer from "../components/recordings/RecordingPlayer";
import VideoLibrary from "../components/recordings/VideoLibrary";
import ToastDisplay from "../components/ui/ToastDisplay";
import { useRecordings } from "../hooks/recordings/useRecordings";

interface RecordingsPageProps {
  onBack: () => void;
}

const RecordingsPage: React.FC<RecordingsPageProps> = ({ onBack }) => {
  const { library, rename, directory } = useRecordings();

  return (
    <div className="mx-auto max-w-350 px-4 pt-4 sm:px-6 sm:pt-5">
      <PageHeader
        title="ODReplay"
        description="Recorded footage"
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

      {/* Player first; the library sits beside it on wide screens */}
      <main className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1fr)_340px]">
        <RecordingPlayer
          currentVideo={library.currentVideo}
          hasRecordings={library.recordings.length !== 0}
        />

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
      </main>

      <Footer />
    </div>
  );
};

export default RecordingsPage;
