"""
Ejemplo: Calculadora simple para demostrar métricas.

Este módulo demuestra código con buenas y malas prácticas
para testing de los agentes de calidad.
"""

from typing import Union

Number = Union[int, float]


class Calculator:
    """
    Calculadora con operaciones básicas.

    Ejemplo de clase con buena cohesión (LCOM bajo).
    """

    def __init__(self):
        """Inicializa la calculadora."""
        self.last_result: Number = 0
        self.history: list[Number] = []

    def add(self, a: Number, b: Number) -> Number:
        """Suma dos números."""
        result = a + b
        self._save_result(result)
        return result

    def subtract(self, a: Number, b: Number) -> Number:
        """Resta dos números."""
        result = a - b
        self._save_result(result)
        return result

    def multiply(self, a: Number, b: Number) -> Number:
        """Multiplica dos números."""
        result = a * b
        self._save_result(result)
        return result

    def divide(self, a: Number, b: Number) -> Number:
        """
        Divide dos números.

        Raises:
            ValueError: Si b es cero
        """
        if b == 0:
            raise ValueError("No se puede dividir por cero")
        result = a / b
        self._save_result(result)
        return result

    def _save_result(self, result: Number) -> None:
        """Guarda resultado en historial."""
        self.last_result = result
        self.history.append(result)

    def clear_history(self) -> None:
        """Limpia el historial."""
        self.history.clear()
        self.last_result = 0


# Ejemplo de función con alta complejidad ciclomática (mala práctica)
def complex_calculation(a: int, b: int, c: int, operation: str) -> int:
    """
    Función con alta complejidad ciclomática.

    Esta función es un ejemplo de código que debería
    ser refactorizado según las métricas de CodeGuard.

    CC = 8 (supera umbral de 10 si se agrega más lógica)
    """
    result = 0

    if operation == "add":
        if a > 0:
            result = a + b + c
        else:
            result = b + c
    elif operation == "subtract":
        if a > b:
            result = a - b - c
        else:
            result = b - a - c
    elif operation == "multiply":
        if c != 0:
            result = a * b * c
        else:
            result = a * b
    elif operation == "divide":
        if b != 0 and c != 0:
            result = a // b // c
        elif b != 0:
            result = a // b
        else:
            result = 0

    return result


# Ejemplo de God Class (mala práctica)
class GodCalculator:
    """
    Ejemplo de God Class - hace demasiadas cosas.

    Esta clase viola el principio de responsabilidad única
    y debería ser dividida en clases más pequeñas.

    Métricas esperadas:
    - WMC: Alto (muchos métodos)
    - LCOM: Alto (baja cohesión)
    - CBO: Potencialmente alto si se agregan dependencias
    """

    def __init__(self):
        self.value = 0
        self.history = []
        self.logs = []
        self.config = {}
        self.cache = {}

    # Operaciones matemáticas
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        return a / b if b != 0 else 0

    # Logging (debería estar en otra clase)
    def log(self, message):
        self.logs.append(message)

    def get_logs(self):
        return self.logs

    def clear_logs(self):
        self.logs.clear()

    # Configuración (debería estar en otra clase)
    def set_config(self, key, value):
        self.config[key] = value

    def get_config(self, key):
        return self.config.get(key)

    # Cache (debería estar en otra clase)
    def cache_result(self, key, value):
        self.cache[key] = value

    def get_cached(self, key):
        return self.cache.get(key)

    def clear_cache(self):
        self.cache.clear()

    # Historial (ya está en Calculator, duplicación)
    def save_to_history(self, value):
        self.history.append(value)

    def get_history(self):
        return self.history
