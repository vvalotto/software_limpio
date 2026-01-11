# Ocultamiento de Información

> David Parnas, 1972

**Pregunta guía:** *¿Qué exponer y qué esconder de cada módulo?*

---

## Definición

Cada módulo debe ocultar sus decisiones internas y exponer solo lo necesario para usarlo. Los demás módulos no saben *cómo* funciona, solo *qué* hace.

---

## Por qué importa

Si un módulo expone sus detalles internos, cualquier cambio interno puede romper a quienes lo usan. Los usuarios del módulo quedan atados a decisiones que deberían poder cambiar.

El ocultamiento permite:
- Cambiar la implementación sin afectar a los usuarios
- Simplificar el uso (menos detalles que entender)
- Proteger invariantes internos
- Evolucionar el sistema sin reescribirlo

---

## En Código

A nivel de funciones y clases:

- **Funciones** que reciben parámetros y devuelven resultados, sin exponer estado interno
- **Atributos privados** que no se acceden directamente
- **Métodos públicos** que definen qué se puede hacer, no cómo

```python
# Mal: expone estructura interna
class Carrito:
    def __init__(self):
        self.items = []  # Cualquiera puede modificarlo

carrito.items.append(producto)  # Acceso directo

# Bien: oculta estructura
class Carrito:
    def __init__(self):
        self._items = []

    def agregar(self, producto):
        self._items.append(producto)

    def total(self):
        return sum(p.precio for p in self._items)
```

---

## En Diseño

A nivel de módulos y paquetes:

- **Interfaces públicas** bien definidas
- **Implementaciones** que pueden cambiar sin aviso
- **Contratos** que especifican comportamiento, no mecanismo

```python
# modulo_pagos/__init__.py
from .procesador import procesar_pago  # Solo esto es público

# modulo_pagos/procesador.py
def procesar_pago(monto, tarjeta):
    """Procesa un pago. Retorna True si fue exitoso."""
    # Internamente puede usar Stripe, MercadoPago, etc.
    # El usuario del módulo no lo sabe ni le importa
    return _gateway.cobrar(monto, tarjeta)
```

---

## En Arquitectura

A nivel de sistema:

- **APIs** que exponen capacidades, no implementación
- **Capas** que ocultan la capa inferior
- **Servicios** con contratos estables

```
┌─────────────────────────────────┐
│      API REST (público)         │  ← Solo esto ven los clientes
├─────────────────────────────────┤
│    Lógica de Negocio            │  ← Oculta reglas internas
├─────────────────────────────────┤
│    Repositorios                 │  ← Oculta tipo de base de datos
└─────────────────────────────────┘
```

El cliente de la API no sabe si usamos PostgreSQL o MongoDB. Podemos cambiar sin avisarle.

---

## Métricas

| Métrica | Qué indica | Señal de alerta |
|---------|------------|-----------------|
| Atributos públicos | Exposición | Muchos atributos públicos |
| Imports internos | Acoplamiento a detalles | Importar desde `_private` |
| Cambios en cascada | Falta de ocultamiento | Cambio interno rompe externos |

**Herramientas:** `pylint` (detecta acceso a `_private`), code review

---

## Anti-patrones

### Intimidad Inapropiada
Un módulo conoce demasiado sobre los internos de otro. Accede a atributos privados, depende de estructuras internas.

### Interfaz Gorda
Exponer todo "por las dudas". Una interfaz con 50 métodos cuando se usan 5.

### Getters y Setters para Todo
Exponer atributos con `get_x()` y `set_x()` no es ocultamiento. Es exposición con pasos extra.

---

## La Regla

> *"Un módulo debe saber lo mínimo necesario para hacer su trabajo."*

Si un módulo necesita saber cómo funciona otro por dentro, algo está mal. Debería bastar con saber qué hace.

---

## Ejemplo

Sistema de notificaciones:

```python
# Interfaz pública
class Notificador:
    def enviar(self, usuario, mensaje):
        """Envía una notificación al usuario."""
        ...

# El usuario del módulo no sabe si envía por:
# - Email
# - SMS
# - Push notification
# - Paloma mensajera

# Puede cambiar internamente sin afectar a nadie
```

Mañana cambiamos de proveedor de SMS. El código que usa `Notificador` no se entera.

---

[← Volver a Fundamentos](README.md)
