import xml.etree.ElementTree as ET
import numpy as np
from pathlib import Path
from typing import List, Tuple

class SVGParser:
    """Parse les fichiers SVG et extrait les trajectoires"""
    
    def __init__(self, svg_path: Path):
        self.tree = ET.parse(svg_path)
        self.root = self.tree.getroot()
        self.namespace = {'svg': 'http://www.w3.org/2000/svg'}
        
    def extract_paths(self) -> List[np.ndarray]:
        """Extrait les chemins du SVG"""
        paths = []
        
        for path_elem in self.root.findall('.//svg:path', self.namespace):
            d_attr = path_elem.get('d')
            if d_attr:
                points = self._parse_path_data(d_attr)
                paths.append(points)
        
        return paths
    
    def _parse_path_data(self, d: str) -> np.ndarray:
        """Parse une chaîne de commandes SVG en points"""
        # Simplifié : ne gère que les commandes M, L, C
        points = []
        commands = d.replace(',', ' ').split()
        
        i = 0
        current_pos = np.array([0.0, 0.0])
        while i < len(commands):
            cmd = commands[i]
            if cmd in ['M', 'L']:
                x = float(commands[i+1])
                y = float(commands[i+2])
                current_pos = np.array([x, y])
                points.append(current_pos)
                i += 3
            elif cmd == 'C':
                # Bézier cubique - simplifié: on prend les points de contrôle
                x1, y1, x2, y2, x, y = map(float, commands[i+1:i+7])
                # Convertir en ligne droite pour simplifier
                current_pos = np.array([x, y])
                points.append(current_pos)
                i += 7
            elif cmd == 'Z':
                # Fermeture du chemin
                if points:
                    points.append(points[0])
                i += 1
            else:
                i += 1
        
        return np.array(points) if points else np.array([])