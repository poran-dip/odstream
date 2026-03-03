# Underwater Object Detection – Remote Control Interface

A unified control and monitoring interface for an underwater object detection drone, developed as part of the IIT Guwahati internship project (July 2025).

---

## Overview

This system provides a cross-platform GUI to interact with a remotely operated underwater drone equipped with:

* **Intel RealSense camera**
* **NVIDIA Jetson Nano** for ML inference
* **YOLOv8** object detection model

The interface supports real-time control, recording, playback, and Python-based ML workflows, accessible via a modern frontend.

---

## Features

* Live video feed from Jetson or webcam
* Start/Stop recording sessions
* Save videos as `.mp4` with timestamped filenames
* Display and playback saved recordings
* Trigger and display YOLO-based object detection from the frontend
* Frontend/backend integration (Vite + Flask)
* Supports remote backend running on a Jetson Nano via [uwod-remote](https://github.com/poran-dip/uwod-remote)

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
uwod-rc
├── .gitignore           # Self explanatory
├── docs                 # Dev logs, documentation
│   └── git-setup.md     # Project setup and git guide
├── shared
│   └── recordings       # Saved .mp4 files
├── backend
│   ├── utils            # Python helpers (planned)
│   ├── requirements.txt # Backend dependencies
│   └── app.py           # Flask entrypoint
└── frontend
    ├── public           # Favicon, other global assets
    └── src              # Everything app related
        ├── pages        # Route-based page components
        ├── utils        # Helpers functions (planned)
        ├── assets       # Assets for components
        └── components   # Reusable UI components
            └── ui       # UI primitives

# Jetson-side remote backend (separate repo)
uwod-remote
├── .gitignore           # As per usual
├── app.py               # Jetson Flask entrypoint
├── jetson_camera.py     # Stream handling and detection logic
├── jetson_routes.py     # Defines all Flask API endpoints
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

* [x] Flask API to run YOLOv8 inference
* [x] Detection overlay on live stream
* [x] Toggle detection from frontend

### Phase 3 – Deployment & Polish

* [ ] Auto-deploy scripts for Jetson + host
* [x] LAN streaming support (MJPEG)
* [x] Basic mobile responsiveness

---

## Contributors

* [**Poran Dip**](https://github.com/poran-dip)
* Ruhan Roushan Islam
* Pooja Basumatary

**Mentors:**

* Divya Jyoti (PhD Scholar, EEE, IIT Guwahati)
* Pravez Aziz Baruah (PhD Scholar, CSE, IIT Guwahati)

**Supervisor:**
* Dr. Chayan Bawal (HoD, EEE, IIT Guwahati)

---

## Notes

* Minimal dependencies, modern stack
* Recording format: `YYYYMMDD-HHMM.mp4` (e.g., `20250704-1315.mp4`)
* Network-based live stream and object detection are now supported

---

> “Build it simple, scale it smart.”
