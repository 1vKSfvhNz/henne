import os
import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple
import json
from PIL import Image
import logging

class DataPipeline:
    """Pipeline de chargement et prétraitement des données"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.supported_formats = {'.png', '.jpg', '.jpeg', '.webp'}
        
    def load_images(self, zone: str) -> List[np.ndarray]:
        """Charge toutes les images d'une zone spécifique"""
        zone_dir = self.data_dir / 'raw' / 'scans_3d' / zone
        images = []
        
        for ext in self.supported_formats:
            for img_path in zone_dir.glob(f"*{ext}"):
                # Charger avec OpenCV
                img = cv2.imread(str(img_path))
                if img is not None:
                    images.append(img)
                    
        logging.info(f"Chargé {len(images)} images pour la zone {zone}")
        return images
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Prétraitement standard"""
        # Redimensionner
        resized = cv2.resize(image, (640, 480))
        # Normaliser
        normalized = resized / 255.0
        return normalized
    
    def augment_data(self, image: np.ndarray) -> List[np.ndarray]:
        """Augmentation de données"""
        augmented = []
        
        # Rotation
        angles = [90, 180, 270]
        for angle in angles:
            rotated = self._rotate_image(image, angle)
            augmented.append(rotated)
        
        # Flip
        flipped = cv2.flip(image, 1)
        augmented.append(flipped)
        
        # Bruit
        noisy = self._add_noise(image, 0.1)
        augmented.append(noisy)
        
        # Changement de luminosité
        bright = cv2.convertScaleAbs(image, alpha=1.2, beta=30)
        augmented.append(bright)
        
        return augmented
    
    def _rotate_image(self, image: np.ndarray, angle: int) -> np.ndarray:
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, M, (w, h))
    
    def _add_noise(self, image: np.ndarray, intensity: float) -> np.ndarray:
        noise = np.random.randn(*image.shape) * intensity
        return np.clip(image + noise, 0, 255).astype(np.uint8)