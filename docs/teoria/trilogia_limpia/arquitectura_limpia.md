# Arquitectura Limpia

> *"La arquitectura es sobre intención, no sobre frameworks."*
> — **Robert C. Martin**, Clean Architecture (2017)

**Pregunta ética:** *¿Puede el sistema evolucionar?*

**Nivel Macro:** Componentes, capas, dependencias

---

## Definición

La arquitectura limpia organiza el sistema en componentes independientes con dependencias explícitas y unidireccionales. Permite que el sistema crezca, cambie y dure décadas.

**No es:** elegir frameworks de moda o dibujar diagramas bonitos.

**Es:** tomar decisiones de diseño que permitan cambiar lo periférico sin tocar lo esencial.

---

## Por Qué Importa

La arquitectura determina si un sistema muere en 2 años o vive 20. No se ve en el primer sprint. Se sufre (o se agradece) en el año 5.

**Mala arquitectura:** cada cambio requiere reescribir medio sistema.

**Buena arquitectura:** cada cambio se localiza en un componente específico.

### En la Era de la IA

La IA puede generar componentes completos en minutos. Pero no sabe:
- Dónde poner los boundaries entre componentes
- Qué depende de qué
- Cuál es la dirección correcta de las dependencias

**Tu responsabilidad: diseñar la estructura que hace sostenible lo generado.**

---

## Los Tres Principios de Arquitectura Limpia

### 1. Separación en Capas

El sistema se divide en capas concéntricas. Las dependencias apuntan **hacia adentro**.

```
┌───────────────────────────────────────────────┐
│          Frameworks y Drivers                 │  ← Externo
│    (Web, DB, UI, Devices)                     │
├───────────────────────────────────────────────┤
│       Interface Adapters                      │
│    (Controllers, Presenters, Gateways)        │
├───────────────────────────────────────────────┤
│         Casos de Uso                          │
│    (Application Business Rules)               │
├───────────────────────────────────────────────┤
│          Entidades                            │  ← Interno
│    (Enterprise Business Rules)                │
└───────────────────────────────────────────────┘

        Dependencias apuntan →  hacia adentro
```

**Regla de Dependencia:**
> El código en un círculo interno **nunca** debe conocer nada del círculo externo.

**Ejemplo:**
```python
# Bien: Entidad no conoce frameworks
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def is_valid(self):
        return "@" in self.email

# Mal: Entidad acoplada a Flask
class User(db.Model):  # ¡Violación! Entidad depende de framework
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
```

---

### 2. La Regla de Dependencia

**Principio:** Las dependencias de código fuente apuntan hacia las políticas de alto nivel.

```
    Detalles  →  Políticas
    (cambios frecuentes)  →  (cambios raros)

    UI        →  Casos de Uso  →  Entidades
    DB        →  Casos de Uso  →  Reglas de Negocio
    Framework →  Aplicación    →  Dominio
```

**Inversión de Dependencias (DIP):**

```python
# Mal: política depende de detalle
class OrderService:
    def process(self, order):
        mysql = MySQLDatabase()  # ¡Dependencia incorrecta!
        mysql.save(order)

# Bien: detalle depende de política
class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository  # Abstracción (política)

    def process(self, order):
        self.repository.save(order)

class MySQLOrderRepository(OrderRepository):
    def save(self, order):
        # Implementación concreta (detalle)
        pass
```

---

### 3. Boundaries (Fronteras)

Los boundaries separan componentes. Aislan cambios. Permiten testar independientemente.

**Tipos de boundaries:**

| Tipo | Ejemplo | Cuándo usar |
|------|---------|-------------|
| **API** | Interface / Protocol | Entre capas del mismo proceso |
| **Adaptador** | Gateway / Repository | Entre dominio y persistencia |
| **Servicio** | Microservicio | Entre bounded contexts |

**Ejemplo de boundary:**

