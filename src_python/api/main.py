from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
from datetime import datetime

from .routes import scan, motif, job, preview, calibration, session
from ..db.database import init_db
from ..utils.logger import setup_logger

app = FastAPI(
    title="MIHI-CN v2.0 API",
    description="API pour la machine à tatouage henné IA",
    version="2.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(scan.router, prefix="/api/v1/scan", tags=["scan"])
app.include_router(motif.router, prefix="/api/v1/motif", tags=["motif"])
app.include_router(job.router, prefix="/api/v1/job", tags=["job"])
app.include_router(preview.router, prefix="/api/v1/preview", tags=["preview"])
app.include_router(calibration.router, prefix="/api/v1/calibration", tags=["calibration"])
app.include_router(session.router, prefix="/api/v1/session", tags=["session"])

# Gestion des WebSockets
@app.websocket("/ws/preview/{job_id}")
async def websocket_preview(websocket: WebSocket, job_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Traiter le stream
            await websocket.send_text(f"Preview data for job {job_id}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.on_event("startup")
async def startup_event():
    await init_db()
    setup_logger()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)