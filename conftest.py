"""Hace que la raiz del repo sea importable desde los tests (fase2_*, etc.)
sin necesidad de instalar el proyecto como paquete."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