```python
# Boundary: interfaz (Protocol)
class PaymentGateway(Protocol):
    def charge(self, amount: float, token: str) -> bool:
        pass

# Dominio usa la abstracción
class CheckoutService:
    def __init__(self, payment: PaymentGateway):
        self.payment = payment

    def complete_order(self, order):
        success = self.payment.charge(order.total, order.token)
        return success

# Implementaciones concretas (detalles)
class StripeGateway(PaymentGateway):
    def charge(self, amount, token):
        # Llamada a API de Stripe
        pass

class MercadoPagoGateway(PaymentGateway):
    def charge(self, amount, token):
        # Llamada a API de MercadoPago
        pass
```

**Beneficio:** cambiar de Stripe a MercadoPago no toca `CheckoutService`.

---

## Las Cuatro Capas Clásicas

### 1. Entidades (Enterprise Business Rules)

**Qué son:** Reglas de negocio que son verdad independientemente de la aplicación.

**Ejemplo:**
```python
class LoanApplication:
    def __init__(self, amount, applicant):
        self.amount = amount
        self.applicant = applicant

    def is_approvable(self):
        # Regla de negocio: no prestar más del 40% del ingreso
        return self.amount <= self.applicant.monthly_income * 0.4
```

**No dependen de:** UI, DB, frameworks. Son pura lógica de dominio.

---

### 2. Casos de Uso (Application Business Rules)

**Qué son:** Orquestación específica de la aplicación. "Cómo se hace X en este sistema".

**Ejemplo:**
```python
class ApplyForLoan:
    def __init__(self, loan_repo, notifier):
        self.loan_repo = loan_repo
        self.notifier = notifier

    def execute(self, request):
        loan = LoanApplication(request.amount, request.applicant)

        if not loan.is_approvable():
            return Response(success=False, reason="Exceeds income ratio")

        self.loan_repo.save(loan)
        self.notifier.send_confirmation(request.applicant)

        return Response(success=True, loan_id=loan.id)
```

**Dependen de:** Entidades (inner).
**No dependen de:** UI, DB (outer).

---

### 3. Interface Adapters

**Qué son:** Traductores entre la aplicación y el mundo externo.

**Tipos:**
- **Controllers:** traducen HTTP → Casos de Uso
- **Presenters:** traducen Casos de Uso → JSON/HTML
- **Gateways:** traducen Casos de Uso → DB/APIs externas

**Ejemplo - Controller:**
```python
class LoanController:
    def __init__(self, use_case: ApplyForLoan):
        self.use_case = use_case

    def post(self, http_request):
        # Traduce HTTP → Request del caso de uso
        request = LoanRequest(
            amount=http_request.json["amount"],
            applicant_id=http_request.json["applicant_id"]
        )

        response = self.use_case.execute(request)

        # Traduce Response → HTTP
        if response.success:
            return {"status": "approved", "loan_id": response.loan_id}, 200
        else:
            return {"status": "rejected", "reason": response.reason}, 400
```

---

### 4. Frameworks y Drivers

**Qué son:** Detalles concretos. Web frameworks, ORMs, librerías.

**Ejemplo:**
```python
# Flask (framework) - capa más externa
app = Flask(__name__)

@app.route("/loans", methods=["POST"])
def apply_loan():
    # Inyecta dependencias concretas
    repo = SQLAlchemyLoanRepository(db)
    notifier = SMTPNotifier()
    use_case = ApplyForLoan(repo, notifier)
    controller = LoanController(use_case)

    return controller.post(request)
```

**Objetivo:** que cambiar de Flask a FastAPI sea trivial.

---

## Métricas de Arquitectura Limpia

| Métrica | Qué mide | Umbral | Herramienta |
|---------|----------|--------|-------------|
| **Distancia desde la Secuencia Principal** | D = \|A + I - 1\| | ≤ 0.3 | Structure101 |
| **Violaciones de capa** | Imports que apuntan hacia afuera | 0 | `pydeps`, análisis custom |
| **Ciclos de dependencia** | Componentes que se importan mutuamente | 0 | `pydeps --show-cycles` |
| **Acoplamiento Aferente (Ca)** | Cuántos componentes dependen de este | Medido | `pydeps` |
| **Acoplamiento Eferente (Ce)** | De cuántos componentes depende este | ≤ 5 ideal | `pydeps` |

