# El Rol Profesional

> *"El código se escribe una vez, se lee cien veces, se mantiene mil veces."*

**De programador a evaluador de calidad**

---

## El Cambio de Rol

La IA democratizó la generación de código. Ahora cualquiera puede pedirle a una máquina que escriba una función, una clase, un módulo completo. El código aparece en segundos.

Pero **el código generado no es código profesional** hasta que alguien:
- Lo evalúa contra principios
- Lo mide con métricas
- Lo refina hasta que cumple umbrales
- Decide si es apto para producción

Ese "alguien" es el nuevo profesional: **no quien escribe más rápido, sino quien evalúa mejor**.

---

## Las Cuatro Competencias

El profesional del software en la era IA domina cuatro capacidades:

| Competencia | Qué es | Herramienta |
|-------------|--------|-------------|
| **Dirigir** | Comunicar intención, contexto y restricciones | Prompts bien estructurados |
| **Evaluar** | Verificar calidad con criterios objetivos | Métricas automatizadas |
| **Refinar** | Iterar hasta cumplir los principios | Feedback de herramientas |
| **Decidir** | Asumir responsabilidad de diseño | Criterio profesional |

**No son secuenciales. Son cíclicas.**

---

## 1. Dirigir

### Definición

Proporcionar a la IA el contexto, las restricciones y los criterios de calidad que debe cumplir el código generado.

### Por qué importa

La IA no conoce tus principios. No sabe cuál es tu umbral de complejidad ciclomática, ni cuánto acoplamiento tolerás, ni qué nivel de cohesión esperás.

**Sin dirección clara, la IA genera código que funciona pero no escala, no se mantiene, no se entiende.**

### En la práctica

**Prompt sin dirección:**
```
"Crea una clase para gestionar usuarios"
```

**Prompt con dirección:**
```
"Crea una clase User en Python que:
- Maneje autenticación y perfil (dos responsabilidades)
- Tenga cohesión alta (LCOM ≤ 1)
- Complejidad ciclomática ≤ 10 por método
- Nombres descriptivos sin abreviaturas
- Docstrings en español rioplatense"
```

### Qué incluir en la dirección

- **Principios a respetar:** cohesión, acoplamiento, modularidad
- **Umbrales de métricas:** complejidad ≤ 10, líneas ≤ 20, LCOM ≤ 1
- **Convenciones:** nombres, idioma, formato
- **Restricciones:** librerías permitidas, patrones a usar o evitar

### Anti-patrón

**Delegación ciega:**
> "La IA sabe lo que hace. Si funciona, está bien."

**Resultado:** código que pasa tests pero viola todos los principios de diseño.

---

## 2. Evaluar

### Definición

Medir el código generado con métricas objetivas contra umbrales predefinidos. No es opinión, es verificación.

### Por qué importa

La sensación de que "está bien" es subjetiva. La complejidad ciclomática es objetiva. La cohesión es medible. El acoplamiento es cuantificable.

**Sin evaluación objetiva, la calidad depende del humor del revisor.**

### En la práctica

Después de generar código con IA, ejecutás:

```bash
# Complejidad ciclomática
radon cc src/ -a --total-average

# Cohesión (LCOM)
pylint src/ --disable=all --enable=too-many-instance-attributes

# Acoplamiento (dependencias)
pydeps src/ --max-bacon=2

# Maintainability Index
radon mi src/ --min=B
```

### Qué evaluar

| Nivel | Métrica | Herramienta |
|-------|---------|-------------|
| **Código** | Complejidad ciclomática | radon |
| **Código** | Líneas por función | radon |
| **Diseño** | LCOM (cohesión) | pylint, radon |
| **Diseño** | CBO (acoplamiento) | pydeps |
| **Diseño** | Maintainability Index | radon |
| **Arquitectura** | Ciclos de dependencias | pydeps |

### Anti-patrón

**Evaluación subjetiva:**
> "Me parece que está bien diseñado. Lo commiteo."

**Resultado:** deuda técnica acumulada, degradación gradual del sistema.

---

## 3. Refinar

### Definición

Iterar sobre el código usando las métricas como feedback hasta que cumpla los umbrales de calidad.

### Por qué importa

La primera generación rara vez es la óptima. La IA genera código funcional, no necesariamente limpio.

**El refinamiento es donde el profesional agrega valor**: toma el código que funciona y lo convierte en código que dura.

### En la práctica

**Ciclo de refinamiento:**

1. IA genera código inicial
2. Ejecutás métricas
3. Detectás violaciones (ej: complejidad 15, umbral 10)
4. Pedís a la IA refactorizar específicamente esa violación
5. Re-ejecutás métricas
6. Repetís hasta cumplir todos los umbrales

**Ejemplo:**

```python
# Primera generación: funciona, pero complejidad = 15
def procesar_pedido(pedido):
    if pedido.valido:
        if pedido.tiene_stock:
            if pedido.cliente.activo:
                if pedido.total > 0:
                    # ... 50 líneas más
                    pass

# Después del refinamiento: complejidad = 6
def procesar_pedido(pedido):
    validar_pedido(pedido)
    verificar_stock(pedido)
    verificar_cliente(pedido)
    calcular_total(pedido)
    guardar_pedido(pedido)
```

