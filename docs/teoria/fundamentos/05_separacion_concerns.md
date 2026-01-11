# Separación de Concerns

> Edsger Dijkstra, 1974

**Pregunta guía:** *¿Cada módulo aborda un solo aspecto del problema?*

---

## Definición

Dividir un programa de modo que cada parte aborde una *preocupación* (concern) distinta. Una preocupación es un aspecto del problema: la lógica de negocio, la persistencia, la presentación.

---

## Por qué importa

Cuando mezclamos preocupaciones, los cambios se complican. Modificar la interfaz afecta la base de datos. Cambiar una regla de negocio rompe la presentación.

La separación permite:
- Cambiar un aspecto sin afectar otros
- Especializar equipos por área
- Probar cada aspecto de forma aislada
- Reusar aspectos en diferentes contextos

---

## En Código

A nivel de funciones y clases:

- **Funciones puras** sin efectos secundarios
- **Clases** que no mezclan lógica con I/O
- **Separar** cálculo de presentación

```python
# Mal: mezcla cálculo con presentación
def procesar_venta(items):
    total = sum(i.precio for i in items)
    iva = total * 0.21
    print(f"Subtotal: ${total}")
    print(f"IVA: ${iva}")
    print(f"Total: ${total + iva}")

# Bien: separar concerns
def calcular_venta(items):
    total = sum(i.precio for i in items)
    iva = total * 0.21
    return {"subtotal": total, "iva": iva, "total": total + iva}

def mostrar_venta(resultado):
    print(f"Subtotal: ${resultado['subtotal']}")
    print(f"IVA: ${resultado['iva']}")
    print(f"Total: ${resultado['total']}")
```

---

## En Diseño

A nivel de módulos y paquetes:

- **Módulos separados** por responsabilidad
- **Capas** claramente definidas
- **Interfaces** entre preocupaciones

```
proyecto/
├── dominio/          # Reglas de negocio
│   ├── entidades.py
│   └── servicios.py
├── infraestructura/  # Detalles técnicos
│   ├── database.py
│   └── api_externa.py
└── presentacion/     # Interfaz de usuario
    ├── cli.py
    └── web.py
```

---

## En Arquitectura

A nivel de sistema:

- **Capas horizontales**: presentación, negocio, datos
- **Cortes verticales**: features o bounded contexts
- **Aspectos transversales**: logging, seguridad, caching

```
┌────────────────────────────────────────┐
│            Presentación                │
├────────────────────────────────────────┤
│          Lógica de Negocio             │
├────────────────────────────────────────┤
│            Persistencia                │
└────────────────────────────────────────┘
        ↑               ↑
     Logging        Seguridad
   (transversal)   (transversal)
```

---

## Concerns Comunes

| Concern | Responsabilidad |
|---------|-----------------|
| **Negocio** | Reglas del dominio |
| **Persistencia** | Guardar y recuperar datos |
| **Presentación** | Mostrar información |
| **Validación** | Verificar datos de entrada |
| **Logging** | Registrar eventos |
| **Seguridad** | Autenticación y autorización |
| **Caching** | Optimizar acceso a datos |

---

## Métricas

| Señal | Qué indica |
|-------|------------|
| Imports cruzados | Concerns mezclados |
| Clases con múltiples razones de cambio | Falta de separación |
| Tests que requieren infraestructura | Negocio mezclado con I/O |

**Herramientas:** `import-linter`, revisión de dependencias

---

## Anti-patrones

### Smart UI
La interfaz de usuario contiene lógica de negocio. Cambiar reglas requiere tocar pantallas.

### Anemic Domain
El dominio son solo datos. La lógica está esparcida en servicios, controladores, utilidades.

### Spaghetti
Todo mezclado. No hay límites claros entre preocupaciones.

---

## La Prueba

> *"¿Puedo cambiar cómo se muestra sin cambiar qué se calcula?"*

Si la respuesta es no, falta separación de concerns.

---

## Ejemplo

Sistema de reportes:

```python
# Mal: todo mezclado
def generar_reporte(datos):
    # Filtrado (negocio)
    filtrados = [d for d in datos if d.activo]
    # Cálculo (negocio)
    total = sum(d.monto for d in filtrados)
    # Formato (presentación)
    html = f"<h1>Reporte</h1><p>Total: ${total}</p>"
    # Guardado (persistencia)
    with open("reporte.html", "w") as f:
        f.write(html)

# Bien: concerns separados
def filtrar_activos(datos):
    return [d for d in datos if d.activo]

def calcular_total(datos):
    return sum(d.monto for d in datos)

def formatear_html(total):
    return f"<h1>Reporte</h1><p>Total: ${total}</p>"

def guardar_archivo(contenido, ruta):
    with open(ruta, "w") as f:
        f.write(contenido)
```

Ahora puedo cambiar el formato (PDF, JSON) sin tocar el cálculo.

---

[← Volver a Fundamentos](README.md)
