# Ticket 4.1 — Catálogo de Code Smells

**Fase:** 4 — Code Smells y SOLID
**Fecha:** 2026-02-20
**Estado:** ✅ Completado

---

## Objetivo

Definir el catálogo oficial de code smells a detectar en DesignReviewer v0.2.0:
cuáles detectar, qué principio SOLID violan, cómo detectarlos por AST,
severidad y fórmula de `estimated_effort`.

---

## Cambios de Infraestructura

### `models.py`
- Nuevo enum `SolidPrinciple` (S, O, L, I, D)
- Nuevos campos opcionales en `ReviewResult`:
  - `solid_principle: SolidPrinciple | None` — principio violado
  - `smell_type: str | None` — nombre del smell detectado

### `config.py`
Nuevos umbrales en `DesignReviewerConfig`:
| Campo | Default | Descripción |
|-------|---------|-------------|
| `max_god_object_methods` | 20 | Métodos públicos máximos por clase |
| `max_god_object_lines` | 300 | Líneas máximas por clase |
| `max_method_lines` | 20 | Líneas máximas por método |
| `max_parameters` | 5 | Parámetros máximos por método |
| `min_data_clump_size` | 3 | Mínimo de params para un Data Clump |
| `min_data_clump_occurrences` | 2 | Mínimo de apariciones para Data Clump |

---

## Catálogo de Smells

### 1. God Object
| Campo | Valor |
|-------|-------|
| **Analyzer** | `GodObjectAnalyzer` |
| **Archivo** | `god_object_analyzer.py` |
| **Principio SOLID** | S — Single Responsibility Principle |
| **Categoría** | `smells` |
| **Severidad** | CRITICAL |
| **Prioridad** | 1 |

**¿Qué detecta?**
Una clase que acumula demasiadas responsabilidades, medida por:
- Cantidad de métodos públicos > `max_god_object_methods` (default: 20)
- Líneas de código de la clase > `max_god_object_lines` (default: 300)

Se reporta si **cualquiera** de las dos condiciones se cumple.

**Estrategia AST:**
- Caminar `ClassDef` en el AST
- Contar métodos (`FunctionDef`/`AsyncFunctionDef`) que no empiezan con `__`
- Contar líneas: `class_node.end_lineno - class_node.lineno + 1`

**Fórmula de `estimated_effort`:**
```
exceso_metodos = max(0, metodos - max_god_object_methods)
exceso_lineas  = max(0, lineas - max_god_object_lines) // 50
effort = 3.0 + (exceso_metodos + exceso_lineas) * 0.5  # horas
```

**Mensaje:** `"Clase 'X' tiene N métodos y M líneas (umbrales: P métodos, Q líneas). Clase dios: acumula demasiadas responsabilidades."`
**Sugerencia:** `"Dividir 'X' aplicando SRP: extraer responsabilidades en clases separadas. Esfuerzo estimado: H horas."`

---

### 2. Long Method
| Campo | Valor |
|-------|-------|
| **Analyzer** | `LongMethodAnalyzer` |
| **Archivo** | `long_method_analyzer.py` |
| **Principio SOLID** | S — Single Responsibility Principle |
| **Categoría** | `smells` |
| **Severidad** | WARNING |
| **Prioridad** | 2 |

**¿Qué detecta?**
Métodos o funciones con más líneas de código que `max_method_lines` (default: 20).
Cuenta líneas de código reales: `func_node.end_lineno - func_node.lineno + 1`.

**Estrategia AST:**
- Caminar `FunctionDef`/`AsyncFunctionDef` en el AST
- Excluir funciones de menos de 2 líneas (triviales)
- Calcular largo: `end_lineno - lineno + 1`

**Fórmula de `estimated_effort`:**
```
exceso = lineas - max_method_lines
effort = round(exceso / 10 * 0.5, 1)  # 0.5h por cada 10 líneas de exceso
```

**Mensaje:** `"Método 'X.metodo' tiene N líneas (umbral: M). Método demasiado largo."`
**Sugerencia:** `"Extraer N-M líneas en métodos auxiliares con nombres descriptivos."`

---

### 3. Long Parameter List
| Campo | Valor |
|-------|-------|
| **Analyzer** | `LongParameterListAnalyzer` |
| **Archivo** | `long_parameter_list_analyzer.py` |
| **Principio SOLID** | I — Interface Segregation Principle |
| **Categoría** | `smells` |
| **Severidad** | WARNING |
| **Prioridad** | 2 |

