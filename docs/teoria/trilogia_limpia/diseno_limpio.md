# Diseño Limpio

> *"El diseño es donde los principios se vuelven estructura."*

**Pregunta ética:** *¿Puede otro humano modificar esto?*

**Nivel Medio:** Módulos, cohesión, acoplamiento

---

## Definición

El diseño limpio organiza el código en módulos con responsabilidades claras y relaciones explícitas. Es el puente entre código legible (micro) y arquitectura sostenible (macro).

**No es:** aplicar patrones de diseño por moda.

**Es:** estructurar el código para que cambios futuros sean localizados, no explosivos.

---

## El Vacío que Llena

Robert Martin escribió sobre código (funciones, nombres) y arquitectura (componentes, capas). Pero dejó un vacío en el **nivel medio**:

- ¿Cómo organizar clases en módulos?
- ¿Cuándo dividir un módulo en dos?
- ¿Cómo medir si un módulo está bien diseñado?

**Diseño Limpio llena ese vacío con principios medibles.**

---

## Por Qué Importa

Un sistema con código limpio pero mal diseño colapsa cuando crece. Cada cambio requiere tocar 10 archivos. Cada bug aparece en lugares inesperados.

**El mal diseño no se ve en la primera versión. Se sufre en la décima.**

### En la Era de la IA

La IA puede generar clases y módulos rápidamente. Pero no sabe:
- Si una clase tiene responsabilidades mezcladas (baja cohesión)
- Si dos módulos están demasiado acoplados
- Si una abstracción oculta las decisiones correctas

**Tu responsabilidad: estructurar el código generado según principios de diseño.**

---

## Los Seis Principios Fundamentales

El diseño limpio se basa en los 6 principios históricos (pre-OO, aplicables en cualquier paradigma):

| Principio | Pregunta Guía | Métrica |
|-----------|---------------|---------|
| **Modularidad** | ¿Está dividido en partes manejables? | LOC por módulo ≤ 500 |
| **Ocultamiento** | ¿Las decisiones de diseño están encapsuladas? | Public API < 20% |
| **Cohesión** | ¿Cada módulo hace una sola cosa? | LCOM ≤ 1 |
| **Acoplamiento** | ¿Los módulos son independientes? | CBO ≤ 5 |
| **Separación de Concerns** | ¿Cada módulo tiene una responsabilidad única? | SRP violations = 0 |
| **Abstracción** | ¿Se trabaja con conceptos, no detalles? | DIP compliance |

**Ver:** [`docs/teoria/fundamentos/`](../fundamentos/) para profundizar en cada principio.

---

## Los Tres Ejes del Diseño

### 1. Cohesión Alta

**Definición:** Los elementos de un módulo trabajan juntos hacia un propósito común.

```python
# Mal: baja cohesión (hace múltiples cosas no relacionadas)
class UserManager:
    def authenticate(self, user): pass
    def send_email(self, user, msg): pass
    def calculate_discount(self, user): pass
    def export_to_pdf(self, users): pass

# Bien: alta cohesión (cada clase una responsabilidad)
class Authenticator:
    def authenticate(self, user): pass
    def validate_credentials(self, user): pass

class EmailService:
    def send(self, recipient, message): pass
    def format_template(self, template, data): pass

class DiscountCalculator:
    def calculate(self, user): pass
    def apply_rules(self, user): pass
```

**Métrica:** LCOM (Lack of Cohesion of Methods)
- LCOM = 0: perfecta cohesión
- LCOM > 1: clase probablemente tiene múltiples responsabilidades

**Herramienta:** `radon`, `pylint`

---

### 2. Acoplamiento Bajo

**Definición:** Los módulos dependen lo mínimo posible entre sí. Cambios en uno no fuerzan cambios en otros.

```python
# Mal: alto acoplamiento (conoce detalles de implementación)
class OrderProcessor:
    def process(self, order):
        # Acopla a la implementación concreta de MySQL
        db = MySQLDatabase("localhost", "user", "pass")
        db.execute(f"INSERT INTO orders VALUES ({order.id}, ...)")

# Bien: bajo acoplamiento (depende de abstracción)
class OrderProcessor:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def process(self, order):
        # No conoce si es MySQL, Postgres, o archivo
        self.repository.save(order)
```

**Métrica:** CBO (Coupling Between Objects)
- CBO ≤ 5: acoplamiento aceptable
- CBO > 10: módulo demasiado dependiente

**Herramienta:** `pydeps`, análisis estático

---

### 3. Separación de Responsabilidades

**Definición:** Cada módulo tiene **una razón para cambiar**.

**Ejemplo clásico:**

