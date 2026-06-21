import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class LSTMPredictor(nn.Module):
    """
    LSTM pour prédire les paramètres de contrôle en temps réel
    """
    
    def __init__(self, input_size=8, hidden_size=64, output_size=4, num_layers=2):
        super(LSTMPredictor, self).__init__()
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.2
        )
        
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(32, output_size)
        )
        
    def forward(self, x):
        # x: (batch, seq_len, input_size)
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Dernier état
        last_out = lstm_out[:, -1, :]
        output = self.fc(last_out)
        
        # Appliquer les contraintes physiques
        output = self._apply_constraints(output)
        
        return output
    
    def _apply_constraints(self, x):
        """Applique des contraintes physiques aux sorties"""
        # x: [debit, pression, hauteur, vitesse]
        # Débit: 0-60 µl/s
        x[:, 0] = torch.sigmoid(x[:, 0]) * 60
        
        # Pression: 0-5 bar
        x[:, 1] = torch.sigmoid(x[:, 1]) * 5
        
        # Hauteur: 1-5 mm
        x[:, 2] = torch.sigmoid(x[:, 2]) * 4 + 1
        
        # Vitesse: 5-40 mm/s
        x[:, 3] = torch.sigmoid(x[:, 3]) * 35 + 5
        
        return x

class RealtimeController:
    """Contrôleur temps réel intégrant le LSTM"""
    
    def __init__(self, model_path: str):
        self.model = LSTMPredictor()
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()
        
        # Paramètres PID pour correction
        self.kp = 0.5
        self.ki = 0.1
        self.kd = 0.05
        self.prev_error = 0
        self.integral = 0
        
        # Historique pour LSTM
        self.history = []
        self.window_size = 10
        
    def predict(self, state: np.ndarray) -> np.ndarray:
        """
        Prédit les paramètres de contrôle
        state: [error_pos, curvature, speed, temperature, humidity, ...]
        """
        # Ajouter à l'historique
        self.history.append(state)
        if len(self.history) > self.window_size:
            self.history.pop(0)
        
        # Si pas assez d'historique, utiliser des valeurs par défaut
        if len(self.history) < self.window_size:
            return np.array([30, 2.5, 2.5, 20])  # valeurs par défaut
        
        # Préparer l'input pour LSTM
        input_tensor = torch.FloatTensor(np.array(self.history)).unsqueeze(0)  # (1, seq_len, input_size)
        
        with torch.no_grad():
            output = self.model(input_tensor)
        
        return output.squeeze().numpy()
    
    def pid_correction(self, error: float) -> float:
        """Correction PID pour la trajectoire"""
        self.integral += error
        derivative = error - self.prev_error
        
        correction = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        
        return correction