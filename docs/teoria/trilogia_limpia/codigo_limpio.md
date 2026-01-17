# Código Limpio

> *"El código limpio siempre parece escrito por alguien a quien le importa."*
> — **Robert C. Martin**, Clean Code (2008)

**Pregunta ética:** *¿Puede otro humano entender esto?*

**Nivel Micro:** Funciones, nombres, estilo

---

## Definición

Código que se lee como prosa. Que comunica intención sin comentarios. Que otro desarrollador puede entender en minutos, no horas.

**No es:** perfección estética o seguir reglas por seguirlas.

**Es:** respeto por quien lee tu código, incluyendo tu yo futuro.

---

## Por Qué Importa

El código se lee 10 veces más de lo que se escribe. Un nombre vago cuesta 5 minutos de confusión cada vez que alguien lo encuentra. Una función de 100 líneas cuesta 30 minutos de análisis mental.

**El código sucio no es deuda técnica. Es falta de respeto.**

### En la Era de la IA

La IA genera código funcional en segundos. Pero código funcional ≠ código limpio.

Sin criterio, la IA genera:
- Nombres genéricos (`data`, `temp`, `process`)
- Funciones largas que hacen múltiples cosas
- Lógica anidada difícil de seguir

**Tu responsabilidad: refinar lo generado hasta que sea legible.**

---

## Los Cinco Pilares

### 1. Nombres Significativos

**Regla:** El nombre debe revelar intención. No debe requerir comentario.

```python
# Mal: requiere comentario
d = 86400  # segundos en un día

# Bien: se explica solo
SECONDS_PER_DAY = 86400
```

**Nombres de variables:**
```python
# Mal
x = get_data()
tmp = x[0]
result = process(tmp)

# Bien
user_records = fetch_active_users()
first_user = user_records[0]
validated_user = validate_credentials(first_user)
```

**Nombres de funciones:**
```python
# Mal: qué hace "do"?
def do(u):
    pass

# Bien: verbo + sustantivo
def authenticate_user(user):
    pass
```

**Reglas prácticas:**
- Variables y parámetros: sustantivos (`user`, `total_price`)
- Funciones: verbos (`calculate`, `validate`, `format`)
- Booleanos: preguntas (`is_valid`, `has_permission`)
- Clases: sustantivos concretos (`UserRepository`, no `Manager`)

---

### 2. Funciones Pequeñas

**Regla:** Una función hace **una cosa**. Si tiene más de 20 líneas, probablemente hace múltiples cosas.

```python
# Mal: hace validar + calcular + guardar
def process_order(order):
    # Validar (15 líneas)
    if not order.customer:
        raise ValueError("No customer")
    if order.items == []:
        raise ValueError("Empty order")
    # ...

    # Calcular (20 líneas)
    total = 0
    for item in order.items:
        # ...
        pass

    # Guardar (10 líneas)
    db.save(order)
    return total

# Bien: cada función hace una cosa
def process_order(order):
    validate_order(order)
    total = calculate_total(order)
    save_order(order)
    return total

def validate_order(order):
    if not order.customer:
        raise ValueError("No customer")
    if not order.items:
        raise ValueError("Empty order")

def calculate_total(order):
    return sum(item.price * item.quantity for item in order.items)

def save_order(order):
    db.save(order)
```

**Beneficios:**
- Cada función se entiende sin leer el contexto
- Se puede testear por separado
- Se puede reusar
- El nombre documenta qué hace

---

### 3. Profundidad de Anidamiento

**Regla:** No más de 3-4 niveles de indentación. Si necesitás más, extraé funciones.

```python
# Mal: 5 niveles
def check_eligibility(user):
    if user.active:
        if user.age >= 18:
            if user.country == "AR":
                if user.verified:
                    if user.balance > 0:
                        return True
    return False

# Bien: early returns
def check_eligibility(user):
    if not user.active:
        return False
    if user.age < 18:
        return False
    if user.country != "AR":
        return False
    if not user.verified:
        return False
    return user.balance > 0
```

**Mejor aún: extraer funciones**
```python
def check_eligibility(user):
    return (
        is_active_user(user) and
        is_adult(user) and
        is_in_argentina(user) and
        is_verified(user) and
        has_balance(user)
    )
```

---

### 4. Comentarios que Agregan Valor

**Regla:** El código explica el *cómo*. Los comentarios explican el *por qué*.

```python
# Mal: comentario obvio
# Incrementar el contador
counter += 1

# Mal: comentario que podría ser un nombre mejor
# Calcular el precio con descuento
p = total * 0.85

# Bien: explicar por qué
# Aplicamos 15% de descuento por Black Friday
discounted_price = total * 0.85

# Bien: advertir sobre decisiones no obvias
def calculate_distance(x1, y1, x2, y2):
    # Usamos distancia Manhattan en lugar de Euclidiana
    # porque el costo computacional importa más que la precisión
    return abs(x2 - x1) + abs(y2 - y1)
```

**Cuándo comentar:**
- Decisiones de negocio no obvias
- Limitaciones conocidas (bugs de terceros)
- Advertencias (performance, seguridad)
- TODOs (pero con ticket asociado)

**Cuándo NO comentar:**
- Código obvio
- Código que podría tener mejor nombre
- Código viejo comentado (usar git)

