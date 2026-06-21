#!/usr/bin/env python3
"""
MIHI-CN v2.0 - Point d'entrée principal
Combine API REST (configuration) + IPC temps réel
"""

import sys
import asyncio
import threading
import signal
import argparse
import logging
from pathlib import Path

# Ajout du chemin pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.logger import setup_logger
from core.safety_monitor import SafetyMonitor
from core.machine_state import MachinePhase, MachineState
from ipc.low_latency_client import LowLatencyClient
from api.main import app as api_app

logger = setup_logger("main")

class MIHICNController:
    """Contrôleur principal de la machine"""
    
    def __init__(self, mode: str = "shared_memory", api_port: int = 8000):
        self.mode = mode
        self.api_port = api_port
        self.running = False
        
        # Composants
        self.safety_monitor = SafetyMonitor()
        self.state_machine = MachineState()
        self.ipc_client = LowLatencyClient(mode=mode)
        
        # Threads
        self.api_thread = None
        self.main_loop_thread = None
    
    def start(self):
        """Démarre tous les composants"""
        logger.info("🚀 Démarrage de MIHI-CN v2.0")
        
        # 1. Moniteur de sécurité
        self.safety_monitor.start(frequency_hz=100)
        self.safety_monitor.register_callback(self._on_emergency)
        
        # 2. IPC temps réel
        if not self.ipc_client.start():
            logger.error("❌ Échec démarrage IPC")
            return False
        
        # Configuration des callbacks IPC
        self.ipc_client.set_callbacks(
            on_position=self._on_position,
            on_sensor=self._on_sensor,
            on_emergency=self._on_emergency
        )
        
        # 3. API REST (dans un thread séparé)
        self.api_thread = threading.Thread(
            target=self._run_api,
            daemon=True
        )
        self.api_thread.start()
        
        # 4. Machine d'état
        self.state_machine.on_enter(MachinePhase.SCANNING, self._on_enter_scanning)
        self.state_machine.on_enter(MachinePhase.TRACING, self._on_enter_tracing)
        self.state_machine.on_enter(MachinePhase.EMERGENCY_STOP, self._on_enter_emergency)
        
        self.running = True
        
        # 5. Boucle principale
        self._main_loop()
        
        return True
    
    def _run_api(self):
        """Démarre l'API FastAPI"""
        import uvicorn
        logger.info(f"🌐 API REST sur http://localhost:{self.api_port}")
        uvicorn.run(api_app, host="0.0.0.0", port=self.api_port, log_level="warning")
    
    def _main_loop(self):
        """Boucle principale de contrôle"""
        logger.info("🔄 Boucle principale démarrée")
        
        # Simulation d'un cycle complet
        asyncio.run(self._simulate_cycle())
    
    async def _simulate_cycle(self):
        """Simulation d'un cycle de tatouage"""
        
        # Attente de validation
        await self.state_machine.transition_to(MachineState.IDLE, "Machine prête")
        
        # Scan
        await self.state_machine.transition_to(MachineState.SCANNING, "Début scan")
        await asyncio.sleep(1.0)
        
        # IA Processing
        await self.state_machine.transition_to(MachineState.PROCESSING_IA, "IA traitement")
        await asyncio.sleep(0.8)
        
        # Preview
        await self.state_machine.transition_to(MachineState.PREVIEW, "Génération preview")
        await asyncio.sleep(0.5)
        
        # Attente validation (simulée)
        await self.state_machine.transition_to(MachineState.WAITING_VALIDATION, "Attente client")
        await asyncio.sleep(2.0)
        
        # Validation auto pour simulation
        await self.state_machine.transition_to(MachineState.PREPARING, "Validation reçue")
        await asyncio.sleep(5.0)
        
        # Traçage
        await self.state_machine.transition_to(MachineState.TRACING, "Début traçage")
        
        # Simulation de points de trajectoire
        for i in range(100):
            point = {
                'x': i * 0.01,
                'y': 0.5 * (i / 100 - 0.5),
                'z': 0.5,
                'thickness': 0.5,
                'speed': 25,
                'flow': 30,
                'flags': 0
            }
            self.ipc_client.send_trajectory_point(point)
            await asyncio.sleep(0.01)  # 10ms = 100Hz
        
        await asyncio.sleep(1.0)
        
        # Séchage
        await self.state_machine.transition_to(MachineState.DRYING, "Séchage")
        await asyncio.sleep(10.0)
        
        # Contrôle qualité
        await self.state_machine.transition_to(MachineState.QUALITY_CHECK, "Contrôle qualité")
        await asyncio.sleep(2.0)
        
        # Terminé
        await self.state_machine.transition_to(MachineState.COMPLETED, "Cycle terminé")
        
        # Retour au repos
        await asyncio.sleep(3.0)
        await self.state_machine.transition_to(MachineState.IDLE, "Prêt pour prochain client")
    
    def _on_position(self, position: dict):
        """Callback position temps réel"""
        # Envoi vers STM32 via EtherCAT (simulé)
        pass
    
    def _on_sensor(self, sensors: dict):
        """Callback capteurs temps réel"""
        # Mise à jour du moniteur de sécurité
        self.safety_monitor.update_sensors(
            temperature=sensors.get('temperature'),
            pressure=sensors.get('pressure')
        )
    
    def _on_emergency(self, *args):
        """Callback urgence"""
        asyncio.create_task(self.state_machine.emergency_stop("Urgence déclenchée"))
    
    async def _on_enter_scanning(self, old, new):
        logger.info("📷 Démarrage du scan 3D...")
    
    async def _on_enter_tracing(self, old, new):
        logger.info("✍️ Démarrage du traçage...")
    
    async def _on_enter_emergency(self, old, new):
        logger.error("🛑 MODE URGENCE ACTIF - Machine arrêtée")
    
    def stop(self):
        """Arrête le système"""
        logger.info("Arrêt de MIHI-CN...")
        self.running = False
        self.safety_monitor.stop()
        self.ipc_client.stop()
        sys.exit(0)


def signal_handler(signum, frame):
    """Gestionnaire de signaux"""
    logger.info(f"Signal {signum} reçu, arrêt en cours...")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="MIHI-CN v2.0")
    parser.add_argument("--mode", type=str, default="shared_memory",
                        choices=["shared_memory", "zeromq", "unix_socket"],
                        help="Mode de communication IPC")
    parser.add_argument("--api-port", type=int, default=8000,
                        help="Port de l'API REST")
    parser.add_argument("--simulation", action="store_true",
                        help="Mode simulation (sans matériel)")
    
    args = parser.parse_args()
    
    # Enregistrement des signaux
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Démarrage
    controller = MIHICNController(mode=args.mode, api_port=args.api_port)
    
    try:
        controller.start()
    except KeyboardInterrupt:
        controller.stop()
    except Exception as e:
        logger.error(f"Erreur fatale: {e}")
        controller.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()