import zmq
import json
import threading
import time
import numpy as np
from typing import Dict, Any, Callable

class ZeroMQPublisher:
    """Version Python de ZeroMQ pour communication rapide"""
    
    def __init__(self):
        self.context = zmq.Context()
        self.socket = None
        self.running = False
        self.thread = None
    
    def start(self, port: int = 5556, protocol: str = "tcp"):
        """Démarre le publisher"""
        self.socket = self.context.socket(zmq.PUB)
        
        if protocol == "ipc":
            endpoint = "ipc:///tmp/mihi_cn.ipc"
        else:
            endpoint = f"tcp://*:{port}"
        
        self.socket.bind(endpoint)
        self.socket.set_hwm(1000)  # High water mark
        print(f"✅ ZeroMQ Publisher démarré sur {endpoint}")
    
    def publish_binary(self, topic: str, data: bytes):
        """Envoi binaire ultra-rapide"""
        self.socket.send_multipart([topic.encode(), data], zmq.NOBLOCK)
    
    def publish_json(self, topic: str, data: Dict[str, Any]):
        """Envoi JSON (plus lent mais pratique)"""
        json_str = json.dumps(data, separators=(',', ':'))
        self.publish_binary(topic, json_str.encode())
    
    def publish_trajectory_point(self, point: Dict[str, float]):
        """Envoi d'un point de trajectoire (format binaire compact)"""
        # Format binaire: 4 floats + timestamp (28 bytes)
        import struct
        data = struct.pack(
            "fffff d",
            point.get('x', 0),
            point.get('y', 0),
            point.get('z', 0),
            point.get('thickness', 0.5),
            point.get('speed', 25),
            time.time()
        )
        self.publish_binary("traj", data)
    
    def start_loop(self, frequency_hz: int, callback: Callable):
        """Boucle de publication à haute fréquence"""
        self.running = True
        
        def loop():
            period = 1.0 / frequency_hz
            next_time = time.perf_counter()
            
            while self.running:
                data = callback()
                if data:
                    self.publish_json("sensor", data)
                
                next_time += period
                sleep_time = next_time - time.perf_counter()
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        self.thread = threading.Thread(target=loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        if self.socket:
            self.socket.close()
        self.context.term()


class ZeroMQSubscriber:
    """Client de réception haute performance"""
    
    def __init__(self):
        self.context = zmq.Context()
        self.socket = None
    
    def connect(self, endpoint: str = "tcp://localhost:5556", topics: list = [""]):
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(endpoint)
        
        for topic in topics:
            self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        
        # Timeout pour ne pas bloquer
        self.socket.setsockopt(zmq.RCVTIMEO, 1)
        
        print(f"✅ ZeroMQ Subscriber connecté à {endpoint}")
    
    def receive_non_blocking(self) -> tuple:
        """Réception non-bloquante (retourne (topic, data) ou None)"""
        try:
            topic, data = self.socket.recv_multipart(zmq.NOBLOCK)
            return topic.decode(), data
        except zmq.Again:
            return None