```python
# Mal: mezcla lógica de negocio + persistencia + presentación
class Invoice:
    def calculate_total(self):
        # Lógica de negocio
        total = sum(item.price for item in self.items)
        tax = total * 0.21
        return total + tax

    def save_to_database(self):
        # Persistencia
        db.execute(f"INSERT INTO invoices ...")

    def print_pdf(self):
        # Presentación
        pdf = PDF()
        pdf.add_page()
        # ...

# Bien: responsabilidades separadas
class Invoice:
    """Lógica de negocio pura"""
    def calculate_total(self):
        total = sum(item.price for item in self.items)
        tax = total * 0.21
        return total + tax

class InvoiceRepository:
    """Persistencia"""
    def save(self, invoice):
        db.execute(f"INSERT INTO invoices ...")

class InvoicePrinter:
    """Presentación"""
    def print_pdf(self, invoice):
        pdf = PDF()
        # ...
```

**Razones para cambiar separadas:**
- Cambio en cálculo de impuestos → solo `Invoice`
- Cambio de MySQL a Postgres → solo `InvoiceRepository`
- Cambio en formato PDF → solo `InvoicePrinter`

---

## Métricas de Diseño Limpio

| Métrica | Qué mide | Umbral | Herramienta |
|---------|----------|--------|-------------|
| **LCOM** | Lack of Cohesion of Methods | ≤ 1 | radon, pylint |
| **CBO** | Coupling Between Objects | ≤ 5 | pydeps |
| **MI** | Maintainability Index | ≥ 20 (A-B) | radon |
| **WMC** | Weighted Methods per Class | ≤ 20 | radon |
| **RFC** | Response For Class | ≤ 50 | análisis estático |

**Ejecutar:**
```bash
# Cohesión
radon cc src/ --total-average

# Mantenibilidad
radon mi src/ --show --min=B

# Acoplamiento
pydeps src/ --max-bacon=2
```

---

## Patrones de Diseño

Los patrones son **soluciones probadas** a problemas recurrentes. Pero no son recetas a aplicar ciegamente.

### Cuándo Usar Patrones

**Usar cuando:**
- El problema encaja perfectamente
- Simplifica el diseño
- El equipo conoce el patrón

**No usar cuando:**
- Es "porque leí que es bueno"
- Complica más de lo que resuelve
- Nadie en el equipo lo entiende

### Patrones Fundamentales para Diseño Limpio

#### 1. Repository Pattern

**Problema:** Aislar lógica de negocio de persistencia.

```python
# Sin patrón: lógica acoplada a DB
class UserService:
    def register(self, username, password):
        # Lógica + SQL mezclados
        if len(password) < 8:
            raise ValueError("Password too short")
        db.execute(f"INSERT INTO users ...")

# Con patrón: responsabilidades separadas
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register(self, username, password):
        if len(password) < 8:
            raise ValueError("Password too short")
        user = User(username, password)
        self.repository.save(user)

class UserRepository:
    def save(self, user):
        db.execute(f"INSERT INTO users ...")
```

#### 2. Strategy Pattern

**Problema:** Diferentes algoritmos para la misma tarea.

```python
# Sin patrón: if/elif infinitos
def calculate_shipping(order, method):
    if method == "standard":
        return 10
    elif method == "express":
        return 25
    elif method == "overnight":
        return 50

# Con patrón: polimorfismo
class ShippingStrategy:
    def calculate(self, order): pass

class StandardShipping(ShippingStrategy):
    def calculate(self, order): return 10

class ExpressShipping(ShippingStrategy):
    def calculate(self, order): return 25

def calculate_shipping(order, strategy: ShippingStrategy):
    return strategy.calculate(order)
```

#### 3. Dependency Injection

**Problema:** Testear código que usa dependencias concretas.

```python
# Sin patrón: dependencia hardcodeada
class OrderService:
    def __init__(self):
        self.emailer = SMTPEmailer()  # Imposible testear sin SMTP

# Con patrón: inyección de dependencia
class OrderService:
    def __init__(self, emailer: EmailSender):
        self.emailer = emailer  # Puedo inyectar un mock en tests
```

---

## Diseño por Capas

Organizar módulos en **capas** con dependencias unidireccionales.

```
┌─────────────────────────────────────────┐
│         Presentación (API, CLI)         │
│  - Controladores HTTP                   │
│  - Parsers de input                     │
├─────────────────────────────────────────┤
│        Lógica de Negocio                │
│  - Casos de uso                         │
│  - Validaciones de dominio              │
│  - Reglas de negocio                    │
├─────────────────────────────────────────┤
│         Acceso a Datos                  │
│  - Repositories                         │
│  - ORM / Queries                        │
│  - Conexiones a DB                      │
└─────────────────────────────────────────┘
```

**Regla de dependencia:**
- Presentación → Lógica de Negocio → Acceso a Datos
- **Nunca al revés**

