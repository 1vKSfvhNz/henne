import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from pathlib import Path
import numpy as np
from tqdm import tqdm
from datetime import datetime
import logging

from .pointnet import PointNet
from .dataset import Scan3DDataset

def train_model(
    data_dir: Path = Path("data/raw/scans_3d"),
    epochs: int = 100,
    batch_size: int = 8,
    learning_rate: float = 1e-3,
    num_points: int = 5000,
    save_dir: Path = Path("models/checkpoints")
):
    """Entraîne le modèle PointNet sur les données de scan 3D"""
    
    # 1. Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('training.log'),
            logging.StreamHandler()
        ]
    )
    
    # 2. Préparation des données
    logging.info("Chargement des données...")
    dataset = Scan3DDataset(data_dir, num_points=num_points)
    
    # Split train/val
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset, [train_size, val_size]
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    logging.info(f"Train: {len(train_dataset)} samples, Val: {len(val_dataset)} samples")
    
    # 3. Initialisation du modèle
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = PointNet(num_points=num_points, num_classes=4)
    model.to(device)
    
    logging.info(f"Modèle sur: {device}")
    logging.info(f"Nombre de paramètres: {sum(p.numel() for p in model.parameters())}")
    
    # 4. Configuration de l'entraînement
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.5)
    
    # Losses
    mesh_loss_fn = nn.MSELoss()
    class_loss_fn = nn.CrossEntropyLoss()
    
    # 5. Boucle d'entraînement
    best_val_loss = float('inf')
    save_dir.mkdir(parents=True, exist_ok=True)
    
    for epoch in range(epochs):
        # Entraînement
        model.train()
        train_loss = 0
        train_mesh_loss = 0
        train_class_loss = 0
        
        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
        for batch in progress_bar:
            points = batch['points'].to(device)  # (B, N, 3)
            zone_labels = batch['zone'].squeeze().to(device)  # (B,)
            
            # Transposer pour PointNet: (B, 3, N)
            points = points.permute(0, 2, 1)
            
            # Forward
            mesh_pred, class_pred = model(points)
            
            # Pour l'entraînement, on n'a pas de mesh GT (non supervisé)
            # On utilise une perte de reconstruction basée sur la cohérence
            # Pour l'instant, on simule avec une perte nulle
            loss_mesh = torch.tensor(0.0).to(device)
            
            # Perte de classification
            loss_class = class_loss_fn(class_pred, zone_labels)
            
            # Perte totale (pour l'instant, seulement classification)
            loss = loss_class
            
            # Backward
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # Métriques
            train_loss += loss.item()
            train_class_loss += loss_class.item()
            
            progress_bar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'class': f'{loss_class.item():.4f}'
            })
        
        # Validation
        model.eval()
        val_loss = 0
        val_class_loss = 0
        
        with torch.no_grad():
            for batch in val_loader:
                points = batch['points'].to(device).permute(0, 2, 1)
                zone_labels = batch['zone'].squeeze().to(device)
                
                _, class_pred = model(points)
                loss_class = class_loss_fn(class_pred, zone_labels)
                
                val_class_loss += loss_class.item()
                val_loss += loss_class.item()
        
        # Métriques moyennes
        avg_train_loss = train_loss / len(train_loader)
        avg_train_class = train_class_loss / len(train_loader)
        avg_val_loss = val_loss / len(val_loader)
        avg_val_class = val_class_loss / len(val_loader)
        
        # Logging
        logging.info(
            f"Epoch {epoch+1}: "
            f"Train Loss: {avg_train_loss:.4f}, "
            f"Train Class: {avg_train_class:.4f}, "
            f"Val Loss: {avg_val_loss:.4f}, "
            f"Val Class: {avg_val_class:.4f}"
        )
        
        # Scheduler
        scheduler.step()
        
        # Sauvegarde du meilleur modèle
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': avg_val_loss,
                'num_points': num_points
            }, save_dir / 'best_model.pth')
            logging.info(f"✅ Meilleur modèle sauvegardé (loss: {avg_val_loss:.4f})")
        
        # Sauvegarde périodique
        if (epoch + 1) % 10 == 0:
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': avg_val_loss
            }, save_dir / f'checkpoint_epoch_{epoch+1}.pth')
    
    logging.info("✅ Entraînement terminé !")
    return model

if __name__ == "__main__":
    train_model()