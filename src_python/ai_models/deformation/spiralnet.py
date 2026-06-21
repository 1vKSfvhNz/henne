import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class SpiralNet(nn.Module):
    """
    SpiralNet++ pour déformer des motifs sur un mesh 3D
    Basé sur le papier de Bouritsas et al.
    """
    
    def __init__(self, input_dim=3, hidden_dim=128, output_dim=3):
        super(SpiralNet, self).__init__()
        
        # Couches de convolution sur graphe (simplifié)
        self.spiral_conv1 = self._create_spiral_layer(input_dim, hidden_dim)
        self.spiral_conv2 = self._create_spiral_layer(hidden_dim, hidden_dim)
        self.spiral_conv3 = self._create_spiral_layer(hidden_dim, output_dim)
        
        # Mécanisme d'attention pour préserver la longueur
        self.attention = nn.MultiheadAttention(hidden_dim, num_heads=4)
        
    def _create_spiral_layer(self, in_dim, out_dim):
        """Crée une couche de convolution spirale simplifiée"""
        return nn.Sequential(
            nn.Linear(in_dim, out_dim),
            nn.ReLU(),
            nn.BatchNorm1d(out_dim),
        )
    
    def forward(self, pattern_points, mesh_vertices):
        """
        pattern_points: points du motif SVG (N, 3)
        mesh_vertices: vertices du mesh 3D (M, 3)
        """
        # Projeter les points du motif sur le mesh
        # (Simplifié - en réalité on utilise des convolutions sur graphe)
        
        # Trouver les plus proches voisins sur le mesh
        projected = self._project_to_mesh(pattern_points, mesh_vertices)
        
        # Déformer
        x = projected
        x = self.spiral_conv1(x.transpose(0, 1)).transpose(0, 1)
        x, _ = self.attention(x, x, x)
        x = self.spiral_conv2(x.transpose(0, 1)).transpose(0, 1)
        deformed = self.spiral_conv3(x.transpose(0, 1)).transpose(0, 1)
        
        # Ajouter la contrainte de préservation de longueur
        deformed = self._preserve_length(pattern_points, deformed)
        
        return deformed
    
    def _project_to_mesh(self, points, mesh):
        """Projette les points sur le mesh"""
        # Calcul des distances aux vertices du mesh
        # Utilisation d'un KD-tree pour l'efficacité
        from scipy.spatial import KDTree
        tree = KDTree(mesh.numpy())
        distances, indices = tree.query(points.numpy())
        
        projected = mesh[indices]
        return torch.FloatTensor(projected)
    
    def _preserve_length(self, original, deformed):
        """Préserve la longueur des traits"""
        # Calcul de la longueur originale
        orig_lengths = torch.sqrt(torch.sum((original[1:] - original[:-1])**2, dim=1))
        total_orig = torch.sum(orig_lengths)
        
        # Calcul de la longueur déformée
        def_lengths = torch.sqrt(torch.sum((deformed[1:] - deformed[:-1])**2, dim=1))
        total_def = torch.sum(def_lengths)
        
        # Ajuster pour conserver la longueur
        if total_def > 0:
            scale = total_orig / total_def
            deformed = deformed * scale
        
        return deformed