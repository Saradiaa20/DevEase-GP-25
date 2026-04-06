# How to Run DevEase (Code Complexity Analysis)

**Windows setup guide** (macOS/Linux commands noted where different)

This guide walks you through running both parts of **DevEase**: the FastAPI backend and the Vite + React frontend.

## Components Overview

1. **FastAPI backend** — Port **8000** (code analysis, auth, ML complexity, technical debt)
2. **React frontend (Vite)** — Port **5173** by default (dashboard UI; Vite may use **5174** if 5173 is busy)

---

## First-time setup on Windows (normal PC)

If this is your first time running a dev project on Windows, do this **once** before the steps below.

### 1. Open a terminal

Use any of these (all work):

- Press **Win**, type **PowerShell**, open **Windows PowerShell** or **Terminal**
- Or **Command Prompt** (`cmd`)
- In **Cursor / VS Code**: **Terminal → New Terminal** (usually PowerShell)

### 2. Install Python **3.12** (not 3.13 for this project)

1. Open **https://www.python.org/downloads/** and download **Python 3.12.x** for Windows (64-bit installer).
2. Run the installer.
3. **Important:** Check **“Add python.exe to PATH”** at the bottom of the first screen, then click **Install Now**.
4. Close the installer when it finishes.

**Check that it works** (new terminal window):

```powershell
py -3.12 --version
```

You should see `Python 3.12.x`. If `py` is not found, try:

```powershell
python --version
```

If you only see **Python 3.13**, install **3.12** from python.org and use **`py -3.12`** for this project (see backend steps). This repo’s pinned `pandas` stack is unreliable on **3.13**.

### 3. Install Node.js (includes `npm`)

1. Open **https://nodejs.org/** and download the **LTS** version for Windows.
2. Run the installer; accept the defaults (includes **npm** and adds Node to PATH).
3. Restart the terminal or open a **new** one.

**Check:**

```powershell
node -v
npm -v
```

You should see version numbers (e.g. `v22.x.x` and `10.x.x`).

### 4. (Optional) Install Git

Only if you need to clone or pull the repo:

- **https://git-scm.com/download/win** — install with default options.

### 5. Put the project in a simple folder (recommended)

Avoid very long paths or heavy **OneDrive** sync on the project folder if you get **EPERM** or file-lock errors during `npm install`. Example:

- `C:\Users\YourName\DevEase-Test` or `C:\dev\DevEase-Test`

### 6. PowerShell: “running scripts is disabled” (venv activation)

If activating the venv gives an error about **execution policy** when you run `.\.venv\Scripts\Activate.ps1`:

**Option A — use Command Prompt instead** for that session:

```cmd
cd C:\Users\sarad\Downloads\DevEase-Test\backend
.venv\Scripts\activate.bat
```

**Option B — allow scripts for your user** (PowerShell **as Administrator** is not always required; try without first):

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try `.\.venv\Scripts\Activate.ps1` again.

---

## Prerequisites (summary)

- **Python 3.11 or 3.12** (recommended). **Avoid Python 3.13** unless you upgrade pinned packages: `pandas==2.1.3` may fail to install on 3.13.
- **Node.js LTS** with **npm** (see first-time setup above).
- Optional: **Git** to clone or update the project.

---

## Step-by-Step Instructions

### Step 1: Start the FastAPI backend

1. **Open a terminal** (PowerShell or Command Prompt).

2. **Go to the backend folder** (change the path if your project lives elsewhere):
   ```powershell
   cd C:\Users\sarad\Downloads\DevEase-Test\backend
   ```

