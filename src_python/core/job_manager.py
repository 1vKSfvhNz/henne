"""Gestionnaire de jobs"""

import uuid
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ..utils.logger import get_logger

logger = get_logger("job_manager")


@dataclass
class Job:
    job_id: str
    zone_type: str
    motif_id: str
    status: str = "pending"  # pending, scanning, processing, preview, tracing, drying, completed, error
    progress: int = 0
    quality_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class JobManager:
    """Gestionnaire de jobs thread-safe"""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._jobs: Dict[str, Job] = {}
        self._current_job_id: Optional[str] = None
        self._history: List[str] = []
    
    def create_job(self, zone_type: str, motif_id: str, metadata: dict = None) -> str:
        """Crée un nouveau job"""
        job_id = str(uuid.uuid4())[:8]
        
        with self._lock:
            job = Job(
                job_id=job_id,
                zone_type=zone_type,
                motif_id=motif_id,
                metadata=metadata or {}
            )
            self._jobs[job_id] = job
            self._current_job_id = job_id
            logger.info(f"Job créé: {job_id} - zone: {zone_type}, motif: {motif_id}")
            return job_id
    
    def get_job(self, job_id: str) -> Optional[Job]:
        with self._lock:
            return self._jobs.get(job_id)
    
    def get_current_job(self) -> Optional[Job]:
        with self._lock:
            if self._current_job_id:
                return self._jobs.get(self._current_job_id)
            return None
    
    def update_status(self, job_id: str, status: str, progress: int = None):
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job.status = status
                if progress is not None:
                    job.progress = progress
                if status == "tracing" and not job.started_at:
                    job.started_at = datetime.now()
                elif status == "completed" and not job.completed_at:
                    job.completed_at = datetime.now()
                logger.debug(f"Job {job_id} status: {status} ({progress}%)")
    
    def update_quality(self, job_id: str, quality_score: float):
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].quality_score = quality_score
                logger.info(f"Job {job_id} qualité: {quality_score}")
    
    def set_error(self, job_id: str, error_message: str):
        with self._lock:
            if job_id in self._jobs:
                self._jobs[job_id].status = "error"
                self._jobs[job_id].error_message = error_message
                logger.error(f"Job {job_id} erreur: {error_message}")
    
    def complete_job(self, job_id: str, quality_score: float = None):
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                job.status = "completed"
                job.completed_at = datetime.now()
                if quality_score:
                    job.quality_score = quality_score
                self._history.append(job_id)
                if self._current_job_id == job_id:
                    self._current_job_id = None
                logger.info(f"Job {job_id} terminé - qualité: {job.quality_score}")
    
    def get_history(self, limit: int = 100) -> List[Job]:
        with self._lock:
            recent = []
            for job_id in self._history[-limit:]:
                recent.append(self._jobs[job_id])
            return recent
    
    def get_stats(self) -> dict:
        with self._lock:
            total = len(self._jobs)
            completed = len([j for j in self._jobs.values() if j.status == "completed"])
            error = len([j for j in self._jobs.values() if j.status == "error"])
            avg_quality = 0
            for j in self._jobs.values():
                if j.quality_score > 0:
                    avg_quality += j.quality_score
            avg_quality = avg_quality / max(1, completed)
            
            return {
                "total_jobs": total,
                "completed": completed,
                "error": error,
                "in_progress": total - completed - error,
                "avg_quality": round(avg_quality, 1)
            }