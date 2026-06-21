import threading
import time
import struct
from typing import Optional, Callable, Dict, Any
from collections import deque
import logging
from .ring_buffer import RingBufferClient, TrajectoryPoint
from .zeromq_pubsub import ZeroMQPublisher, ZeroMQSubscriber
from .unix_socket import UnixSocketClient

logger = logging.getLogger(__name__)


class LowLatencyClient:
    """
    Client unifié pour communication ultra-rapide.
    Combine Shared Memory, ZeroMQ et Unix Socket selon le besoin.
    """
    
    def __init__(self, mode: str = "shared_memory"):
        """
        mode: "shared_memory" (plus rapide), "zeromq", "unix_socket"
        """
        self.mode = mode
        self.shared_memory = None
        self.zeromq_pub = None
        self.zeromq_sub = None
        self.unix_socket = None
        
        self._running = False
        self._control_thread = None
        self._trajectory_queue = deque(maxlen=2048)
        
        # Callbacks
        self.on_position_callback: Optional[Callable] = None
        self.on_sensor_callback: Optional[Callable] = None
        self.on_emergency_callback: Optional[Callable] = None
        
        # Métriques
        self._last_timestamp = time.time()
        self._points_sent = 0
        self._points_received = 0
        self._latency_samples = deque(maxlen=100)
    
    def start(self) -> bool:
        """Démarre le client selon le mode choisi"""
        
        if self.mode == "shared_memory":
            self.shared_memory = RingBufferClient()
            if self.shared_memory.connect():
                self._start_shared_memory_reader()
                logger.info("LowLatencyClient mode SHARED_MEMORY démarré")
                return True
            else:
                logger.error("Échec connexion mémoire partagée")
                return False
        
        elif self.mode == "zeromq":
            self.zeromq_sub = ZeroMQSubscriber()
            if self.zeromq_sub.connect("tcp://localhost:5556"):
                self.zeromq_sub.on_message("traj", self._on_zmq_trajectory)
                self.zeromq_sub.on_message("sensors", self._on_zmq_sensors)
                self.zeromq_sub.start()
                logger.info("LowLatencyClient mode ZEROMQ démarré")
                return True
            return False
        
        elif self.mode == "unix_socket":
            self.unix_socket = UnixSocketClient()
            if self.unix_socket.connect():
                self.unix_socket.start_receiver(self._on_unix_message)
                logger.info("LowLatencyClient mode UNIX_SOCKET démarré")
                return True
            return False
        
        return False
    
    def _start_shared_memory_reader(self):
        """Démarre le lecteur mémoire partagée"""
        def reader_callback(point: TrajectoryPoint):
            self._points_received += 1
            if self.on_position_callback:
                self.on_position_callback({
                    'x': point.x, 'y': point.y, 'z': point.z,
                    'thickness': point.thickness,
                    'flow': point.flow_rate,
                    'buse': point.buse_id,
                    'flags': point.flags
                })
        
        self.shared_memory.start_reader(reader_callback, frequency_hz=1000)
    
    def _on_zmq_trajectory(self, data: Dict[str, Any]):
        """Handler ZeroMQ pour trajectoire"""
        self._points_received += 1
        if self.on_position_callback:
            self.on_position_callback(data)
    
    def _on_zmq_sensors(self, data: Dict[str, Any]):
        """Handler ZeroMQ pour capteurs"""
        if self.on_sensor_callback:
            self.on_sensor_callback(data)
    
    def _on_unix_message(self, data: bytes):
        """Handler Unix Socket pour messages binaires"""
        if len(data) == 12:  # 3 floats pour position
            x, y, z = struct.unpack('fff', data)
            self._points_received += 1
            if self.on_position_callback:
                self.on_position_callback({'x': x, 'y': y, 'z': z})
        elif len(data) == 4:  # Emergency
            flags = struct.unpack('I', data)[0]
            if flags & 0x04 and self.on_emergency_callback:
                self.on_emergency_callback()
    
    def send_trajectory_point(self, point: Dict[str, float]) -> bool:
        """Envoi d'un point de trajectoire"""
        self._points_sent += 1
        
        if self.mode == "shared_memory" and self.shared_memory:
            traj_point = TrajectoryPoint(
                x=point.get('x', 0.0),
                y=point.get('y', 0.0),
                z=point.get('z', 0.0),
                thickness=point.get('thickness', 0.5),
                speed=point.get('speed', 25.0),
                flow_rate=point.get('flow', 30.0),
                timestamp_us=int(time.time() * 1_000_000),
                buse_id=point.get('buse', 0),
                flags=point.get('flags', 0)
            )
            return self.shared_memory.write_point(traj_point)
        
        elif self.mode == "zeromq" and self.zeromq_pub:
            self.zeromq_pub.publish_trajectory_point(point)
            return True
        
        elif self.mode == "unix_socket" and self.unix_socket:
            data = struct.pack('fff', point.get('x', 0), point.get('y', 0), point.get('z', 0))
            return self.unix_socket.send_command(1, data)
        
        return False
    
    def send_trajectory_batch(self, points: list) -> int:
        """Envoi d'un lot de points (optimisé)"""
        sent = 0
        for point in points:
            if self.send_trajectory_point(point):
                sent += 1
        return sent
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques de performance"""
        elapsed = time.time() - self._last_timestamp
        
        metrics = {
            "mode": self.mode,
            "points_sent": self._points_sent,
            "points_received": self._points_received,
            "send_rate_hz": self._points_sent / elapsed if elapsed > 0 else 0,
            "receive_rate_hz": self._points_received / elapsed if elapsed > 0 else 0,
            "queue_size": len(self._trajectory_queue),
            "latency_us": sum(self._latency_samples) / len(self._latency_samples) if self._latency_samples else 0
        }
        
        # Reset périodique des compteurs
        if elapsed > 1.0:
            self._points_sent = 0
            self._points_received = 0
            self._last_timestamp = time.time()
        
        return metrics
    
    def stop(self):
        """Arrête le client"""
        self._running = False
        
        if self.shared_memory:
            self.shared_memory.stop()
        if self.zeromq_sub:
            self.zeromq_sub.stop()
        if self.unix_socket:
            self.unix_socket.disconnect()
        
        logger.info("LowLatencyClient arrêté")
    
    def set_callbacks(self, on_position=None, on_sensor=None, on_emergency=None):
        """Configure les callbacks"""
        self.on_position_callback = on_position
        self.on_sensor_callback = on_sensor
        self.on_emergency_callback = on_emergency
    
    def emergency_stop(self):
        """Envoi d'une commande d'arrêt d'urgence"""
        if self.mode == "shared_memory" and self.shared_memory:
            # Écrire un point spécial avec flag emergency
            emergency_point = TrajectoryPoint(
                x=0, y=0, z=0, thickness=0, speed=0, flow_rate=0,
                timestamp_us=int(time.time() * 1_000_000), buse_id=0, flags=4
            )
            self.shared_memory.write_point(emergency_point)
        
        elif self.mode == "unix_socket" and self.unix_socket:
            self.unix_socket.send_command(255, b'EMERGENCY')
        
        logger.warning("⚠️ Commande ARRÊT URGENCE envoyée")