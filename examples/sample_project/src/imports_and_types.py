"""
Ejemplo: Código con imports sin usar y problemas de tipos.

Este archivo demuestra problemas que CodeGuard detecta con
ImportCheck y TypeCheck.
"""

# PROBLEMA 1: Imports sin usar
import os  # No se usa
import sys  # No se usa
import json  # No se usa
from typing import Dict, List, Optional, Union  # Algunos no se usan
from pathlib import Path  # No se usa
import datetime  # No se usa

# Solo se usan estos:
from typing import Any


# PROBLEMA 2: Función sin type hints
def add(a, b):  # Debería tener type hints
    """Suma dos números."""
    return a + b


# PROBLEMA 3: Type hints incorrectos
def multiply(a: int, b: int) -> int:
    """Multiplica - pero retorna float si recibe floats."""
    return a * b  # Debería retornar Union[int, float] o usar generics


# PROBLEMA 4: Parámetros con Any (no específico)
def process_data(data: Any) -> Any:
    """Procesa datos - tipos muy genéricos."""
    return data


# PROBLEMA 5: Función que puede retornar None pero no lo indica
def find_user(user_id: int) -> dict:  # Debería ser Optional[dict]
    """Busca usuario por ID."""
    if user_id > 0:
        return {"id": user_id, "name": "Test"}
    return None  # mypy detectará este error


# PROBLEMA 6: Tipo incorrecto en asignación
def calculate_average(numbers: list[int]) -> float:
    """Calcula promedio."""
    if not numbers:
        return "No data"  # ERROR: debería retornar float, no str

    return sum(numbers) / len(numbers)


# PROBLEMA 7: Imports duplicados (más arriba)
import os  # Duplicado


# PROBLEMA 8: Import de módulo completo cuando solo se usa una función
import datetime  # Debería ser: from datetime import datetime


# CORRECCIÓN RECOMENDADA:
# - Eliminar imports sin usar: autoflake --remove-unused-variables --in-place
# - Agregar type hints: mypy --install-types
# - Usar Optional[T] para valores que pueden ser None
# - Ser específico con los tipos (evitar Any)
