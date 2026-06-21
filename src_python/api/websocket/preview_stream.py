from fastapi import WebSocket
import asyncio
import json
import logging

class PreviewStreamManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[job_id] = websocket
        logging.info(f"Client {job_id} connecté au stream preview")
    
    async def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]
    
    async def send_update(self, job_id: str, data: dict):
        if job_id in self.active_connections:
            try:
                await self.active_connections[job_id].send_json(data)
            except Exception as e:
                logging.error(f"Erreur d'envoi preview: {e}")
                await self.disconnect(job_id)
    
    async def stream_mesh(self, job_id: str, mesh_data: bytes):
        """Envoie le mesh 3D au client"""
        await self.send_update(job_id, {
            "type": "mesh_update",
            "data": mesh_data.decode('utf-8')  # Simplifié pour l'exemple
        })

preview_manager = PreviewStreamManager()