### Qué refinar

- **Complejidad alta:** extraer funciones
- **Baja cohesión:** separar responsabilidades
- **Alto acoplamiento:** invertir dependencias
- **Nombres vagos:** renombrar con intención clara
- **Funciones largas:** dividir en pasos

### Anti-patrón

**Aceptar la primera versión:**
> "Funciona y tengo que entregar. Lo arreglo después."

**Resultado:** nunca se arregla. Se acumula deuda técnica.

---

## 4. Decidir

### Definición

Tomar decisiones de diseño y arquitectura, y asumir la responsabilidad de sus consecuencias.

### Por qué importa

La IA puede generar múltiples soluciones. Puede proponer alternativas. Puede sugerir trade-offs. **Pero no puede decidir por vos.**

Decidir implica:
- Elegir entre opciones con trade-offs
- Priorizar un principio sobre otro en casos de conflicto
- Aceptar la responsabilidad de la elección

**La decisión es lo que no se puede delegar.**

### En la práctica

**Decisiones típicas:**

| Situación | Opciones | Trade-off |
|-----------|----------|-----------|
| Sistema de cache | In-memory vs Redis | Velocidad vs Persistencia |
| Arquitectura | Monolito vs Microservicios | Simplicidad vs Escalabilidad |
| Testing | Muchos tests unitarios vs E2E | Velocidad vs Realismo |
| Refactoring | Ahora vs Después | Calidad vs Tiempo |

**La IA puede listar opciones y consecuencias. Vos decidís.**

### Criterios para decidir

1. **Principios no negociables:** modularidad, cohesión, acoplamiento bajo
2. **Contexto del proyecto:** tamaño, equipo, criticidad
3. **Trade-offs explícitos:** qué ganás, qué perdés
4. **Reversibilidad:** qué tan fácil es cambiar después

### Anti-patrón

**Decisión por default:**
> "Le pregunto a la IA qué hacer y hago lo que diga."

**Resultado:** arquitectura inconsistente, sin visión coherente.

---

## El Ciclo Completo

Las cuatro competencias se integran en un flujo iterativo:

```
    DIRIGIR
       ↓
   (IA genera)
       ↓
    EVALUAR ──→ ¿Cumple? ──→ SÍ ──→ DECIDIR: Aceptar
       ↑            │
       │            NO
       │            ↓
       └───── REFINAR
```

**Ejemplo completo:**

1. **Dirigir:** "Crear módulo de autenticación. Cohesión alta, complejidad ≤ 10, LCOM ≤ 1"
2. **Evaluar:** radon cc auth/ → complejidad = 12 (falla)
3. **Refinar:** "Extraer validación a función separada"
4. **Evaluar:** radon cc auth/ → complejidad = 8 (pasa)
5. **Decidir:** "Acepto este diseño. Lo commiteo."

---

## De Programador a Evaluador

| Antes | Ahora |
|-------|-------|
| Escribir código | Dirigir IA |
| "Funciona" | Cumple métricas |
| Code review subjetivo | Evaluación objetiva |
| Refactoring opcional | Refinamiento obligatorio |
| Seguir órdenes | Tomar decisiones |

**El nuevo profesional no compite con la IA en velocidad de escritura. Compite en criterio de calidad.**

---

## En los Tres Niveles

| Nivel | Dirigir | Evaluar | Refinar | Decidir |
|-------|---------|---------|---------|---------|
| **Código** | Prompts con restricciones | radon, pylint | Extraer funciones | Aceptar o rechazar |
| **Diseño** | Principios de cohesión/acoplamiento | LCOM, CBO | Separar responsabilidades | Elegir estructura |
| **Arquitectura** | Patrones y boundaries | Ciclos, distancia | Invertir dependencias | Definir capas |

---

## Cultivar las Competencias

Las competencias se practican:

1. **Dirigir:** Escribí prompts con restricciones explícitas. No delegues el criterio.
2. **Evaluar:** Automatizá métricas en tu flujo de trabajo. No confíes en tu "ojo".
3. **Refinar:** Iterá al menos una vez. Nunca aceptes la primera versión.
4. **Decidir:** Documentá tus decisiones. Asumilas públicamente.

---

## La Responsabilidad Final

> *"Si tu nombre está en el commit, vos respondés por el código."*

La IA es una herramienta. Vos sos el profesional. La responsabilidad no se delega:
- Si el código rompe producción, es tu responsabilidad
- Si el diseño genera deuda técnica, es tu responsabilidad
- Si la arquitectura no escala, es tu responsabilidad

**Dirigir, evaluar, refinar y decidir no son opcionales. Son el núcleo de la profesión.**

---

## Lecturas Recomendadas

1. **Martin, R.C. (2008)**. *Clean Code: A Handbook of Agile Software Craftsmanship*.
2. **Forsgren, N. et al. (2018)**. *Accelerate: Building and Scaling High Performing Technology Organizations*.
3. **Evans, E. (2003)**. *Domain-Driven Design: Tackling Complexity in the Heart of Software*.

---

[← Volver a Nuevo Paradigma](README.md)
