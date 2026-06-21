"""Unix Domain Socket - Latence 5-10 microsecondes"""

import socket
import struct
import threading
import time
from typing import Optional, Callable
from dataclasses import dataclass

from ..utils.logger import get_logger

logger = get_logger("unix_socket")

# Format compact pour les commandes (16 bytes)
COMMAND_FORMAT = "iii H B B"  # x_int, y_int, z_int, flow, buse_mask, flags
COMMAND_SIZE = struct.calcsize(COMMAND_FORMAT)

@dataclass
class UltraCompactCommand:
    """Commande ultra-compacte - 16 bytes"""
    x_um: int = 0      # Position X en micromètres (int32)
    y_um: int = 0      # Position Y en micromètres
    z_um: int = 0      # Position Z en micromètres
    flow: int = 3000   # Débit en centièmes de µl/s (uint16)
    buse_mask: int = 0xFF  # Bitmask des buses actives (uint8)
    flags: int = 0          # bits: start(1), stop(2), emergency(4)
    
    def pack(self) -> bytes:
        return struct.pack(COMMAND_FORMAT,
            self.x_um, self.y_um, self.z_um,
            self.flow & 0xFFFF,
            self.buse_mask & 0xFF,
            self.flags & 0xFF
        )
    
    @classmethod
    def unpack(cls, data: bytes) -> 'UltraCompactCommand':
        x, y, z, flow, mask, flags = struct.unpack(COMMAND_FORMAT, data)
        return cls(x_um=x, y_um=y, z_um=z, flow=flow, buse_mask=mask, flags=flags)
    
    @property
    def x_mm(self) -> float:
        return self.x_um / 1000.0
    
    @property
    def y_mm(self) -> float:
        return self.y_um / 1000.0
    
    @property
    def z_mm(self) -> float:
        return self.z_um / 1000.0


class UnixSocketServer:
    """Serveur Unix Domain Socket - pour communication locale ultra-rapide"""
    
    def __init__(self, path: str = "/tmp/mihi_cn.sock"):
        self.path = path
        self.sock = None
        self.client_fd = None
        self.running = False
        self._thread = None
        
    def start(self):
        """Démarre le serveur"""
        # Supprimer l'ancien socket
        import os
        try:
            os.unlink(self.path)
        except:
            pass
        
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(self.path)
        self.sock.listen(1)
        
        self.running = True
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()
        
        logger.info(f"Unix socket server démarré sur {self.path}")
    
    def _accept_loop(self):
        while self.running:
            try:
                self.sock.settimeout(0.5)
                client, addr = self.sock.accept()
                self.client_fd = client
                logger.info("Client Unix socket connecté")
                break
            except socket.timeout:
                continue
            except Exception as e:
                logger.error(f"Erreur accept: {e}")
                break
    
    def send_command(self, cmd: UltraCompactCommand) -> bool:
        """Envoie une commande au client"""
        if not self.client_fd:
            return False
        try:
            self.client_fd.send(cmd.pack())
            return True
        except:
            return False
    
    def receive_response(self) -> Optional[bytes]:
        """Reçoit une réponse du client"""
        if not self.client_fd:
            return None
        try:
            self.client_fd.settimeout(0.001)
            return self.client_fd.recv(32)
        except socket.timeout:
            return None
        except:
            return None
    
    def stop(self):
        self.running = False
        if self.client_fd:
            self.client_fd.close()
        if self.sock:
            self.sock.close()
        logger.info("Unix socket server arrêté")


class UnixSocketClient:
    """Client Unix Domain Socket"""
    
    def __init__(self, path: str = "/tmp/mihi_cn.sock"):
        self.path = path
        self.sock = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connecte au serveur"""
        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect(self.path)
            self.connected = True
            logger.info(f"Unix socket client connecté à {self.path}")
            return True
        except Exception as e:
            logger.error(f"Erreur connexion Unix socket: {e}")
            return False
    
    def receive_command(self, timeout_ms: int = 1) -> Optional[UltraCompactCommand]:
        """Reçoit une commande (bloquant avec timeout)"""
        if not self.connected:
            return None
        
        try:
            self.sock.settimeout(timeout_ms / 1000.0)
            data = self.sock.recv(COMMAND_SIZE)
            if len(data) == COMMAND_SIZE:
                return UltraCompactCommand.unpack(data)
        except socket.timeout:
            pass
        except Exception as e:
            logger.error(f"Erreur réception: {e}")
            self.connected = False
        
        return None
    
    def send_response(self, data: bytes) -> bool:
        """Envoie une réponse"""
        if self.connected:
            try:
                self.sock.send(data)
                return True
            except:
                self.connected = False
        return False
    
    def close(self):
        if self.sock:
            self.sock.close()
            self.connected = False