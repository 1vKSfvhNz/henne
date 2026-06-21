# src_python/ai_models/reconstruction/export_onnx.py

import torch
import onnx
import onnxruntime
from .pointnet import PointNet

def export_to_onnx(model_path: str, output_path: str = "models/pointnet.onnx"):
    """Exporte le modèle PyTorch vers ONNX pour TensorRT"""
    
    # Charger le modèle
    model = PointNet(num_points=5000, num_classes=4)
    checkpoint = torch.load(model_path)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    # Exemple d'input
    dummy_input = torch.randn(1, 3, 5000)
    
    # Exporter
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=11,
        do_constant_folding=True,
        input_names=['points'],
        output_names=['mesh', 'classification'],
        dynamic_axes={
            'points': {0: 'batch_size', 2: 'num_points'},
            'mesh': {0: 'batch_size', 1: 'num_points'},
            'classification': {0: 'batch_size'}
        }
    )
    
    # Vérifier le modèle ONNX
    onnx_model = onnx.load(output_path)
    onnx.checker.check_model(onnx_model)
    print(f"✅ Modèle exporté vers {output_path}")
    
    # Tester avec ONNX Runtime
    ort_session = onnxruntime.InferenceSession(output_path)
    ort_inputs = {ort_session.get_inputs()[0].name: dummy_input.numpy()}
    ort_outputs = ort_session.run(None, ort_inputs)
    print(f"✅ Modèle testé avec ONNX Runtime")
    
    return output_path