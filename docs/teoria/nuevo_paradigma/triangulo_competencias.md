# El Triángulo de Competencias

> *"Principios sin métricas son dogma. Métricas sin principios son números vacíos. IA sin ambos es caos productivo."*

**La integración que la literatura no enseña**

---

## El Problema de la Separación

La formación tradicional en software enseña tres cosas por separado:

1. **Principios de diseño** (en libros de arquitectura)
2. **Métricas de calidad** (en libros de testing)
3. **Herramientas de IA** (en tutoriales de prompts)

**Resultado:** profesionales que saben de todo pero no integran nada.

- Leen sobre cohesión, pero no la miden
- Usan métricas, pero no saben qué principio violan
- Generan código con IA, pero no verifican si cumple principios ni umbrales

**La fragmentación produce código que funciona pero no escala.**

---

## El Triángulo

Los tres vértices no son independientes. Forman un **sistema**:

```
           PRINCIPIOS
          (qué y por qué)
               ▲
              ╱ ╲
             ╱   ╲
            ╱     ╲
           ╱       ╲
          ╱         ╲
    MÉTRICAS ◄────► IA
  (verificación)  (herramienta)
```

| Vértice | Función | Sin los otros |
|---------|---------|---------------|
| **Principios** | Guían el diseño | Subjetividad, opiniones |
| **Métricas** | Verifican objetivamente | Números sin significado |
| **IA** | Acelera la generación | Código rápido pero frágil |

**Juntos, crean un ciclo de mejora continua.**

---

## 1. Principios: El "Qué" y el "Por Qué"

### Definición

Los fundamentos universales que definen calidad:
- **Modularidad:** dividir en partes manejables
- **Cohesión:** cada parte hace una cosa
- **Acoplamiento:** minimizar dependencias entre partes
- **Ocultamiento:** esconder decisiones de diseño
- **Separación de concerns:** no mezclar responsabilidades
- **Abstracción:** trabajar con conceptos, no detalles

### Por qué son el vértice superior

Sin principios, no hay criterio. Las métricas miden, pero no explican **por qué** algo está mal. La IA genera, pero no sabe **qué** es calidad.

Los principios son el marco conceptual que da sentido a todo lo demás.

### El riesgo sin métricas ni IA

- **Subjetividad total:** "me parece cohesivo"
- **Debates interminables:** "para mí está bien acoplado"
- **Sin verificación:** no hay forma de demostrar cumplimiento

---

## 2. Métricas: La Verificación Objetiva

### Definición

Medidas cuantitativas que traducen principios a números:

| Principio | Métrica | Umbral |
|-----------|---------|--------|
| Cohesión | LCOM | ≤ 1 |
| Acoplamiento | CBO | ≤ 5 |
| Modularidad | LOC por módulo | ≤ 500 |
| Complejidad | Ciclomática | ≤ 10 |
| Abstracción | Distance from main sequence | ≤ 0.3 |

### Por qué son esenciales

Las métricas convierten principios abstractos en criterios verificables. No es "¿te parece cohesivo?", es "LCOM = 0.8, cumple el umbral".

**Objetividad reemplaza opinión.**

### El riesgo sin principios ni IA

- **Fetichismo de números:** optimizar métricas sin entender qué principio representan
- **Gaming the system:** alterar código solo para pasar umbrales sin mejorar diseño
- **Métricas sin significado:** medir todo, entender nada

---

## 3. IA: La Herramienta Aceleradora

### Definición

La capacidad de generar código a partir de descripciones en lenguaje natural, acelerando la implementación.

### Por qué no es suficiente sola

La IA genera lo que le pedís. Si no sabés qué pedirle (principios) ni cómo verificarlo (métricas), generarás código rápido pero frágil.

**La IA amplifica tu criterio. Si no tenés criterio, amplifica el caos.**

### El riesgo sin principios ni métricas

- **Código funcional pero inmantenible:** pasa los tests, falla en producción 6 meses después
- **Deuda técnica a escala industrial:** generar 1000 líneas malas es más rápido que 100 buenas
- **Delegación ciega:** "la IA lo hizo, no sé cómo funciona"

---

## La Integración: El Flujo de Trabajo

Los tres vértices se conectan en un **ciclo iterativo**:

### Paso 1: Principio → Prompt (IA)

Traducís el principio a restricciones en el prompt.

**Ejemplo:**

```
Principio: Alta cohesión
    ↓
Prompt: "Crear clase User que solo maneje autenticación.
         No incluir lógica de perfil ni notificaciones.
         LCOM ≤ 1"
```

### Paso 2: IA → Código

La IA genera el código siguiendo las restricciones.

```python
class User:
    def __init__(self, username, password):
        self.username = username
        self._password_hash = self._hash(password)

    def authenticate(self, password):
        return self._password_hash == self._hash(password)

    def _hash(self, password):
        # ...
        pass
```

### Paso 3: Código → Métricas

Ejecutás herramientas para verificar cumplimiento.

```bash
radon cc user.py
# Resultado: Complejidad = 3 (cumple ≤ 10)

pylint user.py --disable=all --enable=too-many-instance-attributes
# Resultado: LCOM = 0 (cumple ≤ 1)
```

### Paso 4: Métricas → Principio (Feedback)

Si las métricas fallan, sabés **qué principio se violó** y cómo corregirlo.

```
LCOM = 2.5 (falla)
    ↓
Violación: Baja cohesión
    ↓
Corrección: Separar responsabilidades
    ↓
Nuevo prompt: "Dividir User en Authenticator y Profile"
```

### Ciclo completo

