from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import yaml
import os

router = APIRouter()

class MachineConfig(BaseModel):
    zone_type: str = Field(..., description="Type de zone: main/pied/avant_bras/jambe")
    speed_mm_s: float = Field(25.0, ge=5, le=50)
    thickness_mm: float = Field(0.5, ge=0.2, le=1.2)
    pressure_bar: float = Field(2.0, ge=0.5, le=4.0)
    temperature_c: float = Field(25.0, ge=20, le=38)
    drying_time_s: int = Field(10, ge=5, le=20)

class ZoneParams(BaseModel):
    main: MachineConfig = MachineConfig(zone_type="main", speed_mm_s=15, thickness_mm=0.3, pressure_bar=2.2)
    pied: MachineConfig = MachineConfig(zone_type="pied", speed_mm_s=20, thickness_mm=0.5, pressure_bar=2.5)
    avant_bras: MachineConfig = MachineConfig(zone_type="avant_bras", speed_mm_s=35, thickness_mm=0.6, pressure_bar=2.0)
    jambe: MachineConfig = MachineConfig(zone_type="jambe", speed_mm_s=40, thickness_mm=0.8, pressure_bar=1.8)

@router.get("/zones")
async def get_zones_config():
    """Récupère la configuration de toutes les zones"""
    return ZoneParams().dict()

@router.get("/zones/{zone_type}")
async def get_zone_config(zone_type: str):
    """Récupère la configuration d'une zone spécifique"""
    zones = ZoneParams().dict()
    if zone_type not in zones:
        raise HTTPException(404, f"Zone {zone_type} non trouvée")
    return zones[zone_type]

@router.post("/zones/{zone_type}")
async def update_zone_config(zone_type: str, config: MachineConfig):
    """Met à jour la configuration d'une zone"""
    # Ici on pourrait sauvegarder dans un fichier YAML
    return {"status": "updated", "zone": zone_type, "config": config.dict()}

@router.get("/machine")
async def get_machine_config():
    """Récupère la configuration générale de la machine"""
    return {
        "max_speed": 50,
        "max_pressure": 4.0,
        "max_temperature": 38,
        "emergency_stop_enabled": True,
        "simulation_mode": True,
        "communication_mode": "shared_memory"  # shared_memory, zeromq, unix_socket
    }

@router.post("/machine")
async def update_machine_config(config: Dict[str, Any]):
    """Met à jour la configuration générale"""
    # Sauvegarde dans un fichier
    with open("config/machine_config.yaml", "w") as f:
        yaml.dump(config, f)
    return {"status": "updated", "config": config}