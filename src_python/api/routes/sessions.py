from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

router = APIRouter()

class SessionCreate(BaseModel):
    client_name: Optional[str] = None
    zone_type: str
    motif_id: str

class SessionResponse(BaseModel):
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    zone_type: str
    motif_id: str
    quality_score: Optional[float]
    duration_seconds: Optional[float]

sessions_db = []

@router.post("/start")
async def start_session(session: SessionCreate):
    """Démarre une nouvelle session"""
    session_id = str(uuid.uuid4())[:8]
    
    new_session = {
        "session_id": session_id,
        "start_time": datetime.now(),
        "end_time": None,
        "zone_type": session.zone_type,
        "motif_id": session.motif_id,
        "client_name": session.client_name,
        "quality_score": None,
        "duration_seconds": None
    }
    
    sessions_db.append(new_session)
    return {"session_id": session_id, "start_time": new_session["start_time"]}

@router.post("/{session_id}/end")
async def end_session(session_id: str, quality_score: Optional[float] = None):
    """Termine une session"""
    for session in sessions_db:
        if session["session_id"] == session_id:
            session["end_time"] = datetime.now()
            session["quality_score"] = quality_score or 92.5
            session["duration_seconds"] = (session["end_time"] - session["start_time"]).total_seconds()
            return {
                "session_id": session_id,
                "duration_seconds": session["duration_seconds"],
                "quality_score": session["quality_score"]
            }
    
    raise HTTPException(404, "Session non trouvée")

@router.get("/history", response_model=List[SessionResponse])
async def get_history(days: int = 7, limit: int = 50):
    """Récupère l'historique des sessions"""
    cutoff = datetime.now() - timedelta(days=days)
    filtered = [s for s in sessions_db if s["start_time"] > cutoff]
    
    return filtered[-limit:]

@router.get("/stats")
async def get_stats():
    """Statistiques globales"""
    total = len(sessions_db)
    if total == 0:
        return {"total": 0, "avg_quality": 0, "zones": {}}
    
    avg_quality = sum(s.get("quality_score", 0) or 0 for s in sessions_db) / total
    
    zones = {}
    for s in sessions_db:
        zone = s["zone_type"]
        zones[zone] = zones.get(zone, 0) + 1
    
    return {
        "total_sessions": total,
        "avg_quality": round(avg_quality, 1),
        "zones_distribution": zones
    }