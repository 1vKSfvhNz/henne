import pytest
import numpy as np
from pathlib import Path
from src_python.tools.data_pipeline import DataPipeline

def test_image_loading():
    """Test le chargement d'images"""
    pipeline = DataPipeline(Path('data'))
    images = pipeline.load_images('main')
    assert len(images) > 0
    assert images[0].shape == (480, 640, 3)

def test_augmentation():
    """Test l'augmentation de données"""
    pipeline = DataPipeline(Path('data'))
    test_image = np.random.rand(640, 480, 3)
    augmented = pipeline.augment_data(test_image)
    assert len(augmented) == 6  # 3 rotations + 1 flip + 1 noise + 1 brightness