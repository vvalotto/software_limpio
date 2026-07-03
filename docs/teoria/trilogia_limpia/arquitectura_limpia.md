# Arquitectura Limpia

> *"La arquitectura es sobre intención, no sobre frameworks."*
> — **Robert C. Martin**, Clean Architecture (2017)

**Pregunta ética:** *¿Puede el sistema evolucionar?*

**Nivel Macro:** Componentes, capas, dependencias

---

## Definición

La arquitectura limpia organiza el sistema en componentes independientes con dependencias explícitas y unidireccionales. Permite que el sistema crezca, cambie y dure décadas.

**No es:** elegir frameworks de moda o dibujar diagramas bonitos.

**Es:** tomar decisiones de diseño que permitan cambiar lo periférico sin tocar lo esencial.

A nivel de arquitectura, los principios de [Fundamentos](../fundamentos/README.md) siguen aplicando: la separación en capas es **modularidad** a escala de sistema, los boundaries son **ocultamiento de información** y **abstracción** entre componentes, y la Regla de Dependencia no es otra cosa que mantener el **acoplamiento** bajo y unidireccional.

*Los ejemplos de esta sección están basados en [ISSE_Termostato](https://github.com/vvalotto/ISSE_Termostato), un sistema real de control de termostato con Clean Architecture, simplificados para fines didácticos.*

---

## Por Qué Importa

La arquitectura determina si un sistema muere en 2 años o vive 20. No se ve en el primer sprint. Se sufre (o se agradece) en el año 5.

**Mala arquitectura:** cada cambio requiere reescribir medio sistema.

**Buena arquitectura:** cada cambio se localiza en un componente específico.

### En la Era de la IA

La IA puede generar componentes completos en minutos. Pero no sabe:
- Dónde poner los boundaries entre componentes
- Qué depende de qué
- Cuál es la dirección correcta de las dependencias

**Tu responsabilidad: diseñar la estructura que hace sostenible lo generado.**

---

## Los Tres Principios de Arquitectura Limpia

### 1. Separación en Capas

El sistema se divide en capas concéntricas. Las dependencias apuntan **hacia adentro**.

```
┌───────────────────────────────────────────────┐
│          Frameworks y Drivers                 │  ← Externo
│    (sockets, sensores, displays)              │
├───────────────────────────────────────────────┤
│       Interface Adapters                      │
│    (Proxies, Visualizadores, Factories)       │
├───────────────────────────────────────────────┤
│         Casos de Uso                          │
│    (Gestores de entidades)                    │
├───────────────────────────────────────────────┤
│          Entidades                            │  ← Interno
│    (Ambiente, Batería, Climatizador)          │
└───────────────────────────────────────────────┘

        Dependencias apuntan →  hacia adentro
```

**Regla de Dependencia:**
> El código en un círculo interno **nunca** debe conocer nada del círculo externo.

**Ejemplo:**
```python
# Bien: entidad no conoce sockets, hardware ni frameworks
class Ambiente:
    def __init__(self, temperatura_deseada_inicial=None):
        self.__temperatura_ambiente = None
        self.__temperatura_deseada = temperatura_deseada_inicial or 22

    @property
    def temperatura_ambiente(self):
        return self.__temperatura_ambiente

# Mal: entidad acoplada al detalle de infraestructura
class Ambiente:
    def __init__(self, socket_conexion):  # ¡Violación! Entidad depende de socket
        self.socket = socket_conexion
```

---

### 2. La Regla de Dependencia

**Principio:** Las dependencias de código fuente apuntan hacia las políticas de alto nivel.

```
    Detalles  →  Políticas
    (cambios frecuentes)  →  (cambios raros)

    Socket/Archivo  →  Gestor  →  Ambiente
    Sensor físico   →  Caso de Uso  →  Reglas de Negocio
```

**Inversión de Dependencias (DIP):**

```python
# Mal: el gestor depende del detalle concreto
class GestorAmbiente:
    def leer_temperatura_ambiente(self):
        proxy = ProxySensorTemperaturaSocket("0.0.0.0", 12000)  # ¡Dependencia incorrecta!
        self._ambiente.temperatura_ambiente = proxy.leer_temperatura()

# Bien: el gestor recibe la abstracción inyectada (así es en ISSE_Termostato)
class GestorAmbiente:
    def __init__(self, ambiente, proxy_sensor, visualizador, incremento_temperatura=1):
        self._ambiente = ambiente
        self._proxy_sensor_temperatura = proxy_sensor  # Abstracción (política)
        self._visualizador_temperatura = visualizador

    def leer_temperatura_ambiente(self):
        try:
            temperatura = self._proxy_sensor_temperatura.leer_temperatura()
            self._ambiente.temperatura_ambiente = temperatura
        except (OSError, ValueError, TimeoutError):
            self._ambiente.temperatura_ambiente = None
```

El `GestorAmbiente` no sabe si el sensor lee de un archivo o de un socket TCP. Solo conoce la abstracción.

---

### 3. Boundaries (Fronteras)

Los boundaries separan componentes. Aislan cambios. Permiten testar independientemente.

**Tipos de boundaries:**

| Tipo | Ejemplo | Cuándo usar |
|------|---------|-------------|
| **API** | Interface / ABC | Entre capas del mismo proceso |
| **Adaptador** | Proxy / Gateway | Entre dominio y sensores/hardware |
| **Servicio** | Microservicio, API REST | Entre bounded contexts |

**Ejemplo de boundary (real, de ISSE_Termostato):**

```python
# Boundary: interfaz abstracta
class AbsSelectorTemperatura(ABC):
    @abstractmethod
    def obtener_selector(self):
        pass

# El gestor usa la abstracción, no le importa el origen
class SelectorTemperaturaArchivo(AbsSelectorTemperatura):
    def obtener_selector(self):
        with open("tipo_temperatura", "r", encoding="utf-8") as archivo:
            return archivo.read().strip()

class SelectorTemperaturaSocket(AbsSelectorTemperatura):
    def __init__(self, host, puerto):
        # ... setup de socket TCP persistente
        pass

    def obtener_selector(self):
        # Lee el modo (ambiente/deseada) desde el socket
        pass
```

**Beneficio:** cambiar de "archivo" a "socket" es una línea en `termostato.json`. No toca al `GestorAmbiente`.

---

## Las Cuatro Capas Clásicas

### 1. Entidades (Enterprise Business Rules)

**Qué son:** Reglas de negocio que son verdad independientemente de la aplicación.

**Ejemplo (simplificado de `entidades/ambiente.py`):**
```python
class Ambiente:
    """Entidad que representa el ambiente a climatizar."""

    def __init__(self, temperatura_deseada_inicial=None):
        self.__temperatura_ambiente = None  # Aún no leída del sensor
        self.__temperatura_deseada = temperatura_deseada_inicial or 22
        self.__temperatura_a_mostrar = "ambiente"

    @property
    def temperatura_ambiente(self):
        return self.__temperatura_ambiente

    @temperatura_ambiente.setter
    def temperatura_ambiente(self, valor):
        self.__temperatura_ambiente = valor
```

**No depende de:** sockets, archivos, hardware, frameworks. Es pura lógica de dominio.

---

### 2. Casos de Uso (Application Business Rules)

**Qué son:** Orquestación específica de la aplicación. "Cómo se coordina X en este sistema".

**Ejemplo (simplificado de `gestores_entidades/gestor_ambiente.py`):**
```python
class GestorAmbiente:
    """Orquesta lectura de sensor, entidad Ambiente y visualización."""

    def __init__(self, ambiente, proxy_sensor, visualizador, incremento_temperatura=1):
        self._ambiente = ambiente
        self._proxy_sensor_temperatura = proxy_sensor
        self._visualizador_temperatura = visualizador
        self._incremento_temperatura = incremento_temperatura

    def leer_temperatura_ambiente(self):
        try:
            temperatura = self._proxy_sensor_temperatura.leer_temperatura()
            self._ambiente.temperatura_ambiente = temperatura
        except (OSError, ValueError, TimeoutError):
            self._ambiente.temperatura_ambiente = None

    def aumentar_temperatura_deseada(self):
        self._ambiente.temperatura_deseada += self._incremento_temperatura
```

**Depende de:** Entidades (inner) y abstracciones de proxy/visualizador.
**No depende de:** sockets concretos, archivos concretos (outer).

---

### 3. Interface Adapters

**Qué son:** Traductores entre la aplicación y el mundo externo.

**Tipos en ISSE_Termostato:**
- **Proxies:** traducen sensor físico/simulado → valor de dominio (`ProxySensorTemperatura`)
- **Visualizadores:** traducen estado de dominio → consola/socket/API (`VisualizadorTemperatura`)
- **Factories:** construyen la implementación correcta según configuración (`FactorySelectorTemperatura`)

**Ejemplo — Factory (Registry Pattern, real):**
```python
class FactorySelectorTemperatura(RegistryFactory):
    """Factory para crear instancias de selector de temperatura."""
    _registry = {}

FactorySelectorTemperatura.registrar("archivo", lambda **kw: SelectorTemperaturaArchivo())
FactorySelectorTemperatura.registrar(
    "socket",
    lambda host=None, puerto=None, **kw: SelectorTemperaturaSocket(host, puerto)
)
```

Agregar una nueva variante (ej. un selector via API) no modifica el Factory: solo se registra. Esto es Open/Closed aplicado a la construcción de objetos.

---

### 4. Frameworks y Drivers

**Qué son:** Detalles concretos. Sockets TCP, archivos, hardware, librerías externas.

**Ejemplo:**
```python
# actores_externos/ — simuladores que envían datos por socket
# Frameworks y Drivers: la capa más externa

simulador = SimuladorTemperatura(host="192.168.0.14", puerto=12000)
simulador.enviar_temperatura(21.5)
```

**Objetivo:** que cambiar de "socket" a "archivo" en `termostato.json`, o de Raspberry Pi a otro dispositivo, sea trivial y no requiera tocar `GestorAmbiente` ni `Ambiente`.

---

## Métricas de Arquitectura Limpia

| Métrica | Qué mide | Umbral | Herramienta |
|---------|----------|--------|-------------|
| **Distancia desde la Secuencia Principal** | D = \|A + I - 1\| | ≤ 0.3 | Structure101 |
| **Violaciones de capa** | Imports que apuntan hacia afuera | 0 | `pydeps`, análisis custom |
| **Ciclos de dependencia** | Componentes que se importan mutuamente | 0 | `pydeps --show-cycles` |
| **Acoplamiento Aferente (Ca)** | Cuántos componentes dependen de este | Medido | `pydeps` |
| **Acoplamiento Eferente (Ce)** | De cuántos componentes depende este | ≤ 5 ideal | `pydeps` |

**Así se ve en la práctica:** el análisis de dependencias de ISSE_Termostato mide CBO promedio de 1.38 (bajo, saludable) pero también detecta **2 violaciones de la regla de dependencia** (`servicios_aplicacion` importando `configurador`, una capa externa) y **3 ciclos de dependencias**. Ni siquiera un proyecto bien diseñado está libre de esto — la diferencia es que las métricas lo hacen visible y accionable.

**Ejecutar:**
```bash
# Detectar ciclos
pydeps src/ --show-cycles

# Visualizar dependencias
pydeps src/ --max-bacon=3 -o deps.png

# Análisis custom de violaciones de capa
python scripts/check_layer_violations.py
```

---

## Principios de Componentes

### Cohesión de Componentes

**REP (Reuse/Release Equivalence):** Lo que se reusa junto, se libera junto.

**CCP (Common Closure Principle):** Clases que cambian juntas, van juntas.

**CRP (Common Reuse Principle):** No obligues a depender de lo que no usás.

**Ejemplo:**
```
# Mal: mezclar concerns en un componente
utils/
├── conversion_temperatura.py
├── envio_notificaciones.py
├── generador_reportes.py

# Bien: separar por razón de cambio
conversion/
└── temperatura.py

notificaciones/
└── enviador.py

reportes/
└── generador.py
```

---

### Acoplamiento de Componentes

**ADP (Acyclic Dependencies Principle):** No ciclos en el grafo de dependencias.

**Ejemplo real (detectado en el análisis de dependencias de ISSE_Termostato):**
```
Ciclo detectado:
servicios_aplicacion → configurador → agentes_sensores → servicios_aplicacion
```

`servicios_aplicacion` importa `configurador` para construir sus dependencias, `configurador` importa `agentes_sensores` para instanciar proxies, y algún componente de `agentes_sensores` termina dependiendo de vuelta de `servicios_aplicacion`. Nadie lo diseñó así a propósito — emergió de agregar imports de a uno.

**Solución aplicada:** extraer una interfaz (`IConfiguradorDependencias`) e inyectar las dependencias ya construidas en lugar de que cada capa importe al configurador directamente.

**SDP (Stable Dependencies Principle):** Depender de lo estable.

**SAP (Stable Abstractions Principle):** Lo estable debe ser abstracto.

---

## Patrones de Arquitectura

### Hexagonal (Ports & Adapters)

```
         ┌─────────────────────┐
         │   Driving Adapters  │ (Simuladores de sensores)
         └──────────┬──────────┘
                    ↓
         ┌─────────────────────┐
         │    Application      │ (Gestores)
         │       Core          │ (Ambiente, Batería, Climatizador)
         └──────────┬──────────┘
                    ↓
         ┌─────────────────────┐
         │   Driven Adapters   │ (Visualizadores, Actuador)
         └─────────────────────┘
```

**Puertos:** interfaces que el core define (`AbsProxySensorTemperatura`, `AbsVisualizadorTemperatura`).
**Adaptadores:** implementaciones concretas (socket, archivo, API REST).

---

### Clean Architecture (Uncle Bob)

La versión de Martin de la arquitectura hexagonal, con énfasis en capas concéntricas. Es la que sigue ISSE_Termostato: Entidades → Casos de Uso → Interface Adapters → Frameworks y Drivers.

**Ventaja:** independencia de frameworks, testabilidad, cambios localizados.

---

### Event-Driven Architecture

**Cuándo:** sistema con múltiples componentes que necesitan reaccionar a cambios sin acoplarse directamente.

```python
# Componente 1: Publica evento
class BateriaCritica(Event):
    nivel: float

if bateria.nivel_de_carga < 15:
    event_bus.publish(BateriaCritica(bateria.nivel_de_carga))

# Componente 2: Escucha evento
@event_bus.subscribe(BateriaCritica)
def alertar_nivel_critico(evento):
    visualizador.mostrar_alerta(f"Batería crítica: {evento.nivel}%")
```

**Beneficio:** componentes desacoplados en tiempo.

---

## Arquitectura Limpia con IA

### Prompt para arquitectura

```
"Diseñar un nuevo proxy de sensor para el sistema de termostato con:
- Arquitectura de capas: Entidad → Gestor (caso de uso) → Proxy (adapter)
- Boundary claro: interfaz AbsProxySensorHumedad
- Inversión de dependencias (DIP): el gestor recibe el proxy inyectado
- Componentes:
  * Ambiente (entidad, ya existe)
  * GestorAmbiente (caso de uso, ya existe)
  * AbsProxySensorHumedad (puerto nuevo)
  * ProxySensorHumedadSocket (adaptador nuevo)
- Sin ciclos de dependencia con configurador ni agentes_sensores
- Type hints en el puerto"
```

### Verificar arquitectura generada

1. **Dibujar diagrama de dependencias:** `pydeps src/`
2. **Detectar ciclos:** `pydeps --show-cycles`
3. **Verificar regla de dependencia:** capas internas no importan externas
4. **Medir distancia:** componentes estables son abstractos

**Checklist:**
- [ ] ¿Las entidades dependen de cero frameworks/hardware?
- [ ] ¿Los gestores dependen solo de entidades y puertos (proxies abstractos)?
- [ ] ¿Los adaptadores implementan puertos definidos en capas internas?
- [ ] ¿Puedo cambiar de sensor real a simulado sin tocar el gestor?

---

## Anti-patrones de Arquitectura

### 1. Big Ball of Mud

**Síntoma:** No hay estructura. Todo depende de todo.

**Solución:** Identificar bounded contexts y separar en módulos.

---

### 2. Arquitectura Centrada en el Hardware

**Síntoma:** La lógica de negocio conoce detalles del dispositivo físico (puerto GPIO, dirección de socket, formato del ADC).

```python
# Mal: el gestor conoce el hardware
class GestorAmbiente:
    def leer_temperatura_ambiente(self):
        valor_adc = leer_gpio(pin=4)  # ¡Todo está acoplado al hardware!
        self._ambiente.temperatura_ambiente = (valor_adc - 150) / 5.0
```

**Solución:** capa HAL (Hardware Abstraction Layer) + Proxy que convierte la señal cruda en un valor de dominio, como en ISSE_Termostato.

---

### 3. Framework Coupling

**Síntoma:** Lógica de negocio embebida en el adaptador de comunicación.

```python
# Mal
class ProxySensorTemperaturaSocket:
    def leer_temperatura(self):
        datos = self._conexion.recv(4096)
        # 50 líneas decidiendo si hay que prender el calefactor aquí
        pass
```

**Solución:** Proxy delgado que solo traduce, lógica de histeresis en `servicios_dominio/ControladorTemperatura`.

---

### 4. Ciclos de Dependencias

**Síntoma:** A → B → C → A

**Consecuencia:** imposible testear componentes por separado.

**Caso real:** el propio ISSE_Termostato tiene 3 variaciones del mismo ciclo (`servicios_aplicacion` ↔ `configurador` ↔ `agentes_sensores`), detectadas por análisis automático de dependencias.

**Solución:** Invertir una dependencia o extraer abstracción (ver "Principios de Componentes" arriba).

---

## La Prueba del Dispositivo

> *"Si cambiar de sensor real a simulado requiere reescribir la lógica de negocio, la arquitectura está mal."*

**Preguntas:**
- ¿Puedo cambiar `proxy_sensor_temperatura` de "socket" a "archivo" en `termostato.json` sin tocar `GestorAmbiente`? → Sí
- ¿Puedo cambiar el visualizador de "consola" a "API REST" sin tocar `Ambiente`? → Sí
- ¿Puedo testear `GestorAmbiente` sin un sensor físico ni una Raspberry Pi? → Sí

**Si alguna respuesta es "No", hay acoplamiento arquitectónico.**

---

## En los Tres Niveles

| Aspecto | Código | Diseño | Arquitectura |
|---------|--------|--------|--------------|
| **Unidad** | Función | Clase/Módulo | Componente/Servicio |
| **Cohesión** | Una cosa | Una responsabilidad | Un bounded context |
| **Acoplamiento** | Pocos params | Pocas deps | Pocas interfaces públicas |
| **Abstracción** | Nombre claro | Interface clara | Boundary bien definido |
| **Cambio** | Líneas | Archivos | Componentes |
| **Tiempo** | Minutos | Horas | Días/Semanas |

---

## Sostenibilidad a Largo Plazo

La arquitectura limpia no es sobre el primer sprint. Es sobre el año 5:

| Sin Arquitectura Limpia | Con Arquitectura Limpia |
|-------------------------|-------------------------|
| Velocity decrece con el tiempo | Velocity se mantiene estable |
| Cada cambio rompe algo inesperado | Cambios localizados |
| Imposible testear sin todo el stack | Tests rápidos, enfocados |
| Frameworks/hardware obsoletos = reescritura | Frameworks/hardware intercambiables |
| Desarrolladores huyen del proyecto | Desarrolladores entienden el sistema |

**La arquitectura es una inversión. Se paga hoy, se cobra en 3 años.**

---

## Evolución de la Arquitectura

La arquitectura no es estática. Evoluciona. Pero con reglas:

1. **Cambios periféricos:** fáciles (cambiar de sensor socket a archivo)
2. **Cambios de casos de uso:** moderados (agregar un nuevo gestor)
3. **Cambios de entidades:** difíciles (cambiar las reglas de histeresis del climatizador)

**El objetivo:** maximizar cambios tipo 1, minimizar tipo 3.

---

## Lecturas Recomendadas

1. **Martin, R.C. (2017)**. *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Capítulos completos.
2. **Fowler, M. (2002)**. *Patterns of Enterprise Application Architecture*. Capítulos 1-2, 9-11.
3. **Evans, E. (2003)**. *Domain-Driven Design*. Parte IV (Strategic Design).
4. **Vernon, V. (2013)**. *Implementing Domain-Driven Design*. Capítulo 4 (Architecture).
5. **Parnas, D.L. (1972)**. "On the Criteria To Be Used in Decomposing Systems into Modules". Paper fundacional.
6. **Valotto, V.** *[ISSE_Termostato](https://github.com/vvalotto/ISSE_Termostato)*. Proyecto de referencia con Clean Architecture aplicada a un sistema embebido real.

---

[← Volver a Trilogía Limpia](README.md)
