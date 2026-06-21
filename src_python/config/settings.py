"""Configuration centralisée"""

import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"
MODELS_DIR = BASE_DIR / "models"

# Création des dossiers
for d in [DATA_DIR, LOGS_DIR, MODELS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# IPC (ultra-rapide)
SHARED_MEMORY_NAME = "/mihi_cn_ring"
UNIX_SOCKET_PATH = "/tmp/mihi_cn.sock"
ZEROMQ_PORT = 5556
ZEROMQ_IPC_PATH = "ipc:///tmp/mihi_cn.ipc"

# Boucle temps réel
CONTROL_LOOP_FREQUENCY_HZ = 1000
CONTROL_LOOP_PERIOD_US = 1000000 // CONTROL_LOOP_FREQUENCY_HZ

# API
API_HOST = "0.0.0.0"
API_PORT = 8000

# Preview
PREVIEW_WEBSOCKET_PORT = 8001
PREVIEW_FPS = 30

# Zones
ZONES = {
    "main": {"speed": 15, "thickness": 0.3, "pressure": 2.2, "curvature": 0.8},
    "pied": {"speed": 20, "thickness": 0.5, "pressure": 2.5, "curvature": 0.6},
    "avant_bras": {"speed": 35, "thickness": 0.6, "pressure": 2.0, "curvature": 0.3},
    "jambe": {"speed": 40, "thickness": 0.8, "pressure": 1.8, "curvature": 0.2},
}

# Sécurité
MAX_TEMP_C = 42.0
MAX_PRESSURE_BAR = 3.5
EMERGENCY_STOP_DELAY_MS = 10

# Simulation
SIMULATION_MODE = os.getenv("MIHI_SIMULATION", "1") == "1"