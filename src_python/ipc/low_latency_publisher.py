"""Boucle de publication à haute fréquence (1kHz) avec mémoire partagée"""

import time
import threading
import struct
from typing import Optional, Callable
from dataclasses import dataclass

from .shared_memory import SharedMemoryRing, TrajectoryPoint
from .zeromq_bridge import ZeroMQBridge
from .unix_socket import UnixSocketServer, UltraCompactCommand
from ..core.machine_state import MachineState
from ..utils.logger import get_logger

logger = get_logger("low_latency_publisher")


class LowLatencyPublisher:
    """
    Publie les données de contrôle à très haute fréquence
    Utilise Shared Memory (<1µs) + Unix Socket (5µs) + ZeroMQ (30µs)
    """
    
    def __init__(self, frequency_hz: int = 1000):
        self.frequency_hz = frequency_hz
        self.period_s = 1.0 / frequency_hz
        self.running = False
        self._thread = None
        
        # Canaux de communication
        self.shm = SharedMemoryRing()
        self.zmq = ZeroMQBridge()
        self.unix_server = UnixSocketServer()
        
        # Callbacks
        self.on_trajectory_point: Optional[Callable] = None
        
    def start(self, machine_state: MachineState):
        """Démarre la boucle de publication"""
        # 1. Créer la mémoire partagée
        if not self.shm.create():
            logger.error("Impossible de créer la mémoire partagée")
            return False
        
        # 2. Démarrer le serveur Unix socket pour les commandes
        self.unix_server.start()
        
        # 3. Démarrer le publisher ZeroMQ
        self.zmq.start_publisher()
        
        # 4. Démarrer la boucle
        self.running = True
        self._thread = threading.Thread(target=self._loop, args=(machine_state,), daemon=True)
        self._thread.start()
        
        logger.info(f"LowLatencyPublisher démarré à {self.frequency_hz} Hz")
        return True
    
    def _loop(self, machine_state: MachineState):
        """Boucle principale à haute fréquence"""
        next_time = time.perf_counter()
        seq = 0
        
        while self.running:
            start = time.perf_counter()
            
            # 1. Lire l'état courant
            zone = machine_state.get_current_zone()
            phase = machine_state.get_phase()
            progress = machine_state.get_trace_progress()
            
            # 2. Récupérer le prochain point de trajectoire
            point = self._get_next_trajectory_point(machine_state, seq)
            
            if point and phase == "tracing":
                # 3. Écrire dans la mémoire partagée (<1µs)
                point.timestamp_us = int(time.time() * 1_000_000)
                self.shm.write(point)
                
                # 4. Mettre à jour les métriques
                self.shm.update_metrics(
                    x=point.x, y=point.y, z=point.z,
                    pressure=2.0, flow=point.flow_rate                )
                
                # 5. Envoyer via Unix socket (~5µs)
                cmd = UltraCompactCommand(
                    x_um=int(point.x * 1000),
                    y_um=int(point.y * 1000),
                    z_um=int(point.z * 1000),
                    flow=int(point.flow_rate * 100),
                    buse_mask=1 << (point.buse_id % 12),
                    flags=1 if seq == 0 else 0
                )
                self.unix_server.send_command(cmd)
                
                # 6. Publier via ZeroMQ pour monitoring (~30µs)
                if seq % 100 == 0:  # Réduire la charge
                    self.zmq.publish_sensor(
                        self._create_sensor_data(point)
                    )
                
                # 7. Callback si défini
                if self.on_trajectory_point:
                    self.on_trajectory_point(point)
            
            # 8. Mise à jour de la progression
            if phase == "tracing" and point:
                estimated_duration = machine_state.get_estimated_duration()
                if estimated_duration > 0:
                    new_progress = (seq / (self.frequency_hz * estimated_duration)) * 100
                    machine_state.set_trace_progress(min(100, new_progress))
            
            seq += 1
            
            # Timing pour maintenir la fréquence
            elapsed = time.perf_counter() - start
            sleep_time = self.period_s - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                logger.warning(f"Dépassement temps réel: {elapsed*1000:.2f}ms > {self.period_s*1000:.2f}ms")
            
            next_time += self.period_s
    
    def _get_next_trajectory_point(self, machine_state: MachineState, seq: int) -> Optional[TrajectoryPoint]:
        """Récupère le prochain point de trajectoire"""
        trajectory = machine_state.get_trajectory()
        if not trajectory:
            # Générer un point mock
            t = seq * self.period_s
            return TrajectoryPoint(
                x=0.1 * (t % 2 - 1),
                y=0.2 * (t % 1.5 - 0.75),
                z=0.52,
                thickness=0.6,
                speed=35.0,
                flow_rate=30.0,
                buse_id=seq % 12
            )
        
        idx = seq % len(trajectory)
        return trajectory[idx]
    
    def _create_sensor_data(self, point: TrajectoryPoint):
        """Crée les données capteurs pour ZeroMQ"""
        from .zeromq_bridge import SensorData
        return SensorData(
            x=point.x, y=point.y, z=point.z,
            pressure=2.0, flow=point.flow_rate,
            temperature=28.0, timestamp=time.time()
        )
    
    def stop(self):
        """Arrête la boucle"""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        self.shm.close()
        self.unix_server.stop()
        self.zmq.stop()
        logger.info("LowLatencyPublisher arrêté")