**Ejecutar:**
```bash
# Detectar ciclos
pydeps src/ --show-cycles

# Visualizar dependencias
pydeps src/ --max-bacon=3 -o deps.png

# Análisis custom de violaciones de capa
python scripts/check_layer_violations.py
```

---

## Principios de Componentes

### Cohesión de Componentes

**REP (Reuse/Release Equivalence):** Lo que se reusa junto, se libera junto.

**CCP (Common Closure Principle):** Clases que cambian juntas, van juntas.

**CRP (Common Reuse Principle):** No obligues a depender de lo que no usás.

**Ejemplo:**
```
# Mal: mezclar concerns en un componente
utils/
├── date_helpers.py
├── email_sender.py
├── pdf_generator.py

# Bien: separar por razón de cambio
date_utils/
└── helpers.py

notifications/
└── email_sender.py

reports/
└── pdf_generator.py
```

---

### Acoplamiento de Componentes

**ADP (Acyclic Dependencies Principle):** No ciclos en el grafo de dependencias.

```python
# Mal: ciclo
# users.py
from orders import Order

# orders.py
from users import User  # Ciclo!

# Bien: extraer abstracción compartida
# domain/entities.py
class User: pass
class Order: pass

# services/user_service.py
from domain.entities import User, Order
```

**SDP (Stable Dependencies Principle):** Depender de lo estable.

**SAP (Stable Abstractions Principle):** Lo estable debe ser abstracto.

---

## Patrones de Arquitectura

### Hexagonal (Ports & Adapters)

```
         ┌─────────────────────┐
         │   Driving Adapters  │ (HTTP, CLI)
         └──────────┬──────────┘
                    ↓
         ┌─────────────────────┐
         │    Application      │ (Casos de Uso)
         │       Core          │ (Entidades)
         └──────────┬──────────┘
                    ↓
         ┌─────────────────────┐
         │   Driven Adapters   │ (DB, Email, APIs)
         └─────────────────────┘
```

**Puertos:** interfaces que el core define.
**Adaptadores:** implementaciones concretas.

---

### Clean Architecture (Uncle Bob)

La versión de Martin de la arquitectura hexagonal, con énfasis en capas concéntricas.

**Ventaja:** independencia de frameworks, testabilidad, cambios localizados.

---

### Event-Driven Architecture

**Cuándo:** sistema con múltiples bounded contexts que necesitan comunicarse.

```python
# Componente 1: Publica evento
class OrderPlaced(Event):
    order_id: str
    total: float

order_service.place_order(order)
event_bus.publish(OrderPlaced(order.id, order.total))

# Componente 2: Escucha evento
@event_bus.subscribe(OrderPlaced)
def send_confirmation(event):
    emailer.send(f"Order {event.order_id} confirmed")
```

**Beneficio:** componentes desacoplados en tiempo.

---

## Arquitectura Limpia con IA

### Prompt para arquitectura

```
"Diseñar arquitectura para sistema de préstamos con:
- Arquitectura hexagonal (ports & adapters)
- 3 capas: Entidades → Casos de Uso → Adapters
- Boundaries claros entre capas
- Inversión de dependencias (DIP)
- Componentes:
  * LoanApplication (entidad)
  * ApplyForLoan (caso de uso)
  * LoanRepository (puerto)
  * SQLLoanRepository (adaptador)
  * LoanController (adaptador HTTP)
- Sin ciclos de dependencia
- Type hints en puertos"
```

### Verificar arquitectura generada

1. **Dibujar diagrama de dependencias:** `pydeps src/`
2. **Detectar ciclos:** `pydeps --show-cycles`
3. **Verificar regla de dependencia:** capas internas no importan externas
4. **Medir distancia:** componentes estables son abstractos

**Checklist:**
- [ ] ¿Las entidades dependen de cero frameworks?
- [ ] ¿Los casos de uso dependen solo de entidades y puertos?
- [ ] ¿Los adaptadores implementan puertos definidos en capas internas?
- [ ] ¿Puedo cambiar de framework sin tocar casos de uso?

