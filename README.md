# Underwater Object Detection – Remote Control Interface

A unified control and monitoring interface for an underwater object detection drone, developed as part of the IIT Guwahati internship project (July 2025).

---

## Overview

This system provides a cross-platform GUI to interact with a remotely operated underwater drone equipped with:

- **Intel RealSense camera**
- **NVIDIA Jetson Nano** for ML inference
- **YOLOv8** object detection model

The interface supports real-time control, recording, playback, and Python-based ML workflows, accessible via a modern frontend.

---

## Features

- Live video feed from Jetson or webcam
- Start/Stop recording sessions
- Save videos as `.mp4` with timestamped filenames
- Display and playback saved recordings
- Trigger and display YOLO-based object detection from the frontend
- Frontend/backend integration (Vite + Flask)
- Supports remote backend running on a Jetson Nano via [odstream-remote](https://github.com/poran-dip/odstream-remote)

---

## Tech Stack

| Area             | Tools                         |
| ---------------- | ----------------------------- |
| Frontend         | React (via Vite), TailwindCSS |
| Backend          | Python, Flask                 |
| Remote Backend   | Flask on Jetson Nano          |
| Object Detection | YOLOv8 (Ultralytics)          |
| Hardware Targets | Jetson Nano, RealSense Camera |

---

## Setup

See [git & workflow instructions here](docs/git-setup.md)

---

## Directory Structure (WIP)

```bash
odstream
├── .gitignore           # Self explanatory
├── docs                 # Dev logs, documentation
│   └── git-setup.md     # Project setup and git guide
├── shared
│   └── recordings       # Saved .mp4 files
├── run_app.py           # Desktop launcher (starts backend + frontend)
├── launcher             # Launcher pieces: ui, output, processes, theme
├── backend
│   ├── app.py           # Flask entrypoint
│   ├── camera_manager.py # CameraManager (stitches the camera/ mixins)
│   ├── camera           # model, remote stream, lifecycle, frames, capture, detection log
│   ├── routes           # Flask blueprints
│   │   ├── camera_routes.py # Registers routes/camera/* on the camera blueprint
│   │   └── camera       # control, recording, settings, validation, state
│   ├── config.py        # App / camera / YOLO configuration
│   └── requirements.txt # Backend dependencies
└── frontend
    ├── public           # Favicon, other global assets
    └── src              # Everything app related
        ├── pages        # Route-based pages (thin layouts)
        ├── hooks        # Page state & logic (objectDetection/, recordings/)
        ├── utils        # Helpers; api/ holds the backend API client
        ├── assets       # Assets for components
        └── components   # Reusable UI components
            ├── detection   # ObjectDetection page pieces (+ settings/)
            ├── recordings  # Recordings page pieces
            └── ui       # UI primitives

# Jetson-side remote backend (separate repo)
odstream-remote
├── app.py               # Jetson Flask entrypoint
├── camera_routes.py     # Defines all Flask API endpoints
├── remote_camera.py     # RemoteCameraManager (stitches camera/ mixins)
├── camera               # model, realsense, recording, streaming
└── requirements.txt     # Dependencies for remote backend
```

---

## Roadmap

### Phase 1 – Web App (Vite + Flask)

- [x] Vite + Tailwind frontend
- [x] Video source selection dropdown
- [x] Live camera feed display
- [x] Recording and saving `.mp4` files
- [x] Playback for saved videos
- [x] Stream from Jetson Nano
- [x] Jetson connection settings in modal

### Phase 2 – Detection Pipeline

- [x] Flask API to run YOLOv8 inference
- [x] Detection overlay on live stream
- [x] Toggle detection from frontend

### Phase 3 – Deployment & Polish

- [x] Auto-deploy scripts for Jetson + host
- [x] LAN streaming support (MJPEG)
- [x] Basic mobile responsiveness

---

## Contributors

- [**Poran Dip**](https://github.com/poran-dip) (primary developer)
- [**Ruhan Roushan Islam**](https://github.com/roushan-ruhan) (multi-model integration)
- [**Pooja Basumatary**](https://www.linkedin.com/in/pooja-basumatary-8a322a361/) (testing & presentation)

**Mentors:**

- Divya Jyoti (PhD Scholar, EEE, IIT Guwahati)
- Parvez Aziz Boruah (PhD Scholar, CSE, IIT Guwahati)

**Supervisor:**
- Dr. Chayan Bhawal (Professor, EEE, IIT Guwahati)

---

## Notes

- Minimal dependencies, modern stack
- Recording format: `YYYYMMDD-HHMM.mp4` (e.g., `20250704-1315.mp4`)
- Network-based live stream and object detection are now supported

---

> “Build it simple, scale it smart.”
