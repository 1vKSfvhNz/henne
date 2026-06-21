"""ZeroMQ Bridge - Communication distribuée avec latence 30-50µs"""

import zmq
import json
import threading
import time
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass
import struct

from ..utils.logger import get_logger

logger = get_logger("zeromq_bridge")

@dataclass
class SensorData:
    """Données capteurs compactes (28 bytes)"""
    x: float
    y: float
    z: float
    pressure: float
    flow: float
    temperature: float
    timestamp: float
    
    def pack(self) -> bytes:
        return struct.pack("fffffff", 
            self.x, self.y, self.z, 
            self.pressure, self.flow, self.temperature,
            self.timestamp
        )
    
    @classmethod
    def unpack(cls, data: bytes) -> 'SensorData':
        values = struct.unpack("fffffff", data)
        return cls(*values)


class ZeroMQBridge:
    """
    Pont ZeroMQ pour communication ultra-rapide
    - PUB/SUB pour diffusion
    - PUSH/PULL pour workload distribution
    - PAIR pour communication bidirectionnelle
    """
    
    def __init__(self):
        self.context = zmq.Context()
        self.pub_socket = None
        self.sub_socket = None
        self.push_socket = None
        self.pull_socket = None
        self.pair_socket = None
        
        self.running = False
        self._thread = None
    
    # ========== PUBLISHER (diffusion) ==========
    def start_publisher(self, port: int = 5556, protocol: str = "tcp"):
        """Démarre un publisher broadcast"""
        self.pub_socket = self.context.socket(zmq.PUB)
        
        if protocol == "ipc":
            endpoint = "ipc:///tmp/mihi_cn_pub.ipc"
        else:
            endpoint = f"tcp://*:{port}"
        
        self.pub_socket.bind(endpoint)
        self.pub_socket.set_hwm(1000)  # High water mark
        logger.info(f"ZeroMQ Publisher démarré sur {endpoint}")
        return endpoint
    
    def publish_binary(self, topic: str, data: bytes):
        """Publication binaire ultra-rapide"""
        if self.pub_socket:
            self.pub_socket.send_multipart([topic.encode(), data], zmq.NOBLOCK)
    
    def publish_json(self, topic: str, data: Dict[str, Any]):
        """Publication JSON (plus lent)"""
        self.publish_binary(topic, json.dumps(data, separators=(',', ':')).encode())
    
    def publish_sensor(self, sensor: SensorData):
        """Publication dédiée aux capteurs (format binaire)"""
        self.publish_binary("sensor", sensor.pack())
    
    def publish_trajectory_point(self, point: Dict[str, float]):
        """Publication point de trajectoire (28 bytes)"""
        data = struct.pack("ffff", 
            point.get('x', 0), point.get('y', 0), 
            point.get('z', 0), point.get('thickness', 0.5)
        )
        self.publish_binary("traj", data)
    
    # ========== SUBSCRIBER ==========
    def start_subscriber(self, endpoint: str, topics: list = None):
        """Démarre un subscriber"""
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.connect(endpoint)
        
        if topics is None:
            topics = [""]
        for topic in topics:
            self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        
        self.sub_socket.setsockopt(zmq.RCVTIMEO, 1)  # Non-bloquant
        logger.info(f"ZeroMQ Subscriber connecté à {endpoint}")
    
    def receive_non_blocking(self) -> tuple:
        """Réception non-bloquante - retourne (topic, data) ou None"""
        if not self.sub_socket:
            return None
        
        try:
            topic, data = self.sub_socket.recv_multipart(zmq.NOBLOCK)
            return topic.decode(), data
        except zmq.Again:
            return None
    
    # ========== PUSH/PULL (work distribution) ==========
    def start_push(self, endpoint: str):
        """Démarre un push socket (envoi de tâches)"""
        self.push_socket = self.context.socket(zmq.PUSH)
        self.push_socket.connect(endpoint)
        logger.info(f"ZeroMQ PUSH connecté à {endpoint}")
    
    def start_pull(self, port: int = 5557):
        """Démarre un pull socket (réception de tâches)"""
        self.pull_socket = self.context.socket(zmq.PULL)
        self.pull_socket.bind(f"tcp://*:{port}")
        logger.info(f"ZeroMQ PULL démarré sur port {port}")
    
    def push_task(self, task_data: bytes):
        """Envoie une tâche"""
        if self.push_socket:
            self.push_socket.send(task_data, zmq.NOBLOCK)
    
    def pull_task(self) -> Optional[bytes]:
        """Récupère une tâche (non-bloquant)"""
        if self.pull_socket:
            try:
                return self.pull_socket.recv(zmq.NOBLOCK)
            except zmq.Again:
                pass
        return None
    
    # ========== PAIR (bidirectionnel, plus rapide) ==========
    def start_pair_server(self, path: str = "ipc:///tmp/mihi_cn_pair.ipc"):
        """Démarre un serveur PAIR (bidirectionnel, ultra-rapide)"""
        self.pair_socket = self.context.socket(zmq.PAIR)
        self.pair_socket.bind(path)
        logger.info(f"ZeroMQ PAIR server sur {path}")
    
    def start_pair_client(self, path: str = "ipc:///tmp/mihi_cn_pair.ipc"):
        """Connecte un client PAIR"""
        self.pair_socket = self.context.socket(zmq.PAIR)
        self.pair_socket.connect(path)
        logger.info(f"ZeroMQ PAIR client connecté à {path}")
    
    def pair_send(self, data: bytes):
        """Envoi via PAIR"""
        if self.pair_socket:
            self.pair_socket.send(data, zmq.NOBLOCK)
    
    def pair_recv(self) -> Optional[bytes]:
        """Réception via PAIR (non-bloquant)"""
        if self.pair_socket:
            try:
                return self.pair_socket.recv(zmq.NOBLOCK)
            except zmq.Again:
                pass
        return None
    
    # ========== Boucle de forwarding ==========
    def start_forwarding(self, from_socket, to_socket):
        """Forward les messages d'un socket à l'autre"""
        self.running = True
        self._thread = threading.Thread(target=self._forward_loop, 
                                         args=(from_socket, to_socket),
                                         daemon=True)
        self._thread.start()
    
    def _forward_loop(self, from_sock, to_sock):
        zmq.proxy(from_sock, to_sock)
    
    def stop(self):
        self.running = False
        for sock in [self.pub_socket, self.sub_socket, self.push_socket, 
                     self.pull_socket, self.pair_socket]:
            if sock:
                sock.close()
        self.context.term()