---

## Anti-patrones de Arquitectura

### 1. Big Ball of Mud

**Síntoma:** No hay estructura. Todo depende de todo.

**Solución:** Identificar bounded contexts y separar en módulos.

---

### 2. Arquitectura Centrada en Base de Datos

**Síntoma:** La estructura del sistema sigue la estructura de la DB.

```python
# Mal: entidad es un modelo de DB
class User(db.Model):
    __tablename__ = "users"
    # Todo está acoplado al ORM
```

**Solución:** Entidades puras, mappers separados.

---

### 3. Framework Coupling

**Síntoma:** Lógica de negocio embebida en controllers de Flask/Django.

```python
# Mal
@app.route("/orders", methods=["POST"])
def create_order():
    # 50 líneas de lógica de negocio aquí
    pass
```

**Solución:** Controller delgado, lógica en casos de uso.

---

### 4. Dependency Cycles

**Síntoma:** A → B → C → A

**Consecuencia:** imposible testear componentes por separado.

**Solución:** Invertir una dependencia o extraer abstracción.

---

## La Prueba del Framework

> *"Si cambiar de framework requiere reescribir la lógica de negocio, la arquitectura está mal."*

**Preguntas:**
- ¿Puedo cambiar de Flask a FastAPI sin tocar casos de uso? → Sí
- ¿Puedo cambiar de SQLAlchemy a MongoDB sin tocar entidades? → Sí
- ¿Puedo testear casos de uso sin levantar servidor web? → Sí

**Si alguna respuesta es "No", hay acoplamiento arquitectónico.**

---

## En los Tres Niveles

| Aspecto | Código | Diseño | Arquitectura |
|---------|--------|--------|--------------|
| **Unidad** | Función | Clase/Módulo | Componente/Servicio |
| **Cohesión** | Una cosa | Una responsabilidad | Un bounded context |
| **Acoplamiento** | Pocos params | Pocas deps | Pocas interfaces públicas |
| **Abstracción** | Nombre claro | Interface clara | Boundary bien definido |
| **Cambio** | Líneas | Archivos | Componentes |
| **Tiempo** | Minutos | Horas | Días/Semanas |

---

## Sostenibilidad a Largo Plazo

La arquitectura limpia no es sobre el primer sprint. Es sobre el año 5:

| Sin Arquitectura Limpia | Con Arquitectura Limpia |
|-------------------------|-------------------------|
| Velocity decrece con el tiempo | Velocity se mantiene estable |
| Cada cambio rompe algo inesperado | Cambios localizados |
| Imposible testear sin todo el stack | Tests rápidos, enfocados |
| Frameworks obsoletos = reescritura | Frameworks intercambiables |
| Desarrolladores huyen del proyecto | Desarrolladores entienden el sistema |

**La arquitectura es una inversión. Se paga hoy, se cobra en 3 años.**

---

## Evolución de la Arquitectura

La arquitectura no es estática. Evoluciona. Pero con reglas:

1. **Cambios periféricos:** fáciles (cambiar DB, UI)
2. **Cambios de casos de uso:** moderados (agregar feature)
3. **Cambios de entidades:** difíciles (cambiar reglas de negocio)

**El objetivo:** maximizar cambios tipo 1, minimizar tipo 3.

---

## Lecturas Recomendadas

1. **Martin, R.C. (2017)**. *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Capítulos completos.
2. **Fowler, M. (2002)**. *Patterns of Enterprise Application Architecture*. Capítulos 1-2, 9-11.
3. **Evans, E. (2003)**. *Domain-Driven Design*. Parte IV (Strategic Design).
4. **Vernon, V. (2013)**. *Implementing Domain-Driven Design*. Capítulo 4 (Architecture).
5. **Parnas, D.L. (1972)**. "On the Criteria To Be Used in Decomposing Systems into Modules". Paper fundacional.

---

[← Volver a Trilogía Limpia](README.md)