**¿Qué detecta?**
Funciones/métodos con más parámetros que `max_parameters` (default: 5).
Excluye `self` y `cls`. No cuenta `*args`/`**kwargs` explícitos como parámetros adicionales.

**Estrategia AST:**
- Caminar `FunctionDef`/`AsyncFunctionDef`
- Extraer `args.args` excluyendo `self`/`cls`
- Contar también `args.posonlyargs`, `args.kwonlyargs`

**Fórmula de `estimated_effort`:**
```
exceso = cantidad - max_parameters
effort = round(exceso * 0.5, 1)  # 0.5h por parámetro de exceso
```

**Mensaje:** `"Función 'X.metodo' tiene N parámetros (umbral: M). Lista de parámetros demasiado larga."`
**Sugerencia:** `"Agrupar los N parámetros en un objeto Parameter Object o dataclass."`

---

### 4. Feature Envy
| Campo | Valor |
|-------|-------|
| **Analyzer** | `FeatureEnvyAnalyzer` |
| **Archivo** | `feature_envy_analyzer.py` |
| **Principio SOLID** | S — Single Responsibility Principle |
| **Categoría** | `smells` |
| **Severidad** | WARNING |
| **Prioridad** | 3 |

**¿Qué detecta?**
Un método que accede más a atributos/métodos de otro objeto (recibido como parámetro)
que a los propios (`self.X`). Indica que la lógica debería vivir en otra clase.

**Estrategia AST:**
- Por cada método de una clase: contar accesos `self.X` (propios)
- Contar accesos `param.X` donde `param` es un parámetro recibido (excluyendo `self`)
- Si el objeto más accedido externamente > accesos propios: reportar

**Condición de reporte:**
```
accesos_externos_max > accesos_propios AND accesos_externos_max >= 3
```
(mínimo 3 accesos externos para evitar falsos positivos)

**Fórmula de `estimated_effort`:**
```
effort = 1.5  # horas por método con Feature Envy
```

**Mensaje:** `"Método 'X.metodo' accede N veces a 'param' vs M veces a self. Posible Feature Envy."`
**Sugerencia:** `"Mover 'metodo' a la clase de 'param', o extraer la lógica a una función auxiliar."`

---

### 5. Data Clumps
| Campo | Valor |
|-------|-------|
| **Analyzer** | `DataClumpsAnalyzer` |
| **Archivo** | `data_clumps_analyzer.py` |
| **Principio SOLID** | S — Single Responsibility Principle |
| **Categoría** | `smells` |
| **Severidad** | WARNING |
| **Prioridad** | 3 |

**¿Qué detecta?**
Grupos de N parámetros que aparecen juntos en M o más funciones/métodos del archivo.
Indica que esos datos deberían encapsularse en un objeto.

**Parámetros:**
- `min_data_clump_size`: mínimo de params en el grupo (default: 3)
- `min_data_clump_occurrences`: mínimo de métodos donde aparece el grupo (default: 2)

**Estrategia AST:**
- Recolectar firmas de todas las funciones del archivo (listas de nombres de parámetros, excluyendo self/cls)
- Por cada combinación de N parámetros que aparece en M+ funciones: reportar como Data Clump
- Usar `itertools.combinations` sobre los conjuntos de parámetros

**Fórmula de `estimated_effort`:**
```
effort = 2.0  # horas por Data Clump detectado (crear la dataclass)
```

**Mensaje:** `"Data Clump: parámetros {a, b, c} aparecen juntos en N métodos. Considerar encapsularlos."`
**Sugerencia:** `"Crear una dataclass o namedtuple con los campos {a, b, c} y usarla como parámetro único."`

---

## Resumen del Catálogo

| Smell | SOLID | Severidad | Umbral principal | Effort aprox |
|-------|-------|-----------|-----------------|--------------|
| God Object | S | CRITICAL | 20 métodos / 300 líneas | 3h+ |
| Long Method | S | WARNING | 20 líneas | 0.5h/10líneas |
| Long Parameter List | I | WARNING | 5 parámetros | 0.5h/param |
| Feature Envy | S | WARNING | 3 accesos externos | 1.5h |
| Data Clumps | S | WARNING | 3 params en 2+ métodos | 2.0h |

---

## Tickets Siguientes

- **4.2** GodObjectAnalyzer + LongMethodAnalyzer
- **4.3** LongParameterListAnalyzer
- **4.4** FeatureEnvyAnalyzer
- **4.5** DataClumpsAnalyzer
- **4.6** Tests unitarios (todos los smells)
