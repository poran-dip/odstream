## Project Setup Instructions (Vite + Flask)

### Cloning the Repository

1. Clone the repository:

```bash
git clone https://github.com/poran-dip/uwod-rc.git
```

2. Navigate into the project directory:

```bash
cd uwod-rc
```

---

### Frontend Setup (React + Vite)

3. Navigate to the frontend directory:

```bash
cd frontend
```

4. Install frontend dependencies:

```bash
npm install
```

5. Start the frontend dev server:

```bash
npm run dev
```

---

### Backend Setup (Flask)

6. Open a separate terminal window/tab and go to the backend directory:

```bash
cd backend
```

7. Create a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate # or source venv/bin/activate on macOS/Linux
```

8. Install Python dependencies:

```bash
pip install -r requirements.txt
```

9. Run the Flask backend:

```bash
python app.py
```

Ensure the Flask server runs on the expected port (typically 5000) and is accessible to the frontend.

---

## Uploading Changes to GitHub

> Make sure you're working on a separate feature branch and pulling latest changes before pushing.

1. Stage changes:

```bash
git add .
```

2. Commit with a descriptive message:

```bash
git commit -m "your commit message"
```

3. Push to the correct branch:

```bash
git push -u origin [your-branch-name]
```

---

## Common Git Commands

### Check current branch:

```bash
git branch
```

### Switch to a different branch:

```bash
git checkout branch-name
```

### Pull latest changes:

```bash
git pull
```

### Add a remote (if not already set):

```bash
git remote add origin https://github.com/poran-dip/uwod-rc.git
```
