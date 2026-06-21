import asyncio
import threading
import time
from dataclasses import dataclass
from typing import Optional, Callable, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class EmergencyLevel(Enum):
    NONE = 0
    WARNING = 1
    CRITICAL = 2
    EMERGENCY_STOP = 3

@dataclass
class SafetyEvent:
    level: EmergencyLevel
    source: str
    message: str
    timestamp: float

class SafetyMonitor:
    """Moniteur de sécurité temps réel"""
    
    def __init__(self):
        self.emergency_triggered = False
        self.current_level = EmergencyLevel.NONE
        self.events: List[SafetyEvent] = []
        self.callbacks: List[Callable] = []
        
        # Capteurs simulés
        self.capacitive_triggered = False
        self.hand_present = True
        self.current_temp = 25.0
        self.current_pressure = 2.0
        
        # Seuils
        self.MAX_TEMP = 42.0  # °C
        self.MAX_PRESSURE = 4.5  # bar
        self.MIN_HAND_DISTANCE = 5.0  # mm
        
        self._running = False
        self._thread = None
    
    def start(self, frequency_hz: int = 100):
        """Démarre la boucle de surveillance"""
        self._running = True
        self._thread = threading.Thread(target=self._monitoring_loop, args=(frequency_hz,))
        self._thread.daemon = True
        self._thread.start()
        logger.info("SafetyMonitor démarré à {} Hz", frequency_hz)
    
    def stop(self):
        """Arrête la surveillance"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        logger.info("SafetyMonitor arrêté")
    
    def _monitoring_loop(self, frequency_hz: int):
        period = 1.0 / frequency_hz
        
        while self._running:
            self._check_conditions()
            time.sleep(period)
    
    def _check_conditions(self):
        """Vérifie toutes les conditions de sécurité"""
        events = []
        
        # 1. Barre capacitive
        if self.capacitive_triggered:
            events.append(SafetyEvent(
                level=EmergencyLevel.EMERGENCY_STOP,
                source="capacitive_bar",
                message="Barre capacitive déclenchée - contact détecté",
                timestamp=time.time()
            ))
        
        # 2. Présence main/pied
        if not self.hand_present:
            events.append(SafetyEvent(
                level=EmergencyLevel.EMERGENCY_STOP,
                source="hand_detection",
                message="Main/pied retiré de la zone de travail",
                timestamp=time.time()
            ))
        
        # 3. Température excessive
        if self.current_temp > self.MAX_TEMP:
            events.append(SafetyEvent(
                level=EmergencyLevel.CRITICAL,
                source="temperature",
                message=f"Température excessive: {self.current_temp:.1f}°C > {self.MAX_TEMP}°C",
                timestamp=time.time()
            ))
        
        # 4. Pression excessive
        if self.current_pressure > self.MAX_PRESSURE:
            events.append(SafetyEvent(
                level=EmergencyLevel.CRITICAL,
                source="pressure",
                message=f"Pression excessive: {self.current_pressure:.1f} bar",
                timestamp=time.time()
            ))
        
        # Traitement des événements
        for event in events:
            self.events.append(event)
            
            if event.level == EmergencyLevel.EMERGENCY_STOP:
                self._trigger_emergency_stop(event)
            elif event.level == EmergencyLevel.CRITICAL:
                self._handle_critical(event)
            else:
                logger.warning(f"Sécurité: {event.message}")
    
    def _trigger_emergency_stop(self, event: SafetyEvent):
        """Déclenche l'arrêt d'urgence"""
        if not self.emergency_triggered:
            self.emergency_triggered = True
            self.current_level = EmergencyLevel.EMERGENCY_STOP
            logger.error(f"⚠️ ARRÊT URGENCE ⚠️: {event.message}")
            
            for callback in self.callbacks:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Erreur callback urgence: {e}")
    
    def _handle_critical(self, event: SafetyEvent):
        """Gère une condition critique (pas encore arrêt total)"""
        self.current_level = EmergencyLevel.CRITICAL
        logger.warning(f"⚠️ Critique: {event.message}")
    
    def reset(self):
        """Réinitialise l'état d'urgence"""
        self.emergency_triggered = False
        self.current_level = EmergencyLevel.NONE
        logger.info("Système de sécurité réinitialisé")
    
    def update_sensors(self, capacitive: bool = None, hand_present: bool = None,
                       temperature: float = None, pressure: float = None):
        """Met à jour les valeurs des capteurs"""
        if capacitive is not None:
            self.capacitive_triggered = capacitive
        if hand_present is not None:
            self.hand_present = hand_present
        if temperature is not None:
            self.current_temp = temperature
        if pressure is not None:
            self.current_pressure = pressure
    
    def register_callback(self, callback: Callable):
        """Enregistre une fonction appelée en cas d'urgence"""
        self.callbacks.append(callback)
    
    def is_safe(self) -> bool:
        """Retourne True si la machine peut fonctionner"""
        return not self.emergency_triggered and self.current_level != EmergencyLevel.EMERGENCY_STOP