"""État de la machine - thread-safe"""

import threading
from enum import Enum
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

from ..config.settings import ZONES, SIMULATION_MODE
from ..utils.logger import get_logger

logger = get_logger("machine_state")


class MachinePhase(Enum):
    IDLE = "idle"
    SCANNING = "scanning"
    PROCESSING_IA = "processing_ia"
    PREVIEW = "preview"
    WAITING_VALIDATION = "waiting_validation"
    PREPARING = "preparing"
    TRACING = "tracing"
    DRYING = "drying"
    QUALITY_CHECK = "quality_check"
    FINISHED = "finished"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class TrajectoryPoint:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    thickness: float = 0.5
    speed: float = 25.0
    flow_rate: float = 30.0
    pressure: float = 2.0
    buse_id: int = 0


class MachineState:
    """État central de la machine (thread-safe)"""
    
    def __init__(self):
        self._lock = threading.RLock()
        
        # Phase
        self._phase = MachinePhase.IDLE
        
        # Zone
        self._current_zone = "avant_bras"
        self._zone_params = ZONES.get(self._current_zone, ZONES["avant_bras"])
        
        # Motif
        self._motif_path: Optional[str] = None
        self._motif_svg: Optional[str] = None
        
        # Trajectoire
        self._trajectory: List[TrajectoryPoint] = []
        self._trajectory_index = 0
        self._trace_progress = 0.0
        self._estimated_duration = 70.0  # secondes
        
        # Position temps réel
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0
        self.current_pressure = 2.0
        self.current_flow = 0.0
        self.current_temperature = 25.0
        
        # Session
        self._current_job_id: Optional[str] = None
        self._start_time: Optional[datetime] = None
        
        # Qualité
        self._quality_score = 0.0
        
        logger.info(f"MachineState initialisé - zone: {self._current_zone}")
    
    # ========== Phase ==========
    def get_phase(self) -> MachinePhase:
        with self._lock:
            return self._phase
    
    def set_phase(self, phase: MachinePhase):
        with self._lock:
            self._phase = phase
            logger.info(f"Phase changée: {phase.value}")
    
    # ========== Zone ==========
    def get_current_zone(self) -> str:
        with self._lock:
            return self._current_zone
    
    def set_zone(self, zone: str):
        with self._lock:
            if zone in ZONES:
                self._current_zone = zone
                self._zone_params = ZONES[zone]
                logger.info(f"Zone changée: {zone} - params: {self._zone_params}")
            else:
                logger.warning(f"Zone inconnue: {zone}")
    
    def get_zone_params(self) -> dict:
        with self._lock:
            return self._zone_params.copy()
    
    # ========== Motif ==========
    def set_motif(self, path: str, svg_content: str = None):
        with self._lock:
            self._motif_path = path
            self._motif_svg = svg_content
            logger.info(f"Motif chargé: {path}")
    
    def get_motif(self) -> Optional[str]:
        with self._lock:
            return self._motif_path
    
    # ========== Trajectoire ==========
    def set_trajectory(self, trajectory: List[TrajectoryPoint]):
        with self._lock:
            self._trajectory = trajectory
            self._trajectory_index = 0
            self._trace_progress = 0.0
            logger.info(f"Trajectoire chargée: {len(trajectory)} points")
    
    def get_trajectory(self) -> List[TrajectoryPoint]:
        with self._lock:
            return self._trajectory.copy()
    
    def get_next_trajectory_point(self) -> Optional[TrajectoryPoint]:
        with self._lock:
            if self._trajectory_index < len(self._trajectory):
                point = self._trajectory[self._trajectory_index]
                self._trajectory_index += 1
                return point
            return None
    
    def reset_trajectory(self):
        with self._lock:
            self._trajectory_index = 0
            self._trace_progress = 0.0
    
    # ========== Progression ==========
    def get_trace_progress(self) -> float:
        with self._lock:
            return self._trace_progress
    
    def set_trace_progress(self, progress: float):
        with self._lock:
            self._trace_progress = min(100.0, max(0.0, progress))
    
    def get_estimated_duration(self) -> float:
        with self._lock:
            return self._estimated_duration
    
    def set_estimated_duration(self, duration: float):
        with self._lock:
            self._estimated_duration = duration
    
    # ========== Position temps réel ==========
    def update_position(self, x: float, y: float, z: float):
        self.current_x = x
        self.current_y = y
        self.current_z = z
    
    def get_position(self) -> tuple:
        return (self.current_x, self.current_y, self.current_z)
    
    # ========== Session ==========
    def start_session(self, job_id: str):
        with self._lock:
            self._current_job_id = job_id
            self._start_time = datetime.now()
            self._quality_score = 0.0
            logger.info(f"Session démarrée: {job_id}")
    
    def end_session(self, quality_score: float = None):
        with self._lock:
            if quality_score:
                self._quality_score = quality_score
            duration = (datetime.now() - self._start_time).total_seconds() if self._start_time else 0
            logger.info(f"Session terminée: {self._current_job_id}, durée: {duration:.1f}s, qualité: {self._quality_score}")
            return {"job_id": self._current_job_id, "duration": duration, "quality": self._quality_score}
    
    def get_quality_score(self) -> float:
        with self._lock:
            return self._quality_score
    
    # ========== Réinitialisation ==========
    def reset(self):
        with self._lock:
            self._phase = MachinePhase.IDLE
            self._trajectory = []
            self._trajectory_index = 0
            self._trace_progress = 0.0
            self._current_job_id = None
            self._start_time = None
            logger.info("MachineState réinitialisé")
    
    # ========== Utilitaires ==========
    def to_dict(self) -> dict:
        with self._lock:
            return {
                "phase": self._phase.value,
                "zone": self._current_zone,
                "zone_params": self._zone_params,
                "progress": self._trace_progress,
                "position": {"x": self.current_x, "y": self.current_y, "z": self.current_z},
                "pressure": self.current_pressure,
                "temperature": self.current_temperature,
                "quality": self._quality_score,
                "has_trajectory": len(self._trajectory) > 0
            }