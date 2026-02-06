"""
Ejemplo: Código con problemas de seguridad.

Este archivo contiene vulnerabilidades intencionales para demostrar
cómo CodeGuard (SecurityCheck) las detecta.
"""

import os
import pickle
import yaml

# PROBLEMA 1: Hardcoded password (ERROR crítico)
DATABASE_PASSWORD = "super_secret_123"  # bandit detectará esto
API_KEY = "sk-1234567890abcdef"

# PROBLEMA 2: Uso de eval() (ERROR crítico)
def calculate_expression(expr: str) -> float:
    """Evalúa expresión matemática - INSEGURO."""
    return eval(expr)  # Muy peligroso, permite ejecución arbitraria


# PROBLEMA 3: Uso inseguro de pickle (WARNING)
def load_data(filename: str):
    """Carga datos desde archivo pickle - INSEGURO."""
    with open(filename, 'rb') as f:
        return pickle.load(f)  # Deserialización insegura


# PROBLEMA 4: Uso inseguro de YAML (WARNING)
def load_config(filename: str):
    """Carga configuración desde YAML - INSEGURO."""
    with open(filename, 'r') as f:
        return yaml.load(f)  # Debería ser yaml.safe_load()


# PROBLEMA 5: SQL injection potencial (WARNING)
def get_user(username: str):
    """Busca usuario en base de datos - VULNERABLE A SQL INJECTION."""
    import sqlite3
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Vulnerable: concatenación de strings en SQL
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)  # bandit detectará esto

    return cursor.fetchone()


# PROBLEMA 6: Assert en código de producción (WARNING)
def process_data(data):
    """Procesa datos con validación insegura."""
    assert data is not None, "Data cannot be None"  # No usar assert
    assert len(data) > 0, "Data cannot be empty"
    return data[0]


# PROBLEMA 7: Uso de exec() (ERROR crítico)
def run_command(code: str):
    """Ejecuta código Python arbitrario - EXTREMADAMENTE INSEGURO."""
    exec(code)  # Nunca usar exec() con input del usuario


# PROBLEMA 8: Tempfile inseguro (WARNING)
def create_temp_file():
    """Crea archivo temporal de forma insegura."""
    import tempfile
    # Inseguro: predecible, race condition
    filename = "/tmp/myapp_" + str(os.getpid())
    with open(filename, 'w') as f:
        f.write("secret data")
    return filename


# CORRECCIÓN RECOMENDADA:
# - Usar variables de entorno: os.getenv('DATABASE_PASSWORD')
# - Evitar eval/exec completamente
# - Usar yaml.safe_load() en lugar de yaml.load()
# - Usar SQL parametrizado: cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
# - Validar con if, no con assert
# - Usar tempfile.NamedTemporaryFile(delete=False)