**Ejemplo de violación:**
```python
# Mal: capa de datos conoce presentación
class UserRepository:
    def save(self, user):
        db.execute(...)
        # ¡Violación! Repository enviando emails
        send_email(user.email, "Welcome!")
```

**Correcto:**
```python
# Bien: notificación en capa de negocio
class UserService:
    def register(self, user):
        self.repository.save(user)
        self.notifier.send_welcome_email(user)
```

---

## Diseño Limpio con IA

### Prompt para diseño

```
"Diseñar módulo de autenticación con:
- Alta cohesión (LCOM ≤ 1): una responsabilidad por clase
- Bajo acoplamiento (CBO ≤ 5): depender de abstracciones
- Separar:
  * AuthenticationService (lógica de negocio)
  * UserRepository (persistencia)
  * PasswordHasher (utilidad)
- Usar inyección de dependencias
- Type hints completos"
```

### Refinar el diseño generado

1. **Medir cohesión:** `radon cc -a`
2. **Verificar dependencias:** `pydeps --show-deps`
3. **Detectar violaciones de capas:** revisar imports
4. **Refactorizar:** si LCOM > 1, dividir clase

**Checklist:**
- [ ] ¿Cada clase tiene una razón para cambiar?
- [ ] ¿Puedo cambiar la implementación sin tocar otras clases?
- [ ] ¿Los nombres de las clases describen su responsabilidad?
- [ ] ¿Las dependencias apuntan hacia abstracciones, no concretos?

---

## Anti-patrones de Diseño

### 1. God Class

**Síntoma:** Una clase con 50+ métodos que sabe de todo.

**Solución:** Dividir según responsabilidades.

### 2. Feature Envy

**Síntoma:** Un método usa más datos de otra clase que de la propia.

```python
# Mal
class Order:
    def print_customer_name(self):
        # Usa datos de Customer, no de Order
        return self.customer.first_name + " " + self.customer.last_name

# Bien: mover el método a Customer
class Customer:
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
```

### 3. Inappropriate Intimacy

**Síntoma:** Dos clases que se conocen demasiado (acceden a atributos privados mutuamente).

**Solución:** Fusionar o separar claramente con interfaces.

### 4. Circular Dependencies

**Síntoma:** A importa B, B importa A.

```python
# Mal
# users.py
from orders import Order

# orders.py
from users import User  # Ciclo!
```

**Solución:** Crear abstracción compartida o reorganizar módulos.

---

## La Prueba del Cambio

> *"El buen diseño hace que cambios comunes sean fáciles, cambios raros sean posibles."*

**Preguntate:**
- Si mañana cambio de MySQL a Postgres, ¿cuántos archivos toco?
  - Respuesta ideal: 1 (el repository)
- Si agrego un nuevo método de pago, ¿dónde lo agrego?
  - Respuesta ideal: Una nueva clase `PaymentMethod`
- Si cambio el formato de email, ¿afecta la lógica de negocio?
  - Respuesta ideal: No, está en capa separada

**Si cada cambio requiere tocar 10 archivos, el diseño está acoplado.**

---

## En los Tres Niveles

| Aspecto | Código (Micro) | Diseño (Medio) | Arquitectura (Macro) |
|---------|----------------|----------------|----------------------|
| **Unidad** | Función | Módulo/Clase | Componente/Capa |
| **Cohesión** | Función hace una cosa | Clase una responsabilidad | Componente un concern |
| **Acoplamiento** | Pocos parámetros | Pocas dependencias | Pocas interfaces |
| **Abstracción** | Nombre descriptivo | Interfaz clara | Boundary bien definido |
| **Verificación** | CC ≤ 10 | LCOM ≤ 1, CBO ≤ 5 | Ciclos = 0 |

---

## Diseño Limpio es el Puente

```
Código Limpio         Diseño Limpio           Arquitectura Limpia
(funciones)      →    (módulos)          →    (componentes)

Legible                Modificable              Sostenible
```

**Sin diseño limpio, tenés:**
- Código hermoso que no escala
- Arquitectura bien pensada imposible de implementar

**Con diseño limpio, tenés:**
- Código que se puede leer **y** modificar
- Arquitectura que se puede implementar **y** evolucionar

---

## Lecturas Recomendadas

1. **Martin, R.C. (2002)**. *Agile Software Development: Principles, Patterns, and Practices*. Capítulos 7-12 (Principios SOLID).
2. **Fowler, M. (1999)**. *Refactoring: Improving the Design of Existing Code*. Capítulo 3 (Code Smells).
3. **Evans, E. (2003)**. *Domain-Driven Design*. Capítulos 2-4 (Layered Architecture, Entities, Value Objects).
4. **Parnas, D.L. (1972)**. "On the Criteria To Be Used in Decomposing Systems into Modules". *CACM*.

---

[← Volver a Trilogía Limpia](README.md)
