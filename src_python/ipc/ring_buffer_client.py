import mmap
import struct
import threading
import numpy as np
from ctypes import Structure, c_float, c_uint32, c_uint16, c_uint8, c_bool
from dataclasses import dataclass
from typing import Optional, Callable

@dataclass
class TrajectoryPoint:
    x: float
    y: float
    z: float
    thickness: float
    speed: float
    flow_rate: float
    timestamp_us: int
    buse_id: int
    flags: int

# Structure C pour correspondre au C++
class TrajectoryPointC(Structure):
    _fields_ = [
        ("x", c_float),
        ("y", c_float),
        ("z", c_float),
        ("thickness", c_float),
        ("speed", c_float),
        ("flow_rate", c_float),
        ("timestamp_us", c_uint32),
        ("buse_id", c_uint16),
        ("flags", c_uint8),
        ("reserved", c_uint8 * 5)
    ]

class RingBufferClient:
    """Client Python pour la mémoire partagée"""
    
    def __init__(self, shm_name="/mihi_cn_ring"):
        self.shm_name = shm_name
        self.shm_fd = None
        self.mmap = None
        self.RING_SIZE = 2048
        self.STRUCT_SIZE = struct.calcsize("ffffffI2sB5s")  # ~36 bytes
        
    def connect(self):
        import posix_ipc
        self.shm_fd = posix_ipc.SharedMemory(self.shm_name)
        self.mmap = mmap.mmap(self.shm_fd.fd, self.RING_SIZE * self.STRUCT_SIZE + 64)
        return True
    
    def write_point(self, point: TrajectoryPoint):
        """Écrit un point dans le ring buffer (depuis Python)"""
        data = struct.pack(
            "ffffffI HB",
            point.x, point.y, point.z, point.thickness,
            point.speed, point.flow_rate, point.timestamp_us,
            point.buse_id, point.flags
        )
        # Calcul de la position (simplifié)
        write_idx = self._get_write_index()
        offset = 64 + (write_idx * self.STRUCT_SIZE)
        self.mmap[offset:offset + self.STRUCT_SIZE] = data
    
    def read_point(self) -> Optional[TrajectoryPoint]:
        """Lit un point depuis le ring buffer (depuis Python)"""
        read_idx = self._get_read_index()
        write_idx = self._get_write_index()
        
        if read_idx == write_idx:
            return None
        
        offset = 64 + (read_idx * self.STRUCT_SIZE)
        data = self.mmap[offset:offset + self.STRUCT_SIZE]
        
        unpacked = struct.unpack("ffffffI HB", data)
        return TrajectoryPoint(
            x=unpacked[0], y=unpacked[1], z=unpacked[2],
            thickness=unpacked[3], speed=unpacked[4], flow_rate=unpacked[5],
            timestamp_us=unpacked[6], buse_id=unpacked[7], flags=unpacked[8]
        )
    
    def _get_write_index(self) -> int:
        return struct.unpack("I", self.mmap[0:4])[0]
    
    def _get_read_index(self) -> int:
        return struct.unpack("I", self.mmap[4:8])[0]
    
    def close(self):
        if self.mmap:
            self.mmap.close()