3. **Create and activate a virtual environment** (recommended):
   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   You should see `(.venv)` in your prompt.  
   **Command Prompt (`cmd`):** use `py -3.12 -m venv .venv` then `.venv\Scripts\activate.bat` (see [First-time setup on Windows](#first-time-setup-on-windows-normal-pc) if activation fails).

4. **Install Python dependencies:**
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

5. **If you see errors about `email-validator` or Pydantic email fields:**
   ```powershell
   python -m pip install "pydantic[email]"
   ```

6. **Start the API server:**
   ```powershell
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

7. **Verify it is running:**
   - You should see Uvicorn listening on `http://127.0.0.1:8000`
   - Open: `http://127.0.0.1:8000/api/health`
   - You should see JSON with `"status": "healthy"` (or similar)

**Keep this terminal open.**

**Note:** The first startup can be **slow** because optional **TensorFlow** may load for design-pattern detection. Wait until Uvicorn prints that it is running.

---

### Step 2: Start the React frontend

1. **Open a new terminal** (leave the backend running).

2. **Go to the frontend folder:**
   ```powershell
   cd C:\Users\sarad\Downloads\DevEase-Test\frontend
   ```

3. **Install dependencies** (first time or after `package.json` changes):
   ```powershell
   npm install
   ```

4. **Start the dev server:**
   ```powershell
   npm run dev
   ```

5. **Verify it is running:**
   - Vite prints something like: `Local: http://localhost:5173/` (or **5174** if 5173 is in use)
   - Open that URL in your browser

**Keep this terminal open.**

---

## Quick Start Commands Summary

### Terminal 1 — Backend
```powershell
cd C:\Users\sarad\Downloads\DevEase-Test\backend
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 — Frontend
```powershell
cd C:\Users\sarad\Downloads\DevEase-Test\frontend
npm run dev
```

---

## Configuration

### API URL (frontend → backend)

By default the frontend calls **`http://localhost:8000`**.

To override, create `frontend/.env` (or `.env.local`):

```env
VITE_API_URL=http://127.0.0.1:8000
```

Restart `npm run dev` after changing env vars.

---

## Using DevEase

1. Open the frontend URL (e.g. `http://localhost:5173`).
2. Use **Register** / **Login** if your build exposes auth (JWT is stored in `localStorage` as `auth_token`).
3. Upload or analyze code via the dashboard; analysis hits the backend on port **8000**.

---

## Troubleshooting

### Windows (first-time issues)

**`python` opens the Microsoft Store or is not found:**  
Install Python from **python.org**, and enable **“Add python.exe to PATH”**. Close and reopen the terminal. Use **`py -3.12`** to pick version 3.12.

**PowerShell: “cannot be loaded because running scripts is disabled”** when running `Activate.ps1`:  
Use **Command Prompt** and `backend\.venv\Scripts\activate.bat`, or run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` once (see [First-time setup on Windows](#first-time-setup-on-windows-normal-pc)).

**`py -3.12` not found:**  
Reinstall Python 3.12 from python.org and enable **py launcher** (default in installer).

### Backend

**`pip install` fails on `pandas` / `metadata-generation-failed`:**  
Use **Python 3.12** (or 3.11), recreate `.venv`, and run `pip install -r requirements.txt` again.

**Port 8000 already in use (Windows):**
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Import / `email-validator` errors:**  
`python -m pip install "pydantic[email]"`

**Slow or hanging first import:**  
Caused by TensorFlow loading from `design_pattern_detector`. Wait, or consider lazy-loading TensorFlow only when needed (code change).

### Frontend

**Port 5173 already in use:**  
Vite usually picks **5174** automatically. Use the URL shown in the terminal.

**`Failed to resolve import` for `recharts`, `react-dropzone`, `@heroicons/react`:**  
From `frontend`:
```powershell
npm install recharts react-dropzone @heroicons/react
```

**EPERM / file lock errors during `npm install` (often with OneDrive):**  
Close dev servers and editors using the folder, pause OneDrive sync for the project, or move the repo to a non-synced path (e.g. `C:\dev\DevEase-Test`) and run `npm install` again.

**CORS:**  
Backend allows broad origins in development. If you change hosts/ports, ensure `VITE_API_URL` matches the backend URL.

### General

**401 Unauthorized:**  
Log in again; token may be expired. Clear `localStorage` for the site if needed.

**Network errors in the browser:**  
Confirm the backend is running and the URL matches `VITE_API_URL` / default `http://localhost:8000`.

---

## Stopping the servers

In each terminal, press **Ctrl+C**.

Suggested order:

1. Frontend (Ctrl+C)
2. Backend (Ctrl+C)

---

## Verification checklist

Before relying on the app:

- [ ] Backend responds at `http://127.0.0.1:8000/api/health`
- [ ] Frontend loads at the URL Vite prints (e.g. `http://localhost:5173`)
- [ ] Browser devtools **Network** tab shows API calls going to `http://localhost:8000` (or your `VITE_API_URL`)
- [ ] Python **3.11/3.12** venv used for backend installs

---

## macOS / Linux quick notes

- Activate venv: `source .venv/bin/activate`
- Backend same: `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
- Free a port: `lsof -i :8000` then `kill -9 <PID>`

---

## Need help?

- Check the terminal running **Uvicorn** for Python tracebacks
- Check the browser **Console** (F12) and **Network** tab for failed requests
- Confirm `backend/requirements.txt` installed without errors and `frontend/package.json` dependencies are installed (`npm install`)