---

### 5. Manejo de Errores

**Regla:** Fallar rápido y explícito. No ocultar errores.

```python
# Mal: silenciar errores
def get_user(user_id):
    try:
        return db.get(user_id)
    except:
        return None  # ¿Qué falló? ¿DB caída? ¿User inexistente?

# Bien: errores específicos
def get_user(user_id):
    try:
        return db.get(user_id)
    except ConnectionError as e:
        raise DatabaseUnavailable(f"Cannot connect to DB: {e}")
    except KeyError:
        raise UserNotFound(f"User {user_id} does not exist")

# Mejor: validar primero
def get_user(user_id):
    if not isinstance(user_id, int):
        raise ValueError(f"user_id must be int, got {type(user_id)}")

    user = db.get(user_id)
    if user is None:
        raise UserNotFound(f"User {user_id} not found")

    return user
```

**Excepciones vs None:**
- `None`: cuando la ausencia es parte del dominio (`find_user` puede no encontrar)
- Excepción: cuando es un error que el llamador debe manejar

---

## Formato y Estilo

### Consistencia > Preferencias

No importa si usás 2 o 4 espacios. Importa que **todo el proyecto use lo mismo**.

**Herramientas obligatorias:**
- `black`: formateador automático
- `isort`: ordenar imports
- `flake8` o `ruff`: detectar violaciones de PEP8

**Configurar una vez, nunca discutir de nuevo.**

### Reglas Universales

```python
# Largo de línea: ≤ 100 caracteres
# (configurado en black)

# Imports agrupados
# 1. Librería estándar
import os
from pathlib import Path

# 2. Terceros
import requests
from flask import Flask

# 3. Locales
from myapp.models import User
from myapp.utils import validate

# Espacios alrededor de operadores
x = 1 + 2  # bien
x=1+2      # mal

# Sin espacios en llamadas
func(arg1, arg2)  # bien
func (arg1, arg2) # mal

# Líneas en blanco
# 2 entre funciones/clases de nivel módulo
# 1 dentro de clases

class User:
    def __init__(self):
        pass

    def login(self):  # 1 línea en blanco
        pass


def external_function():  # 2 líneas en blanco
    pass
```

---

## Métricas de Código Limpio

| Métrica | Qué mide | Umbral | Herramienta |
|---------|----------|--------|-------------|
| **Complejidad Ciclomática** | Caminos posibles en una función | ≤ 10 | radon, pylint |
| **Líneas por función** | Tamaño de función | ≤ 20 | radon |
| **Profundidad anidamiento** | Niveles de if/for | ≤ 4 | radon |
| **Largo de línea** | Caracteres por línea | ≤ 100 | black, flake8 |
| **Duplicación** | Código repetido | < 5% | pylint |

**Ejecutar:**
```bash
# Complejidad
radon cc src/ -a -nb

# Métricas generales
radon mi src/ --min=B

# Estilo
flake8 src/ --max-line-length=100
```

---

## Anti-patrones

### 1. Clase Dios
```python
# Mal: una clase que hace todo
class User:
    def authenticate(self): pass
    def send_email(self): pass
    def calculate_discount(self): pass
    def generate_report(self): pass
    def update_database(self): pass
```

**Solución:** Separar responsabilidades.

### 2. Función con Muchos Parámetros
```python
# Mal: imposible recordar el orden
def create_user(name, email, age, country, city, phone, address, zip_code):
    pass
```

**Solución:** Usar dataclass o diccionario.
```python
@dataclass
class UserData:
    name: str
    email: str
    age: int
    location: Location

def create_user(data: UserData):
    pass
```

### 3. Magic Numbers
```python
# Mal
if user.age > 18:
    pass

# Bien
LEGAL_AGE = 18
if user.age > LEGAL_AGE:
    pass
```

---

## Código Limpio con IA

### Prompt inicial
```
"Crear función calculate_order_total que:
- Reciba una lista de items
- Calcule el total sumando precio * cantidad
- Aplique descuento si total > $1000
- Nombres descriptivos
- Complejidad ciclomática ≤ 5
- Máximo 15 líneas
- Type hints"
```

### Refinar lo generado

1. **Revisar nombres:** ¿Son descriptivos?
2. **Medir complejidad:** `radon cc archivo.py`
3. **Dividir funciones largas:** Extraer responsabilidades
4. **Eliminar comentarios obvios:** El código debe auto-explicarse
5. **Formatear:** `black archivo.py`

**No delegues la responsabilidad de legibilidad a la IA.**

---

## La Prueba del Elevator

> *"Si no podés explicar tu función en una oración simple, hace múltiples cosas."*

- "Calcula el total del pedido" → ✓ Una cosa
- "Valida el usuario, calcula el total y guarda en BD" → ✗ Tres cosas

---

## Lecturas Recomendadas

1. **Martin, R.C. (2008)**. *Clean Code: A Handbook of Agile Software Craftsmanship*. Capítulos 1-3, 10.
2. **Thomas, D. & Hunt, A. (1999)**. *The Pragmatic Programmer*. Capítulo "Code That's Easy to Change".
3. **McConnell, S. (2004)**. *Code Complete*. Capítulos 5-7 (nombres, funciones).

---

[← Volver a Trilogía Limpia](README.md)
