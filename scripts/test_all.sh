#!/bin/bash

echo "=== Tests MIHI-CN v2.0 ==="

# Tests Python
echo "Exécution des tests Python..."
pytest src_python/tests/ -v

# Tests C++
echo "Exécution des tests C++..."
cd src/build && ctest

# Tests de performance
echo "Test de performance des modèles IA..."
python scripts/benchmark_models.py

# Tests matériels (simulés)
echo "Test de communication matérielle..."
python scripts/test_hardware_communication.py