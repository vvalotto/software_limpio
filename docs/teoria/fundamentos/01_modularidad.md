# Modularidad

> David Parnas, 1972

**Pregunta guía:** *¿Cómo dividir el sistema en partes manejables?*

---

## Definición

Dividir un sistema en partes independientes que se pueden desarrollar, probar y modificar por separado. Cada parte es un **módulo**: una unidad con una responsabilidad clara y una interfaz definida.

---

## Por qué importa

Un sistema sin módulos es un bloque monolítico. Cualquier cambio puede afectar cualquier parte. A medida que crece, se vuelve imposible de entender y mantener.

La modularidad permite:
- Trabajar en una parte sin entender todo el sistema
- Cambiar una parte sin romper otras
- Reusar partes en otros contextos
- Distribuir el trabajo entre personas o equipos

---

## En Código

A nivel de funciones y clases:

- **Funciones pequeñas** que hacen una sola cosa
- **Clases enfocadas** en una responsabilidad
- **Archivos** que agrupan código relacionado

```python
# Mal: función que hace todo
def procesar_pedido(datos):
    # validar (50 líneas)
    # calcular (80 líneas)
    # guardar (40 líneas)
    # notificar (30 líneas)
    pass

# Bien: funciones separadas
def validar_pedido(datos): ...
def calcular_total(pedido): ...
def guardar_pedido(pedido): ...
def notificar_cliente(pedido): ...
```

---

## En Diseño

A nivel de módulos y paquetes:

- **Paquetes** que agrupan clases relacionadas
- **Interfaces claras** entre módulos
- **Dependencias explícitas** y mínimas

```
pedidos/
├── validacion.py      # Reglas de validación
├── calculo.py         # Lógica de precios
├── persistencia.py    # Acceso a datos
└── notificacion.py    # Envío de emails
```

Cada módulo puede cambiar internamente sin afectar a los demás, siempre que mantenga su interfaz.

---

## En Arquitectura

A nivel de sistema:

- **Capas** que separan presentación, lógica y datos
- **Servicios** independientes que se comunican por contratos
- **Boundaries** claros entre subsistemas

```
┌─────────────────────────────────┐
│         Presentación            │
├─────────────────────────────────┤
│       Lógica de Negocio         │
├─────────────────────────────────┤
│        Acceso a Datos           │
└─────────────────────────────────┘
```

Un cambio en la base de datos no debería requerir cambios en la interfaz de usuario.

---

## Métricas

| Métrica | Qué mide | Umbral sugerido |
|---------|----------|-----------------|
| LOC por módulo | Tamaño | ≤ 500 líneas |
| Funciones por módulo | Complejidad | ≤ 20 |
| Dependencias | Acoplamiento | ≤ 10 imports |

**Herramientas:** `radon`, `cloc`, `pydeps`

---

## Anti-patrones

### Big Ball of Mud
Sistema sin estructura. Todo depende de todo. Imposible modificar sin romper algo.

### God Module
Un módulo que hace demasiado. Conoce todo, controla todo. Crece sin límite.

### Dependencias Circulares
A depende de B, B depende de A. No se pueden usar por separado.

---

## El Criterio de Parnas

Parnas propuso que la división en módulos no debe seguir el flujo del programa, sino las **decisiones de diseño que podrían cambiar**.

| Enfoque | Criterio | Problema |
|---------|----------|----------|
| Tradicional | Pasos del algoritmo | Cambios afectan múltiples módulos |
| Parnas | Decisiones a ocultar | Cambios contenidos en un módulo |

Cada módulo oculta una decisión. Si esa decisión cambia, solo cambia ese módulo.

---

## Ejemplo

Sistema de facturación:

```
facturacion/
├── parser.py          # Oculta: formato de entrada
├── calculadora.py     # Oculta: reglas de cálculo
├── impuestos.py       # Oculta: lógica impositiva
├── formateador.py     # Oculta: formato de salida
└── persistencia.py    # Oculta: tipo de base de datos
```

Si cambia el formato de entrada (JSON a XML), solo cambia `parser.py`. El resto del sistema no se entera.

---

[← Volver a Fundamentos](README.md)
