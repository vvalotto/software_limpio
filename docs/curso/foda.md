# FODA — Software Limpio como Curso y Libro

Análisis de fortalezas, debilidades, oportunidades y amenazas de la iniciativa
de transformar el framework Software Limpio en un curso y, eventualmente, un libro.

*Generado: Marzo 2026*

---

## Fortalezas

**1. Hay una contribución conceptual genuina**
La trilogía de Martin tiene un agujero: nadie escribió "Diseño Limpio" (el nivel medio, entre funciones y arquitectura). Este proyecto lo llena con métricas concretas, principios fundamentados y una herramienta que lo valida. Eso no es una claim de marketing, es un vacío real en la literatura.

**2. La teoría tiene profundidad y rigor**
No es "5 tips para código limpio". Arranca en Parnas (1972), pasa por Dijkstra, conecta con Taleb, y termina en investigación reciente (DORA 2024, GitHub Research 2024). Eso distingue el material de la mayoría de los recursos técnicos que son instrumentales y superficiales.

**3. La herramienta existe y funciona**
El framework no es teoría prometida: son 766 tests, tres CLIs, métricas reales. Podés ejecutar `designreviewer src/` y ver los resultados. Eso le da credibilidad al material que un libro solo teórico no tiene.

**4. La coherencia del sistema es notable**
Teoría → Métricas → Herramienta → Guías de adopción. Todo está conectado. Un principio en `teoria/` tiene una métrica en `metricas/`, un check en el código, y una guía de cuándo actuar. Eso es exactamente lo que hace falta para que un estudiante entienda el *por qué* antes del *cómo*.

**5. Está en español**
El mercado hispanohablante tiene escasez severa de material técnico de calidad. "Clean Code" y "Clean Architecture" existen en inglés; las traducciones son mediocres. Un recurso original en español de este nivel es una ventaja real.

**6. El timing con la IA es perfecto**
El argumento central ("de escritores de código a evaluadores de calidad") responde exactamente la pregunta que toda la industria se está haciendo ahora. Es relevante y urgente.

---

## Debilidades

**1. Los docs actuales son referencia, no pedagogía**
Esta es la debilidad más importante. Los archivos de teoría son READMEs bien escritos, pero un curso necesita otro formato: secuencia de aprendizaje, ejercicios, ejemplos malos resueltos, evaluaciones. Transformar lo que existe en material pedagógico es trabajo significativo, no edición menor.

**2. No hay progresión didáctica**
Alguien puede leer `teoria/fundamentos/01_modularidad.md` y `guias/codeguard.md` sin que ninguno de los dos lo lleve al otro. La teoría y las herramientas viven en carpetas separadas. Un curso exige integración explícita: "acá está el principio, acá está la métrica que lo mide, acá está el código que lo viola".

**3. Los ejemplos son insuficientes**
El `sample_project` cubre CodeGuard y poco más. Para un curso necesitás material didáctico deliberado: código que viola principios de manera obvia y educativa, refactorizaciones comentadas, antes/después. Eso no existe todavía.

**4. La integración IA (v0.4.0) está pendiente**
El "Nuevo Paradigma" es una de las secciones más fuertes de la teoría, pero la herramienta todavía no lo implementa. Si se da el curso hoy, esa parte queda como promesa. Funciona para un curso inicial, pero limita el alcance.

**5. Los archivos de teoría son cortos para un libro**
Los READMEs de subsecciones tienen 100-140 líneas. Para un libro, cada uno de esos temas necesita al menos 3-5 veces más desarrollo: ejemplos extendidos, casos reales, comparaciones, profundización. La estructura existe, el contenido necesita crecer.

---

## Oportunidades

**1. El mercado hispanohablante está desatendido**
PyCon Latam, PyAr, comunidades universitarias en toda la región necesitan este material. El mercado de cursos técnicos en español es grande y con poca competencia de calidad.

**2. El framework puede ser la "demostración viva" del curso**
Lo que se enseña se puede mostrar ejecutando las herramientas en tiempo real. Eso es una ventaja pedagógica que un libro solo teórico no tiene. La herramienta es el laboratorio del curso.

**3. Adopción académica**
Las carreras de ingeniería y sistemas en universidades latinoamericanas necesitan material actualizado en español sobre calidad de software. Este framework podría entrar como herramienta de cátedra. Es un vector de distribución que los libros técnicos comerciales no suelen explorar.

**4. Modelo de negocio probado**
Curso → libro → certificación → consultoría. Otros autores técnicos construyeron carreras con este modelo (Fowler, Feathers, Vernon). El orden importa: el curso valida el material antes de invertir en el libro.

**5. El framework publicado en PyPI baja la barrera**
Cuando v0.4.0 esté en PyPI, instalar la herramienta es `pip install quality-agents`. Eso facilita enormemente la adopción en cursos y reduce la fricción de "cómo lo pongo a funcionar".

---

## Amenazas

**1. El alcance es ambicioso en serio**
Curso completo sobre los tres niveles (código, diseño, arquitectura) + herramienta funcional + eventual libro = años de trabajo si se hace bien. El riesgo no es el concepto, es la ejecución. Hay que definir un MVP pedagógico claro o el proyecto se diluye.

**2. La velocidad de la IA puede desactualizar el "Nuevo Paradigma"**
El argumento sobre el rol del desarrollador en la era IA es vanguardia hoy. En 18-24 meses puede ser lugar común o, peor, puede haber cambiado tanto que el análisis quede desactualizado. Hay que estructurarlo de manera que los principios fundamentales sobrevivan aunque cambien los ejemplos.

**3. Competencia con nombres instalados**
Martin, Fowler, Feathers ya son marcas. Entrar al mismo espacio requiere diferenciación muy clara. La ventaja es el idioma y el ángulo de IA; el riesgo es que la comparación con "Clean Code" posicione el material como derivativo en vez de original.

**4. El mantenimiento del framework es carga real**
Un curso que depende de una herramienta activa requiere mantener ambos sincronizados. Si `designreviewer` cambia su output en v0.5.0, el material del curso necesita actualizarse. Esa dependencia tiene costo.

**5. Aceptación del componente filosófico**
El estoicismo, Taleb y los sistemas complejos son materiales valiosos, pero hay una fractura en la audiencia técnica: una parte lo valora como profundidad, otra lo lee como divagación. Hay que pensar cómo estructurarlo para que el que quiere ir directo a las métricas pueda hacerlo, sin sacrificar la profundidad para el que quiere más.

---

## Diagnóstico

La iniciativa tiene bases sólidas y una contribución original real. El mayor trabajo no está
en el concepto ni en la herramienta, está en **la transformación del material existente en
contenido pedagógico**. Lo que hay es una excelente documentación técnica; lo que falta es
la capa didáctica encima.

**Recomendación:** empezar por un curso acotado (por ejemplo, solo DesignReviewer + los
principios de diseño del nivel medio) antes de intentar cubrir los tres niveles completos.
Validar con audiencia real, y construir el libro a partir del material del curso, no al revés.
