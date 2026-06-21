import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
from pathlib import Path
import cv2
import open3d as o3d

class Scan3DDataset(Dataset):
    """Dataset pour l'entraînement de PointNet"""
    
    def __init__(self, data_dir: Path, num_points=5000, transform=None):
        self.data_dir = data_dir
        self.num_points = num_points
        self.transform = transform
        self.samples = []
        
        # Charger toutes les images et leurs meshes correspondants
        for zone_dir in data_dir.iterdir():
            zone_name = zone_dir.name
            for img_path in zone_dir.glob("*.png"):
                # Chercher le mesh correspondant
                mesh_path = img_path.with_suffix('.ply')
                if mesh_path.exists():
                    self.samples.append({
                        'image': img_path,
                        'mesh': mesh_path,
                        'zone': zone_name
                    })
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        # Charger l'image
        img = cv2.imread(str(sample['image']))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (640, 480)) / 255.0
        img = torch.FloatTensor(img).permute(2, 0, 1)  # (C, H, W)
        
        # Charger le mesh
        mesh = o3d.io.read_triangle_mesh(str(sample['mesh']))
        points = np.asarray(mesh.vertices)
        
        # Échantillonner N points
        if len(points) > self.num_points:
            indices = np.random.choice(len(points), self.num_points, replace=False)
            points = points[indices]
        else:
            # Padding si moins de points
            pad = self.num_points - len(points)
            points = np.vstack([points, np.zeros((pad, 3))])
        
        # Normaliser
        points = (points - points.mean(axis=0)) / points.std(axis=0)
        
        # Encoder la zone
        zone_map = {'main': 0, 'pied': 1, 'avant_bras': 2, 'jambe': 3}
        zone_label = zone_map.get(sample['zone'], 0)
        
        return {
            'image': img,
            'points': torch.FloatTensor(points),
            'zone': torch.LongTensor([zone_label])
        }