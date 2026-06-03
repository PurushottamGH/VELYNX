# VELYNX

Multi-stack scaffold for VELYNX.

Quickstart

Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

PowerShell users on Windows can avoid the `npm.ps1` execution-policy issue by running the helper from the repo root:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\scripts\start-frontend.ps1
```

Add `-Install` on the first run if dependencies are missing:

```powershell
.\scripts\start-frontend.ps1 -Install
```

See docs/requirements.md for extracted specs from VELYNX Project.pdf.
