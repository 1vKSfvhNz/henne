import torch
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
from pathlib import Path
import logging
from datetime import datetime

from .pointnet import PointNetPlusPlus, ScanDataset

def train_model(data_dir: Path, epochs=100, batch_size=8):
    """Entraîne le modèle PointNet++"""
    
    # Créer le dataset
    dataset = ScanDataset(data_dir)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=4)
    
    # Modèle
    model = PointNetPlusPlus(num_points=5000)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    
    # Optimiseur
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=20, gamma=0.5)
    
    # Loss
    mesh_loss_fn = nn.MSELoss()
    segmentation_loss_fn = nn.CrossEntropyLoss()
    
    # Logging
    log_dir = Path('logs/training')
    log_dir.mkdir(parents=True, exist_ok=True)
    
    for epoch in range(epochs):
        epoch_loss = 0
        for batch in dataloader:
            points = batch['points'].to(device)
            labels = batch['label'].to(device)
            
            # Forward
            mesh_pred, seg_pred = model(points)
            
            # Loss (sans ground truth pour l'instant, modèle non supervisé)
            # Ici on utiliserait des données annotées
            # loss = mesh_loss_fn(mesh_pred, mesh_gt) + segmentation_loss_fn(seg_pred, labels)
            
            # Pour l'exemple, loss simulée
            loss = torch.tensor(0.5)
            
            # Backward
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
        
        scheduler.step()
        
        # Log
        logging.info(f"Epoch {epoch}/{epochs}, Loss: {epoch_loss/len(dataloader)}")
        
        # Sauvegarder le modèle
        if (epoch + 1) % 10 == 0:
            torch.save(model.state_dict(), f"{log_dir}/pointnet_epoch_{epoch+1}.pth")
    
    return model

# Exporter en ONNX pour TensorRT
def export_to_onnx(model, output_path="models/pointnet.onnx"):
    dummy_input = torch.randn(1, 3, 5000)
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['mesh', 'segmentation'],
        dynamic_axes={'input': {0: 'batch_size'}}
    )
    logging.info(f"Modèle exporté vers {output_path}")