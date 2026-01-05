# Software Limpio

Repositorio de conocimiento sobre calidad de diseño de software en la era de la IA.

## Propósito

Completar la trilogía de Robert C. Martin (Clean Code, Clean Architecture) con **Clean Design**: los fundamentos de diseño que son independientes del paradigma de programación y anteriores a la orientación a objetos.

## Tesis Central

La IA transforma al profesional de software de "escritor de código" a **director y evaluador de calidad**, usando métricas como herramientas objetivas de verificación.

## Contenido

```
software_limpio/
├── teoria/           # Fundamentos de diseño limpio
├── metricas/         # Catálogo de métricas de calidad
├── agentes/          # Agentes de control de calidad (CodeGuard, DesignReviewer, ArchitectAnalyst)
└── ejemplos/         # Código de ejemplo con métricas aplicadas
```

## Fundamentos

Seis principios universales de diseño (paradigma-agnósticos):

1. **Cohesión** - Elementos relacionados juntos
2. **Acoplamiento** - Minimizar dependencias entre módulos
3. **Ocultamiento de información** - Exponer solo lo necesario
4. **Modularidad** - Dividir en partes manejables
5. **Abstracción** - Separar qué hace de cómo lo hace
6. **Separación de responsabilidades** - Una razón para cambiar

## Métricas

| Contexto | Métricas Core | Ejemplo |
|----------|---------------|---------|
| Código | 15 | CC ≤ 10, LOC/función ≤ 20 |
| Diseño | 20 | CBO ≤ 5, LCOM ≤ 1, MI > 20 |
| Arquitectura | 20 | D ≈ 0, Layer Violations = 0 |

## Agentes de Calidad

| Agente | Momento | Acción |
|--------|---------|--------|
| CodeGuard | Pre-commit | Advierte (no bloquea) |
| DesignReviewer | Review/PR | Bloquea si crítico |
| ArchitectAnalyst | Fin de sprint | Analiza tendencias |

## Herramientas Base

- `radon` - Complejidad y mantenibilidad
- `pylint` - Análisis estático
- `bandit` - Seguridad
- `pydeps` - Dependencias
- `coverage.py` - Cobertura de tests

## Estado

🚧 En construcción

## Autor

Víctor Valotto - FIUNER

## Licencia

MIT
