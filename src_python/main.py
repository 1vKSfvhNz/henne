#!/usr/bin/env python3
"""Point d'entrée unique pour MIHI-CN v2.0"""

import sys
import asyncio
import argparse
import threading
from pathlib import Path

# Ajout du chemin
sys.path.insert(0, str(Path(__file__).parent))

from src_python.utils.logger import setup_logger
from src_python.ipc.low_latency_publisher import LowLatencyPublisher
from src_python.core.machine_state import MachineState
from src_python.core.job_manager import JobManager
from src_python.hardware.ethercat import EtherCATMaster
from src_python.preview.streaming import PreviewStreamer

logger = setup_logger("main")

def main():
    parser = argparse.ArgumentParser(description="MIHI-CN v2.0")
    parser.add_argument("--mode", choices=["simulation", "realtime", "api_only"], 
                        default="simulation", help="Mode d'exécution")
    parser.add_argument("--api-port", type=int, default=8000, help="Port API FastAPI")
    parser.add_argument("--frequency", type=int, default=1000, help="Fréquence boucle temps réel (Hz)")
    args = parser.parse_args()
    
    logger.info(f"Démarrage MIHI-CN v2.0 en mode {args.mode}")
    
    # Composants partagés
    machine_state = MachineState()
    job_manager = JobManager()
    
    # 1. Démarrer la boucle temps réel (IPC ultra-rapide)
    if args.mode != "api_only":
        publisher = LowLatencyPublisher(frequency_hz=args.frequency)
        publisher.start(machine_state)
        logger.info(f"✅ Boucle temps réel démarrée à {args.frequency} Hz")
    
    # 2. Démarrer l'API FastAPI (lente) dans un thread séparé
    if args.mode in ["simulation", "api_only"]:
        from src_python.api.main import start_api
        api_thread = threading.Thread(target=start_api, args=(args.api_port,), daemon=True)
        api_thread.start()
        logger.info(f"✅ API FastAPI démarrée sur port {args.api_port}")
    
    # 3. Démarrer le streamer preview (WebSocket)
    preview_streamer = PreviewStreamer()
    preview_thread = threading.Thread(target=preview_streamer.start, daemon=True)
    preview_thread.start()
    logger.info("✅ Preview streamer démarré")
    
    # 4. Boucle principale
    try:
        while True:
            import time
            time.sleep(1)
            
            # Affichage des stats périodiquement
            if machine_state.get_trace_progress() % 10 == 0:
                logger.debug(f"Statut: {machine_state.get_phase()}, "
                           f"Pos: ({machine_state.current_x:.2f}, {machine_state.current_y:.2f})")
                
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
    finally:
        if args.mode != "api_only":
            publisher.stop()
        logger.info("MIHI-CN arrêté")

if __name__ == "__main__":
    main()