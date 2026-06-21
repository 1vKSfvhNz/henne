from fastapi import APIRouter
import psutil
import platform
from datetime import datetime

router = APIRouter()

@router.get("/system")
async def system_status():
    """État du système"""
    return {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage("/").percent,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/machine")
async def machine_status():
    """État de la machine MIHI-CN"""
    return {
        "status": "idle",
        "current_zone": None,
        "current_job": None,
        "temperature": 25.0,
        "pressure": 2.0,
        "uptime_seconds": 3600,
        "total_sessions": 42,
        "avg_quality": 93.5
    }

@router.get("/ipc")
async def ipc_status():
    """État de la communication IPC"""
    return {
        "shared_memory": "active",
        "zeromq": "connected",
        "unix_socket": "connected",
        "ethercat": "active",
        "last_packet_us": 120
    }