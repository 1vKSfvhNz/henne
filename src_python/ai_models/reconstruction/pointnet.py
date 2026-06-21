import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
from pathlib import Path

class PointNetPlusPlus(nn.Module):
    """PointNet++ pour reconstruction 3D à partir d'images depth/RGB"""
    
    def __init__(self, num_points=5000, num_classes=4):
        super(PointNetPlusPlus, self).__init__()
        self.num_points = num_points
        
        # Encodage des points
        self.mlp1 = nn.Sequential(
            nn.Conv1d(3, 64, 1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Conv1d(64, 128, 1),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Conv1d(128, 256, 1),
            nn.BatchNorm1d(256),
            nn.ReLU(),
        )
        
        # Caractéristiques globales
        self.global_pool = nn.AdaptiveMaxPool1d(1)
        
        # Decoder pour reconstruction du mesh
        self.decoder = nn.Sequential(
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Linear(512, 1024),
            nn.ReLU(),
            nn.Linear(1024, num_points * 3),  # Sortie: x,y,z
        )
        
        # Segmentation (zones à éviter)
        self.segmentation_head = nn.Sequential(
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, num_classes),  # 4 zones: main, pied, etc.
        )
        
    def forward(self, x):
        # x: (batch, 3, num_points) - nuage de points
        x = self.mlp1(x)  # (batch, 256, num_points)
        
        # Caractéristiques globales
        global_features = self.global_pool(x)  # (batch, 256, 1)
        global_features = global_features.squeeze(-1)  # (batch, 256)
        
        # Reconstruction
        mesh_flat = self.decoder(global_features)  # (batch, num_points*3)
        mesh = mesh_flat.view(-1, self.num_points, 3)  # (batch, num_points, 3)
        
        # Segmentation
        segmentation = self.segmentation_head(global_features)  # (batch, num_classes)
        
        return mesh, segmentation

class ScanDataset(Dataset):
    """Dataset pour les scans 3D"""
    
    def __init__(self, data_dir: Path, transform=None):
        self.data_dir = data_dir
        self.transform = transform
        self.samples = []
        
        # Charger les fichiers
        for zone_dir in data_dir.iterdir():
            zone_name = zone_dir.name
            for file in zone_dir.glob("*.npy"):
                self.samples.append({
                    'path': file,
                    'zone': zone_name
                })
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        # Charger le nuage de points
        point_cloud = np.load(sample['path'])
        # Normaliser
        point_cloud = (point_cloud - point_cloud.mean(axis=0)) / point_cloud.std(axis=0)
        
        # Encoder la zone (one-hot)
        zone_labels = {
            'main': 0, 'pied': 1, 'avant_bras': 2, 'jambe': 3
        }
        label = zone_labels.get(sample['zone'], 0)
        
        return {
            'points': torch.FloatTensor(point_cloud).transpose(0, 1),  # (3, num_points)
            'label': torch.LongTensor([label])
        }