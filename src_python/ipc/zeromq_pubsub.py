import zmq
import json
import threading
import time
import struct
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class ZeroMQPublisher:
    """Publisher ZeroMQ pour communication haute performance"""
    
    def __init__(self):
        self.context = zmq.Context()
        self.socket = None
        self._running = False
        self._thread = None
        self._callbacks: Dict[str, Callable] = {}
    
    def start(self, port: int = 5556, protocol: str = "tcp") -> bool:
        """Démarre le publisher"""
        self.socket = self.context.socket(zmq.PUB)
        
        if protocol == "ipc":
            endpoint = f"ipc:///tmp/mihi_cn_{port}.ipc"
        elif protocol == "tcp":
            endpoint = f"tcp://*:{port}"
        else:
            endpoint = f"inproc://{port}"
        
        try:
            self.socket.bind(endpoint)
            self.socket.set_hwm(1000)  # High water mark
            self._running = True
            logger.info(f"ZeroMQ Publisher démarré sur {endpoint}")
            return True
        except Exception as e:
            logger.error(f"Erreur démarrage ZeroMQ: {e}")
            return False
    
    def publish_binary(self, topic: str, data: bytes):
        """Envoi binaire ultra-rapide"""
        if self.socket and self._running:
            try:
                self.socket.send_multipart([topic.encode(), data], zmq.NOBLOCK)
            except zmq.ZMQError as e:
                if e.errno != zmq.EAGAIN:
                    logger.error(f"Erreur envoi ZeroMQ: {e}")
    
    def publish_json(self, topic: str, data: Dict[str, Any]):
        """Envoi JSON"""
        json_str = json.dumps(data, separators=(',', ':'))
        self.publish_binary(topic, json_str.encode())
    
    def publish_trajectory_point(self, point: Dict[str, float]):
        """Envoi format binaire compact (28 bytes)"""
        data = struct.pack(
            'fffffd',
            point.get('x', 0.0),
            point.get('y', 0.0),
            point.get('z', 0.0),
            point.get('thickness', 0.5),
            point.get('speed', 25.0),
            point.get('flow', 30.0),
            time.time()
        )
        self.publish_binary('traj', data)
    
    def publish_sensors(self, sensors: Dict[str, float]):
        """Envoi des données capteurs"""
        data = struct.pack(
            'fffff',
            sensors.get('pressure', 2.0),
            sensors.get('temperature', 25.0),
            sensors.get('humidity', 50.0),
            sensors.get('x', 0.0),
            sensors.get('y', 0.0)
        )
        self.publish_binary('sensors', data)
    
    def start_loop(self, frequency_hz: int, callback: Callable):
        """Boucle de publication périodique"""
        def loop():
            period = 1.0 / frequency_hz
            next_time = time.perf_counter()
            
            while self._running:
                data = callback()
                if data:
                    if isinstance(data, dict):
                        self.publish_json('data', data)
                    elif isinstance(data, bytes):
                        self.publish_binary('data', data)
                
                next_time += period
                sleep_time = next_time - time.perf_counter()
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()
        logger.info(f"Boucle publication démarrée à {frequency_hz} Hz")
    
    def stop(self):
        """Arrête le publisher"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        if self.socket:
            self.socket.close()
        self.context.term()
        logger.info("ZeroMQ Publisher arrêté")


class ZeroMQSubscriber:
    """Subscriber ZeroMQ haute performance"""
    
    def __init__(self):
        self.context = zmq.Context()
        self.socket = None
        self._running = False
        self._thread = None
        self.topics: List[str] = []
        self.message_handlers: Dict[str, Callable] = {}
        self.binary_handlers: Dict[str, Callable] = {}
    
    def connect(self, endpoint: str = "tcp://localhost:5556", topics: List[str] = None):
        """Connecte le subscriber"""
        self.socket = self.context.socket(zmq.SUB)
        
        try:
            self.socket.connect(endpoint)
            
            # Souscription aux topics
            topics = topics or [""]
            for topic in topics:
                self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
            
            # Timeout pour non-bloquant
            self.socket.setsockopt(zmq.RCVTIMEO, 10)
            
            logger.info(f"ZeroMQ Subscriber connecté à {endpoint}")
            return True
        except Exception as e:
            logger.error(f"Erreur connexion ZeroMQ: {e}")
            return False
    
    def start(self):
        """Démarre la réception"""
        self._running = True
        self._thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._thread.start()
        logger.info("ZeroMQ Subscriber démarré")
    
    def _receive_loop(self):
        while self._running:
            try:
                topic, data = self.socket.recv_multipart(zmq.NOBLOCK)
                topic_str = topic.decode()
                
                # Appel du handler correspondant
                if topic_str in self.message_handlers:
                    try:
                        if topic_str == 'traj' and len(data) == 28:
                            # Données binaires
                            unpacked = struct.unpack('fffffd', data)
                            self.message_handlers[topic_str]({
                                'x': unpacked[0], 'y': unpacked[1], 'z': unpacked[2],
                                'thickness': unpacked[3], 'speed': unpacked[4],
                                'flow': unpacked[5], 'timestamp': unpacked[6]
                            })
                        elif topic_str == 'sensors' and len(data) == 20:
                            unpacked = struct.unpack('fffff', data)
                            self.message_handlers[topic_str]({
                                'pressure': unpacked[0], 'temperature': unpacked[1],
                                'humidity': unpacked[2], 'x': unpacked[3], 'y': unpacked[4]
                            })
                        else:
                            # Données JSON
                            json_data = json.loads(data.decode())
                            self.message_handlers[topic_str](json_data)
                    except Exception as e:
                        logger.error(f"Erreur traitement message {topic_str}: {e}")
                        
            except zmq.Again:
                pass  # Pas de message
            except Exception as e:
                logger.error(f"Erreur réception ZeroMQ: {e}")
            
            time.sleep(0.0001)  # 100µs pour ne pas saturer le CPU
    
    def on_message(self, topic: str, handler: Callable):
        """Enregistre un handler pour un topic"""
        self.message_handlers[topic] = handler
    
    def stop(self):
        """Arrête le subscriber"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        if self.socket:
            self.socket.close()
        self.context.term()
        logger.info("ZeroMQ Subscriber arrêté")