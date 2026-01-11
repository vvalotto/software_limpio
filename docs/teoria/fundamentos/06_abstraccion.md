# Abstracción

> Barbara Liskov, 1974

**Pregunta guía:** *¿Se separa el qué (comportamiento) del cómo (implementación)?*

---

## Definición

Definir interfaces que describen *qué* hace un componente sin revelar *cómo* lo hace. Los usuarios dependen del contrato, no de los detalles.

---

## Por qué importa

Sin abstracción, el código queda atado a implementaciones específicas. Cambiar un detalle interno requiere cambiar todos los usuarios.

La abstracción permite:
- Cambiar implementación sin afectar usuarios
- Tener múltiples implementaciones del mismo contrato
- Simplificar el uso (ocultar complejidad)
- Facilitar testing con implementaciones de prueba

---

## En Código

A nivel de funciones y clases:

- **Funciones** con nombres que describen qué hacen, no cómo
- **Clases abstractas** o protocolos que definen contratos
- **Métodos** que ocultan su implementación

```python
# Sin abstracción: expone el cómo
def ordenar_burbuja(lista):
    for i in range(len(lista)):
        for j in range(len(lista) - 1):
            if lista[j] > lista[j + 1]:
                lista[j], lista[j + 1] = lista[j + 1], lista[j]

# Con abstracción: solo el qué
def ordenar(lista):
    """Ordena la lista de menor a mayor."""
    return sorted(lista)

# El usuario no sabe (ni le importa) qué algoritmo usa
```

---

## En Diseño

A nivel de módulos y paquetes:

- **Interfaces** que definen capacidades
- **Implementaciones** intercambiables
- **Inversión de dependencias**: depender de abstracciones

```python
# Abstracción
from abc import ABC, abstractmethod

class Repositorio(ABC):
    @abstractmethod
    def guardar(self, entidad): ...

    @abstractmethod
    def buscar(self, id): ...

# Implementaciones
class RepositorioSQL(Repositorio):
    def guardar(self, entidad): ...
    def buscar(self, id): ...

class RepositorioEnMemoria(Repositorio):
    def guardar(self, entidad): ...
    def buscar(self, id): ...

# El código de negocio usa Repositorio, no sabe cuál
```

---

## En Arquitectura

A nivel de sistema:

- **APIs** que exponen capacidades abstractas
- **Contratos** entre servicios
- **Puertos y adaptadores**: el dominio define interfaces, la infraestructura las implementa

```
┌─────────────────────────────────────────┐
│              Dominio                    │
│   ┌─────────────────────────────────┐   │
│   │  Puerto: Repositorio            │   │ ← Abstracción
│   └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
              ▲               ▲
              │               │
┌─────────────┴───┐   ┌───────┴─────────┐
│ Adaptador SQL   │   │ Adaptador Mongo │  ← Implementaciones
└─────────────────┘   └─────────────────┘
```

---

## Niveles de Abstracción

| Nivel | Ejemplo |
|-------|---------|
| **Alto** | "Procesar pedido" |
| **Medio** | "Validar stock, calcular total, reservar" |
| **Bajo** | "SELECT * FROM productos WHERE id = ?" |

El código debe operar en un nivel consistente. No mezclar.

---

## Métricas

| Métrica | Qué indica |
|---------|------------|
| I (Inestabilidad) | Qué tan fácil es cambiar |
| A (Abstracción) | Proporción de interfaces vs clases concretas |
| D (Distancia) | Qué tan lejos de la línea principal (I + A = 1) |

**Zona de dolor**: A bajo, I bajo (difícil de cambiar, difícil de extender)

**Herramientas:** análisis de dependencias, `pydeps`

---

## Anti-patrones

### Abstracción Prematura
Crear interfaces antes de tener múltiples implementaciones. Complejidad sin beneficio.

### Abstracción Filtrada
La abstracción expone detalles de implementación. El usuario debe conocer el "cómo".

### Jerarquías Profundas
Demasiados niveles de abstracción. Difícil seguir el flujo.

---

## La Regla

> *"Programar contra interfaces, no contra implementaciones."*

El código cliente no debe saber qué implementación usa. Solo que cumple el contrato.

---

## Ejemplo

Sistema de pagos:

```python
# Abstracción
class ProcesadorPago(ABC):
    @abstractmethod
    def cobrar(self, monto: float, tarjeta: str) -> bool: ...

# Implementaciones
class ProcesadorStripe(ProcesadorPago):
    def cobrar(self, monto, tarjeta):
        # Lógica específica de Stripe
        return stripe.charge(monto, tarjeta)

class ProcesadorMercadoPago(ProcesadorPago):
    def cobrar(self, monto, tarjeta):
        # Lógica específica de MercadoPago
        return mp.pay(monto, tarjeta)

# Uso: el servicio no sabe cuál es
class ServicioPedidos:
    def __init__(self, procesador: ProcesadorPago):
        self.procesador = procesador

    def finalizar(self, pedido):
        self.procesador.cobrar(pedido.total, pedido.tarjeta)
```

Mañana cambiamos de Stripe a MercadoPago. El servicio no se entera.

---

[← Volver a Fundamentos](README.md)
