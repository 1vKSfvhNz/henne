from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
import aiofiles
from datetime import datetime

router = APIRouter()

class MotifInfo(BaseModel):
    id: str
    name: str
    category: str
    preview_url: str
    estimated_length_cm: float
    usage_count: int

MOTIFS_DIR = "data/motifs/svg"
os.makedirs(MOTIFS_DIR, exist_ok=True)

@router.post("/upload")
async def upload_motif(file: UploadFile = File(...), name: Optional[str] = None, category: str = "general"):
    """Upload d'un nouveau motif SVG"""
    if not file.filename.endswith('.svg'):
        raise HTTPException(400, "Seuls les fichiers SVG sont acceptés")
    
    motif_id = str(uuid.uuid4())[:8]
    filename = f"{motif_id}_{file.filename}"
    filepath = os.path.join(MOTIFS_DIR, filename)
    
    async with aiofiles.open(filepath, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return {
        "id": motif_id,
        "filename": filename,
        "name": name or file.filename,
        "category": category,
        "status": "uploaded"
    }

@router.get("/catalog", response_model=List[MotifInfo])
async def get_catalog(category: Optional[str] = None):
    """Récupère le catalogue des motifs disponibles"""
    # Simulation: motifs prédéfinis
    motifs = [
        MotifInfo(id="mandala_001", name="Mandala Lotus", category="mandalas",
                  preview_url="/previews/mandala_001.png", estimated_length_cm=35, usage_count=42),
        MotifInfo(id="floral_001", name="Fleur d'Arabie", category="floraux",
                  preview_url="/previews/floral_001.png", estimated_length_cm=28, usage_count=38),
        MotifInfo(id="geometric_001", name="Triangles Sacrés", category="geometriques",
                  preview_url="/previews/geometric_001.png", estimated_length_cm=42, usage_count=25),
        MotifInfo(id="bridal_001", name="Mariage Marocain", category="mariage",
                  preview_url="/previews/bridal_001.png", estimated_length_cm=55, usage_count=67),
        MotifInfo(id="ethnic_001", name="Motif Peul", category="ethniques",
                  preview_url="/previews/ethnic_001.png", estimated_length_cm=30, usage_count=19),
    ]
    
    if category:
        motifs = [m for m in motifs if m.category == category]
    
    return motifs

@router.get("/{motif_id}")
async def get_motif(motif_id: str):
    """Récupère un motif spécifique"""
    return {
        "id": motif_id,
        "svg_data": '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">...</svg>',
        "metadata": {
            "width": 100,
            "height": 100,
            "num_paths": 12,
            "estimated_time_seconds": 45
        }
    }

@router.delete("/{motif_id}")
async def delete_motif(motif_id: str):
    """Supprime un motif"""
    # Logique de suppression
    return {"status": "deleted", "id": motif_id}