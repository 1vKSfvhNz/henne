import mmap
import struct
import threading
import time
from typing import Optional, List
from dataclasses import dataclass
import numpy as np
import logging

logger = logging.getLogger(__name__)

@dataclass
class TrajectoryPoint:
    """Point de trajectoire format compact"""
    x: float          # Position X (mm)
    y: float          # Position Y (mm)
    z: float          # Position Z (mm)
    thickness: float  # Épaisseur du trait (mm)
    speed: float      # Vitesse (mm/s)
    flow_rate: float  # Débit (µl/s)
    timestamp_us: int # Timestamp microsecondes
    buse_id: int      # Buse 0-11
    flags: int        # Drapeaux (start=1, end=2, emergency=4)
    
    def to_bytes(self) -> bytes:
        """Convertit en bytes pour mémoire partagée"""
        return struct.pack(
            'ffffffI H B 5x',  # 5x pour padding à 36 bytes
            self.x, self.y, self.z, self.thickness,
            self.speed, self.flow_rate, self.timestamp_us,
            self.buse_id, self.flags
        )
    
    @classmethod
    def from_bytes(cls, data: bytes) -> 'TrajectoryPoint':
        """Crée depuis des bytes"""
        unpacked = struct.unpack('ffffffI H B 5x', data)
        return cls(
            x=unpacked[0], y=unpacked[1], z=unpacked[2],
            thickness=unpacked[3], speed=unpacked[4], flow_rate=unpacked[5],
            timestamp_us=unpacked[6], buse_id=unpacked[7], flags=unpacked[8]
        )


class RingBufferClient:
    """Client de mémoire partagée pour communication temps réel"""
    
    RING_SIZE = 2048  # 2 secondes à 1kHz
    POINT_SIZE = 36   # bytes par point
    HEADER_SIZE = 64   # Bytes pour l'en-tête
    
    def __init__(self, name: str = "mihi_cn_ring"):
        self.name = name
        self.mmap = None
        self._write_index = 0
        self._read_index = 0
        self._running = False
        self._reader_thread = None
    
    def create(self) -> bool:
        """Crée la mémoire partagée (côté serveur)"""
        import posix_ipc
        
        try:
            # Création de la mémoire partagée
            shm = posix_ipc.SharedMemory(self.name, posix_ipc.O_CREAT, size=self._get_total_size())
            self.mmap = mmap.mmap(shm.fd, self._get_total_size())
            
            # Initialisation de l'en-tête
            self._write_index = 0
            self._write_index_ptr = 0
            self._read_index_ptr = 4
            
            # Écriture des index initiaux
            self._atomic_write(0, 0)   # write_index = 0
            self._atomic_write(4, 0)   # read_index = 0
            self._atomic_write(8, 1)   # running = True
            
            logger.info(f"Mémoire partagée créée: {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur création mémoire partagée: {e}")
            return False
    
    def connect(self) -> bool:
        """Connecte à la mémoire partagée existante (côté client)"""
        import posix_ipc
        
        try:
            shm = posix_ipc.SharedMemory(self.name)
            self.mmap = mmap.mmap(shm.fd, self._get_total_size())
            logger.info(f"Connecté à mémoire partagée: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Erreur connexion mémoire partagée: {e}")
            return False
    
    def _get_total_size(self) -> int:
        return self.HEADER_SIZE + (self.RING_SIZE * self.POINT_SIZE)
    
    def _get_point_offset(self, index: int) -> int:
        return self.HEADER_SIZE + (index % self.RING_SIZE) * self.POINT_SIZE
    
    def _atomic_read(self, offset: int, size: int = 4) -> int:
        """Lecture atomique (Python assure l'atomicité pour les reads alignés)"""
        self.mmap.seek(offset)
        data = self.mmap.read(size)
        return struct.unpack('I', data)[0]
    
    def _atomic_write(self, offset: int, value: int):
        """Écriture atomique"""
        self.mmap.seek(offset)
        self.mmap.write(struct.pack('I', value))
        self.mmap.flush()
    
    def write_point(self, point: TrajectoryPoint) -> bool:
        """Écrit un point dans le ring buffer"""
        # Lecture de l'index courant
        write_idx = self._atomic_read(0)
        read_idx = self._atomic_read(4)
        
        next_idx = (write_idx + 1) % self.RING_SIZE
        
        # Vérification buffer plein
        if next_idx == read_idx:
            logger.warning("Ring buffer plein - perte de données")
            return False
        
        # Écriture du point
        offset = self._get_point_offset(write_idx)
        self.mmap.seek(offset)
        self.mmap.write(point.to_bytes())
        
        # Mise à jour de l'index
        self._atomic_write(0, next_idx)
        
        return True
    
    def read_point(self) -> Optional[TrajectoryPoint]:
        """Lit un point depuis le ring buffer"""
        write_idx = self._atomic_read(0)
        read_idx = self._atomic_read(4)
        
        if read_idx == write_idx:
            return None
        
        offset = self._get_point_offset(read_idx)
        self.mmap.seek(offset)
        data = self.mmap.read(self.POINT_SIZE)
        
        point = TrajectoryPoint.from_bytes(data)
        
        # Mise à jour de l'index de lecture
        self._atomic_write(4, (read_idx + 1) % self.RING_SIZE)
        
        return point
    
    def start_reader(self, callback, frequency_hz: int = 1000):
        """Démarre un lecteur en continu"""
        self._running = True
        self._reader_thread = threading.Thread(
            target=self._reader_loop,
            args=(callback, frequency_hz),
            daemon=True
        )
        self._reader_thread.start()
        logger.info(f"Ring buffer reader démarré à {frequency_hz} Hz")
    
    def _reader_loop(self, callback, frequency_hz: int):
        period = 1.0 / frequency_hz
        
        while self._running:
            point = self.read_point()
            if point:
                try:
                    callback(point)
                except Exception as e:
                    logger.error(f"Erreur callback: {e}")
            
            time.sleep(period)
    
    def stop(self):
        """Arrête le lecteur"""
        self._running = False
        if self._reader_thread:
            self._reader_thread.join(timeout=1)
        if self.mmap:
            self.mmap.close()
        logger.info("Ring buffer arrêté")
    
    def get_metrics(self) -> dict:
        """Retourne les métriques du buffer"""
        write_idx = self._atomic_read(0)
        read_idx = self._atomic_read(4)
        
        fill_count = (write_idx - read_idx) % self.RING_SIZE
        
        return {
            "write_index": write_idx,
            "read_index": read_idx,
            "fill_count": fill_count,
            "fill_percent": (fill_count / self.RING_SIZE) * 100,
            "ring_size": self.RING_SIZE
        }


class RingBufferReader:
    """Lecteur simplifié pour la mémoire partagée"""
    
    def __init__(self, ring_buffer: RingBufferClient):
        self.ring = ring_buffer
        self.last_point: Optional[TrajectoryPoint] = None
        self.points_received = 0
        self.last_timestamp = time.time()
    
    def read_latest(self) -> Optional[TrajectoryPoint]:
        """Lit le dernier point disponible"""
        point = self.ring.read_point()
        if point:
            self.last_point = point
            self.points_received += 1
        return point
    
    def get_frequency_hz(self) -> float:
        """Calcule la fréquence de réception"""
        now = time.time()
        elapsed = now - self.last_timestamp
        if elapsed > 0:
            freq = self.points_received / elapsed
            if elapsed > 1.0:
                self.points_received = 0
                self.last_timestamp = now
            return freq
        return 0.0