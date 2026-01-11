# Acoplamiento

> Larry Constantine, 1968

**Pregunta guía:** *¿Qué tan independientes son los módulos entre sí?*

---

## Definición

El grado en que un módulo depende de otros. Bajo acoplamiento significa que los módulos pueden cambiar, probarse y reusarse de forma independiente.

---

## Por qué importa

Alto acoplamiento significa que un cambio en un módulo fuerza cambios en otros. El sistema se vuelve rígido. Modificar algo simple requiere tocar muchos archivos.

El bajo acoplamiento permite:
- Cambiar un módulo sin afectar otros
- Probar módulos de forma aislada
- Reusar módulos en otros proyectos
- Entender un módulo sin entender todo el sistema

---

## En Código

A nivel de funciones y clases:

- **Parámetros** en lugar de variables globales
- **Inyección de dependencias** en lugar de instanciación directa
- **Interfaces** en lugar de clases concretas

```python
# Mal: alto acoplamiento
class Pedido:
    def guardar(self):
        db = PostgresDatabase()  # Depende de implementación concreta
        db.insert(self)

# Bien: bajo acoplamiento
class Pedido:
    def guardar(self, repositorio):  # Recibe la dependencia
        repositorio.guardar(self)
```

---

## En Diseño

A nivel de módulos y paquetes:

- **Dependencias mínimas** entre módulos
- **Interfaces estables** entre paquetes
- **Dirección clara** de dependencias

```
# Mal: dependencias circulares
usuarios/ ←→ pedidos/

# Bien: dependencias en una dirección
pedidos/ → usuarios/
```

---

## En Arquitectura

A nivel de sistema:

- **Capas** que solo conocen la capa inferior
- **Servicios** comunicados por contratos
- **Eventos** para desacoplar productores de consumidores

```
Presentación  → Lógica de Negocio → Repositorios → Base de Datos
```

La presentación no sabe qué base de datos usamos.

---

## Tipos de Acoplamiento

De peor a mejor:

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| **Contenido** | Modifica internos de otro | Acceder a `_private` |
| **Común** | Comparten variables globales | Singletons mutables |
| **Control** | Uno controla flujo del otro | Flags que cambian comportamiento |
| **Datos** | Solo comparten datos necesarios | Parámetros simples |
| **Mensaje** | Comunicación por mensajes | Eventos, colas |

**Objetivo:** acoplamiento de datos o mensaje.

---

## Métricas

| Métrica | Qué mide | Umbral |
|---------|----------|--------|
| CBO | Coupling Between Objects | ≤ 5 |
| Ca | Afferent (quién me usa) | Alto = reuso |
| Ce | Efferent (a quién uso) | ≤ 10 |

**Herramientas:** `pydeps`, `pylint`, `import-linter`

---

## Anti-patrones

### Dependencias Circulares
A depende de B, B depende de A. No se pueden separar.

### Shotgun Surgery
Un cambio requiere modificar muchos módulos.

### God Object
Un objeto que todos conocen y del que todos dependen.

---

## Ejemplo

```python
# Alto acoplamiento
class GestorPedidos:
    def confirmar(self, pedido):
        smtp = SmtpClient("mail.server.com")
        smtp.send(pedido.email, "Confirmado")

# Bajo acoplamiento
class GestorPedidos:
    def __init__(self, notificador):
        self.notificador = notificador

    def confirmar(self, pedido):
        self.notificador.notificar(pedido, "Confirmado")
```

El gestor no sabe si es email, SMS o paloma mensajera.

---

[← Volver a Fundamentos](README.md)
