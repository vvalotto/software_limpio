# Cohesión

> Larry Constantine, 1968

**Pregunta guía:** *¿Qué tan enfocado está cada módulo en una responsabilidad?*

---

## Definición

Los elementos dentro de un módulo deben estar relacionados entre sí y trabajar hacia un propósito común. Un módulo cohesivo hace *una cosa* y la hace bien.

---

## Por qué importa

Un módulo con baja cohesión mezcla responsabilidades. Cambia por múltiples razones. Es difícil de entender, probar y reusar.

La alta cohesión permite:
- Entender el módulo leyendo su nombre
- Modificarlo por una sola razón
- Probarlo de forma aislada
- Reusarlo en otros contextos

---

## En Código

A nivel de funciones y clases:

- **Funciones** que hacen una sola cosa
- **Clases** donde todos los métodos usan los mismos atributos
- **Métodos** que operan sobre el estado del objeto

```python
# Mal: clase con baja cohesión
class Utilidades:
    def calcular_iva(self, monto): ...
    def enviar_email(self, destinatario, mensaje): ...
    def formatear_fecha(self, fecha): ...
    def comprimir_archivo(self, ruta): ...

# Bien: clases cohesivas
class CalculadorImpuestos:
    def calcular_iva(self, monto): ...
    def calcular_iibb(self, monto): ...

class Notificador:
    def enviar_email(self, destinatario, mensaje): ...
    def enviar_sms(self, numero, mensaje): ...
```

---

## En Diseño

A nivel de módulos y paquetes:

- **Módulos** que agrupan funcionalidad relacionada
- **Paquetes** con un tema claro
- **Dependencias internas** fuertes, externas débiles

```
# Mal: paquete sin cohesión
utils/
├── fechas.py
├── emails.py
├── impuestos.py
└── compresion.py

# Bien: paquetes cohesivos
impuestos/
├── calculador.py
└── tasas.py

notificaciones/
├── email.py
└── sms.py
```

---

## En Arquitectura

A nivel de sistema:

- **Servicios** con una responsabilidad de negocio
- **Bounded contexts** bien definidos
- **Microservicios** que hacen una cosa

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Usuarios   │  │   Pedidos    │  │    Pagos     │
│              │  │              │  │              │
│ - registro   │  │ - crear      │  │ - procesar   │
│ - login      │  │ - cancelar   │  │ - reembolsar │
│ - perfil     │  │ - historial  │  │ - consultar  │
└──────────────┘  └──────────────┘  └──────────────┘
```

Cada servicio tiene una razón de existir. No mezcla responsabilidades.

---

## Tipos de Cohesión

De peor a mejor:

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| **Coincidental** | Elementos sin relación | Clase `Utilidades` |
| **Lógica** | Hacen cosas similares pero no relacionadas | `ProcesadorArchivos` (PDF, XML, CSV) |
| **Temporal** | Se ejecutan juntos en el tiempo | `Inicializador` |
| **Procedural** | Parte del mismo proceso | `ValidarYGuardar` |
| **Comunicacional** | Operan sobre los mismos datos | `ReporteCliente` |
| **Secuencial** | Output de uno es input del otro | `ParserYValidador` |
| **Funcional** | Contribuyen a una única tarea | `CalculadorDescuentos` |

**Objetivo:** cohesión funcional.

---

## Métricas

| Métrica | Qué mide | Umbral |
|---------|----------|--------|
| LCOM | Lack of Cohesion of Methods | ≤ 1 |
| TCC | Tight Class Cohesion | ≥ 0.5 |
| LCC | Loose Class Cohesion | ≥ 0.5 |

**LCOM** cuenta cuántos pares de métodos no comparten atributos. Menor es mejor.

**Herramientas:** `pylint`, `radon`

---

## Anti-patrones

### Clase Dios
Una clase que hace todo. Cientos de métodos, miles de líneas. Nadie la entiende completa.

### Clase Utilidades
`StringUtils`, `DateUtils`, `Helpers`. Cajón de sastre sin cohesión.

### Feature Envy
Un método que usa más datos de otra clase que de la propia. Debería moverse.

---

## La Prueba

> *"Si no podés describir qué hace el módulo en una oración simple, probablemente tenga baja cohesión."*

- "Gestiona usuarios" → Cohesivo
- "Gestiona usuarios, envía emails y genera reportes" → No cohesivo

---

## Ejemplo

Sistema de e-commerce:

```python
# Baja cohesión: hace de todo
class GestorPedidos:
    def crear_pedido(self): ...
    def enviar_email_confirmacion(self): ...
    def calcular_impuestos(self): ...
    def generar_factura_pdf(self): ...
    def actualizar_stock(self): ...

# Alta cohesión: cada clase hace una cosa
class Pedidos:
    def crear(self): ...
    def cancelar(self): ...
    def consultar(self): ...

class NotificadorPedidos:
    def confirmar(self, pedido): ...
    def notificar_envio(self, pedido): ...

class Facturador:
    def generar(self, pedido): ...
```

---

[← Volver a Fundamentos](README.md)
