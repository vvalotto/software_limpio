"""
Configuración compartida para pytest.
"""

import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_project():
    """Crea un proyecto temporal para testing."""
    temp_dir = Path(tempfile.mkdtemp())

    # Crear estructura básica
    src_dir = temp_dir / "src"
    src_dir.mkdir()

    # Crear archivo Python de ejemplo
    sample_file = src_dir / "sample.py"
    sample_file.write_text('''
"""Módulo de ejemplo para testing."""

def simple_function(x: int) -> int:
    """Función simple."""
    return x + 1


def complex_function(a, b, c, d, e):
    """Función con muchos parámetros."""
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    return e
    return 0


class SampleClass:
    """Clase de ejemplo."""

    def __init__(self):
        self.value = 0

    def increment(self):
        self.value += 1

    def decrement(self):
        self.value -= 1
''')

    yield temp_dir

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_python_file(temp_project):
    """Retorna path al archivo Python de ejemplo."""
    return temp_project / "src" / "sample.py"


@pytest.fixture
def empty_config():
    """Retorna configuración vacía para testing."""
    from quality_agents.shared.config import QualityConfig
    return QualityConfig()
