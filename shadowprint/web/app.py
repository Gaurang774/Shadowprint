"""
Shadowprint FastAPI Web Application.
Serves the web dashboard UI and REST/WebSocket telemetry APIs.
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from shadowprint.web.routes import router

app = FastAPI(
    title="Shadowprint — MCP Server Security Auditor Dashboard",
    description="Live security telemetry, 4-engine auditor, cryptographic baseline diffing, and benchmark scorecard.",
    version="1.0.0",
)

# Enable CORS for local dev servers (e.g. Vite on 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router)

# Locate frontend build directory
STATIC_DIR = Path(__file__).resolve().parent / "dist"
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

dist_dir = STATIC_DIR if STATIC_DIR.exists() else FRONTEND_DIST

if dist_dir.exists() and (dist_dir / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=str(dist_dir / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Allow API routes to pass through
        if full_path.startswith("api/"):
            return None
        file_path = dist_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(dist_dir / "index.html")
else:
    @app.get("/")
    def index():
        return {
            "message": "Shadowprint API is running.",
            "dashboard_ui": "Frontend assets not yet compiled. Run 'npm run build' in frontend/ to generate UI.",
            "docs_url": "/docs",
            "api_status": "/api/status",
        }
