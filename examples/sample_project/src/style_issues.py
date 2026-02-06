"""
Ejemplo: Código con problemas de estilo PEP8.

Este archivo viola múltiples reglas de PEP8 para demostrar
cómo CodeGuard (PEP8Check) las detecta.
"""

import os
import sys
import json
import math  # Import sin usar

# PROBLEMA 1: Líneas muy largas (> 100 caracteres)
very_long_variable_name_that_exceeds_the_maximum_line_length_recommended_by_pep8_which_is_usually_79_or_100_characters = "too long"

# PROBLEMA 2: Espaciado incorrecto en funciones
def   bad_function( x,y ):  # Espacios extras, sin espacio después de coma
    return x+y  # Sin espacios alrededor del operador

# PROBLEMA 3: Nombres de variables no conformes
MyVariable = 10  # Las variables deberían ser snake_case, no PascalCase
my_Constant = 20  # Constantes deberían ser UPPER_CASE

# PROBLEMA 4: Líneas en blanco incorrectas



def function_with_too_many_blank_lines_before():
    pass


# PROBLEMA 5: Import en mitad del archivo (debería estar al inicio)
def another_function():
    import random  # Los imports deberían estar al inicio del archivo
    return random.randint(1, 10)

# PROBLEMA 6: Indentación inconsistente
def bad_indentation():
    if True:
      return "2 spaces"  # Debería ser 4 espacios
    else:
        return "4 spaces"

# PROBLEMA 7: Trailing whitespace (espacios al final de línea)
def trailing_spaces():
    x = 10
    return x

# PROBLEMA 8: Múltiples statements en una línea
def multiple_statements(): x = 1; y = 2; return x + y

# PROBLEMA 9: Comparación incorrecta con None, True, False
def bad_comparisons(value):
    if value == None:  # Debería ser: if value is None:
        return False
    if value == True:  # Debería ser: if value:
        return True
    return False

# PROBLEMA 10: Nombres de funciones no conformes
def MyFunction():  # Debería ser snake_case
    pass

def FunctionWithBadName():  # Debería ser function_with_bad_name
    pass

# CORRECCIÓN RECOMENDADA:
# Ejecutar: black src/ --line-length 100
# Ejecutar: isort src/
# Seguir guía de estilo PEP8