```
PRINCIPIO ──→ Prompt con restricciones
                      ↓
                     IA
                      ↓
                   CÓDIGO
                      ↓
                  MÉTRICAS
                      ↓
          ¿Cumple umbrales? ────→ SÍ ──→ Aceptar
                 ↓
                 NO
                 ↓
         Identificar principio violado
                 ↓
         Refinar prompt (volver a IA)
```

---

## Ejemplo Completo: Sistema de Pedidos

### Iteración 1

**Principio aplicado:** Separación de concerns

**Prompt:**
```
"Crear módulo pedidos.py que maneje:
- Validación de pedidos
- Cálculo de totales
- Persistencia en base de datos

Cohesión alta, complejidad ≤ 10 por función."
```

**Código generado por IA:**
```python
class Pedidos:
    def procesar(self, pedido):
        # validar (10 líneas)
        # calcular (15 líneas)
        # guardar (8 líneas)
        pass
```

**Métricas:**
```bash
radon cc pedidos.py
# procesar(): Complejidad = 14 (FALLA: umbral 10)
```

### Iteración 2

**Feedback de métrica → Principio:**
- Complejidad alta indica **baja separación de concerns**
- Una función hace demasiado

**Nuevo prompt:**
```
"Dividir Pedidos en tres clases:
- ValidadorPedidos (solo validación)
- CalculadorPedidos (solo cálculo)
- RepositorioPedidos (solo persistencia)

Cada clase con una responsabilidad. LCOM ≤ 1, complejidad ≤ 10."
```

**Código generado por IA:**
```python
class ValidadorPedidos:
    def validar(self, pedido):
        # complejidad = 4
        pass

class CalculadorPedidos:
    def calcular_total(self, pedido):
        # complejidad = 3
        pass

class RepositorioPedidos:
    def guardar(self, pedido):
        # complejidad = 2
        pass
```

**Métricas:**
```bash
radon cc pedidos.py
# ValidadorPedidos.validar(): 4 (PASA)
# CalculadorPedidos.calcular_total(): 3 (PASA)
# RepositorioPedidos.guardar(): 2 (PASA)

pylint pedidos.py
# LCOM = 0 en las tres clases (PASA)
```

**Decisión:** Aceptar diseño. Commitear.

---

## Por Qué Funciona la Integración

| Sin integración | Con integración |
|-----------------|-----------------|
| Principios abstractos sin verificar | Principios medibles |
| Métricas sin contexto | Métricas que explican qué principio se viola |
| IA genera sin criterio | IA dirigida por principios, verificada por métricas |
| Refactoring por intuición | Refactoring por feedback objetivo |
| Decisiones subjetivas | Decisiones basadas en evidencia |

---

## En los Tres Niveles

| Nivel | Principio | Métrica | Uso de IA |
|-------|-----------|---------|-----------|
| **Código** | Funciones cohesivas | Complejidad ≤ 10 | Generar funciones pequeñas |
| **Diseño** | Módulos desacoplados | CBO ≤ 5 | Separar responsabilidades |
| **Arquitectura** | Capas independientes | Ciclos = 0 | Diseñar boundaries |

---

## La Competencia Profesional

El profesional moderno no domina **un** vértice. Domina **la integración**:

1. **Conoce los principios** (qué es calidad y por qué importa)
2. **Usa las métricas** (cómo verificar objetivamente)
3. **Dirige la IA** (cómo acelerar sin sacrificar calidad)

**El triángulo no es teórico. Es el flujo de trabajo diario.**

---

## Anti-patrones: Vértices Aislados

### Solo Principios (Purista)

> "La cohesión es fundamental. Mi código es cohesivo."

**Problema:** No hay forma de demostrarlo. Es opinión.

### Solo Métricas (Fetichista)

> "Mi LCOM es 0.5, perfecto."

**Problema:** No sabe qué principio representa ni por qué importa.

### Solo IA (Delegador)

> "Le pedí a la IA que lo haga. Funciona."

**Problema:** No sabe si cumple principios. No verificó métricas. No asume responsabilidad.

---

## La Evolución de la Literatura

| Época | Enfoque | Qué falta |
|-------|---------|-----------|
| 1970s-1990s | Principios (Parnas, Dijkstra) | Sin métricas automatizadas |
| 2000s-2010s | Métricas + Principios | Sin IA para acelerar |
| 2020s | IA para generar código | Sin integración con principios ni métricas |
| **Ahora** | **Triángulo: Principios + Métricas + IA** | **Primera propuesta integral** |

**Software Limpio es el primer framework que integra sistemáticamente los tres vértices.**

---

## Cultivar la Integración

La integración se practica:

1. **Al diseñar:** Elegir principio → Traducir a restricción de prompt
2. **Al generar:** Pedir código con criterios explícitos
3. **Al verificar:** Ejecutar métricas automáticamente
4. **Al fallar:** Interpretar métrica → Identificar principio violado → Refinar
5. **Al aprobar:** Documentar: "Cumple cohesión (LCOM=0.8), complejidad (CC=6)"

---

## El Resultado

Un profesional que:
- No delega el criterio a la IA
- No confía en su intuición subjetiva
- No acepta código sin verificar
- **Itera hasta que principios, métricas y código convergen**

**El triángulo no es un modelo teórico. Es la nueva definición de profesionalismo.**

---

## Lecturas Recomendadas

1. **Martin, R.C. (2017)**. *Clean Architecture: A Craftsman's Guide to Software Structure and Design*.
2. **Forsgren, N. et al. (2018)**. *Accelerate: Building and Scaling High Performing Technology Organizations*.
3. **Tornhill, A. (2018)**. *Software Design X-Rays: Fix Technical Debt with Behavioral Code Analysis*.

---

[← Volver a Nuevo Paradigma](README.md)
