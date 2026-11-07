from pathlib import Path

from config import DEFAULT_VIDEO_PATH, VIDEO_EXTENSIONS


class VideoManager:
    def __init__(self, base_path=DEFAULT_VIDEO_PATH):
        self.base_path = Path(base_path)

    def get_video_files(self):
        """Get all video files from the specified directory"""
        videos = []

        if not self.base_path.exists():
            return videos

        try:
            for file_path in self.base_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in VIDEO_EXTENSIONS:
                    stat = file_path.stat()
                    videos.append(
                        {
                            "id": str(file_path.name),
                            "name": file_path.name,
                            "path": str(file_path),
                            "size": stat.st_size,
                            "lastModified": int(
                                stat.st_mtime * 1000
                            ),  # Convert to milliseconds
                        }
                    )
        except Exception as e:
            print(f"Error reading directory: {e}")

        return sorted(videos, key=lambda x: x["lastModified"], reverse=True)

    def rename_video(self, old_name, new_name):
        """Rename a video file"""
        old_path = self.base_path / old_name
        new_path = self.base_path / new_name

        if not old_path.exists():
            return False, "File not found"

        if new_path.exists():
            return False, "A file with that name already exists"

        try:
            old_path.rename(new_path)
            return True, "File renamed successfully"
        except Exception as e:
            return False, f"Error renaming file: {e!s}"

    def delete_video(self, filename):
        """Delete a video file"""
        file_path = self.base_path / filename

        if not file_path.exists():
            return False, "File not found"

        try:
            file_path.unlink()
            return True, "File deleted successfully"
        except Exception as e:
            return False, f"Error deleting file: {e!s}"

    def get_video_path(self, filename):
        """Get the full path of a video file"""
        file_path = self.base_path / filename
        return file_path if file_path.exists() else None
