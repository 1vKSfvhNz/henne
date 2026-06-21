"""Shared Memory Ring Buffer - Latence < 1 microseconde"""

import mmap
import struct
import threading
from dataclasses import dataclass
from typing import Optional
from ctypes import Structure, c_float, c_uint32, c_uint16, c_uint8, c_bool, c_char, CDLL, byref, sizeof

# Formats de structure (compact)
# 36 bytes par point
TRAJECTORY_POINT_FORMAT = "fffff f I H B 5s"
TRAJECTORY_POINT_SIZE = struct.calcsize(TRAJECTORY_POINT_FORMAT)

@dataclass
class TrajectoryPoint:
    """Point de trajectoire - 36 bytes"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    thickness: float = 0.5
    speed: float = 25.0
    flow_rate: float = 30.0
    timestamp_us: int = 0
    buse_id: int = 0
    flags: int = 0  # bit0: start, bit1: stop, bit2: emergency
    
    def pack(self) -> bytes:
        return struct.pack(
            TRAJECTORY_POINT_FORMAT,
            self.x, self.y, self.z, self.thickness,
            self.speed, self.flow_rate,
            self.timestamp_us & 0xFFFFFFFF,
            self.buse_id & 0xFFFF,
            self.flags & 0xFF,
            b'\x00\x00\x00\x00\x00'
        )
    
    @classmethod
    def unpack(cls, data: bytes) -> 'TrajectoryPoint':
        values = struct.unpack(TRAJECTORY_POINT_FORMAT, data)
        return cls(
            x=values[0], y=values[1], z=values[2],
            thickness=values[3], speed=values[4], flow_rate=values[5],
            timestamp_us=values[6], buse_id=values[7], flags=values[8]
        )


class SharedMemoryRing:
    """
    Ring buffer en mémoire partagée
    Latence: < 1µs (sans syscall après le premier mapping)
    """
    
    RING_SIZE = 2048  # 2 secondes à 1kHz
    HEADER_SIZE = 64   # Pour les métadonnées (aligné cache line)
    
    def __init__(self, name: str = "/mihi_cn_ring"):
        self.name = name
        self.total_size = self.HEADER_SIZE + (self.RING_SIZE * TRAJECTORY_POINT_SIZE)
        self.mmap = None
        self._write_lock = threading.Lock()
        self._read_lock = threading.Lock()
    
    def create(self) -> bool:
        """Crée la mémoire partagée (côté serveur)"""
        import posix_ipc
        
        try:
            # Supprimer l'ancienne
            posix_ipc.unlink_shared_memory(self.name)
        except:
            pass
        
        # Créer la mémoire partagée
        shm = posix_ipc.SharedMemory(self.name, posix_ipc.O_CREAT, size=self.total_size)
        shm.close_fd()
        
        # Mapper
        self.mmap = mmap.mmap(-1, self.total_size, shm.name)
        
        # Initialiser l'en-tête
        self._write_index = 0
        self._read_index = 0
        self._write_index_value = 0
        self._read_index_value = 0
        self._update_header()
        
        return True
    
    def open(self) -> bool:
        """Ouvre la mémoire partagée existante (côté client)"""
        import posix_ipc
        
        try:
            shm = posix_ipc.SharedMemory(self.name)
            self.mmap = mmap.mmap(shm.fd, self.total_size)
            shm.close_fd()
            return True
        except Exception as e:
            print(f"Erreur ouverture mémoire partagée: {e}")
            return False
    
    def _update_header(self):
        """Met à jour l'en-tête dans la mémoire"""
        if self.mmap:
            # write_index (4 bytes)
            self.mmap[0:4] = struct.pack("I", self._write_index)
            # read_index (4 bytes)
            self.mmap[4:8] = struct.pack("I", self._read_index)
            # running flag (1 byte)
            self.mmap[8:9] = struct.pack("b", 1)
    
    def _get_write_index(self) -> int:
        return struct.unpack("I", self.mmap[0:4])[0] if self.mmap else 0
    
    def _get_read_index(self) -> int:
        return struct.unpack("I", self.mmap[4:8])[0] if self.mmap else 0
    
    def _set_write_index(self, value: int):
        if self.mmap:
            self.mmap[0:4] = struct.pack("I", value)
    
    def _set_read_index(self, value: int):
        if self.mmap:
            self.mmap[4:8] = struct.pack("I", value)
    
    def write(self, point: TrajectoryPoint) -> bool:
        """Écrit un point - retourne False si buffer plein"""
        with self._write_lock:
            write_idx = self._get_write_index()
            read_idx = self._get_read_index()
            
            next_idx = (write_idx + 1) % self.RING_SIZE
            
            if next_idx == read_idx:
                return False  # Buffer full
            
            offset = self.HEADER_SIZE + (write_idx * TRAJECTORY_POINT_SIZE)
            self.mmap[offset:offset + TRAJECTORY_POINT_SIZE] = point.pack()
            
            self._set_write_index(next_idx)
            return True
    
    def read(self) -> Optional[TrajectoryPoint]:
        """Lit un point - retourne None si buffer vide"""
        with self._read_lock:
            read_idx = self._get_read_index()
            write_idx = self._get_write_index()
            
            if read_idx == write_idx:
                return None  # Buffer empty
            
            offset = self.HEADER_SIZE + (read_idx * TRAJECTORY_POINT_SIZE)
            data = self.mmap[offset:offset + TRAJECTORY_POINT_SIZE]
            
            next_idx = (read_idx + 1) % self.RING_SIZE
            self._set_read_index(next_idx)
            
            return TrajectoryPoint.unpack(data)
    
    def get_metrics(self) -> dict:
        """Retourne les métriques temps réel"""
        if not self.mmap:
            return {}
        
        # Lire les métriques depuis la mémoire (offset 16-64)
        x = struct.unpack("f", self.mmap[16:20])[0] if len(self.mmap) > 20 else 0
        y = struct.unpack("f", self.mmap[20:24])[0] if len(self.mmap) > 24 else 0
        z = struct.unpack("f", self.mmap[24:28])[0] if len(self.mmap) > 28 else 0
        pressure = struct.unpack("f", self.mmap[28:32])[0] if len(self.mmap) > 32 else 0
        flow = struct.unpack("f", self.mmap[32:36])[0] if len(self.mmap) > 36 else 0
        
        return {
            "x": x, "y": y, "z": z,
            "pressure": pressure, "flow": flow,
            "write_index": self._get_write_index(),
            "read_index": self._get_read_index(),
            "buffer_usage": (self._get_write_index() - self._get_read_index()) % self.RING_SIZE
        }
    
    def update_metrics(self, x: float, y: float, z: float, pressure: float, flow: float):
        """Met à jour les métriques temps réel (côté contrôleur)"""
        if self.mmap:
            self.mmap[16:20] = struct.pack("f", x)
            self.mmap[20:24] = struct.pack("f", y)
            self.mmap[24:28] = struct.pack("f", z)
            self.mmap[28:32] = struct.pack("f", pressure)
            self.mmap[32:36] = struct.pack("f", flow)
    
    def close(self):
        if self.mmap:
            self.mmap.close()
            self.mmap = None
    
    def __del__(self):
        self.close()