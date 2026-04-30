"""Configura sys.path para que los tests puedan importar desde src/."""

import sys
from pathlib import Path

# Añade modules/01-primer-eval al path
sys.path.insert(0, str(Path(__file__).parent))
