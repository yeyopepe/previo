---
name: pv-internal-tech-mermaid
description: Procedimiento compartido, agnóstico al proyecto, para generar diagramas Mermaid (funcionales o técnicos — flujo, secuencia) que representan un caso de uso, historia de usuario, flujo de trabajo o comunicación entre componentes. Recibe la lista de diagramas a generar (tipo, qué debe representar cada uno) y devuelve el código Mermaid de cada uno, sin decidir por sí misma qué diagramas hacen falta ni dónde se insertan. Uso interno de las skills pv-internal-workflow, pv-new, pv-fix y pv-how, invocada por el nombre configurado en `framework.skills.diagrams` de `.claude/pv-context.json` (por defecto, esta misma skill).
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.2
  uses: []
---

# pv-internal-tech-mermaid

Procedimiento único y compartido para generar diagramas Mermaid que representan el comportamiento de un cambio/fix — nunca su aspecto visual (eso es `design_*.html`, otra skill) ni la navegación entre pantallas de UI (eso son los `design_navigation_*.md`, que escribe directamente `pv-new`). Solo lo invocan otras skills del framework `pv-*` — no está pensado para invocación directa por el usuario.

**Esta skill no decide qué diagramas hacen falta, ni si un diagrama es la herramienta adecuada frente a prosa, ni dónde se inserta el resultado.** Eso lo decide siempre quien invoca: esta skill solo se invoca cuando ya se sabe que hace falta generar al menos un diagrama Mermaid, nunca "por si acaso". Presentar el resultado al usuario para que lo confirme también es responsabilidad de quien invoca.

Si un proyecto configura otra skill en `framework.skills.diagrams` para generar los diagramas de otra forma (otra notación, una herramienta externa), esa skill alternativa debe cumplir el mismo contrato de entrada/salida descrito aquí para poder sustituir a esta sin que `pv-internal-workflow`/`pv-new`/`pv-fix`/`pv-how` necesiten cambiar nada.

## Entrada esperada de quien invoca

Una lista de diagramas a generar. Por cada uno:

- **Tipo**: uno de los tres definidos en "Reglas generales" más abajo — `funcional`, `flujo-técnico` o `secuencia-técnica`.
- **Qué debe representar**: el caso de uso/historia de usuario concreto (si es `funcional`) o el flujo/comunicación concreta (si es técnico) — pasos, decisiones, casos límite, o los actores/componentes involucrados y qué se intercambian, según corresponda.
- **Contexto de apoyo** que quien invoca ya tenga (p.ej. nombres reales de componentes/módulos si es `secuencia-técnica`, o el vocabulario del dominio del proyecto) para que el diagrama use terminología precisa en vez de genérica.

## Reglas generales (agnósticas de Mermaid)

Estas reglas gobiernan **qué** representar y **cómo dividir** los diagramas, independientemente de la sintaxis usada para dibujarlos.

### Diagramas funcionales

- Representan la experiencia directa del usuario: qué hace, qué decide, qué ve como resultado — nunca cómo lo resuelve el sistema por dentro (sin nombres de componentes, funciones, estructuras de datos, llamadas de red, etc.).
- **Un diagrama por cada caso de uso o historia de usuario, nunca menos.** No mezcles dos casos o historias distintos en el mismo diagrama, aunque compartan pasos — si comparten pasos, cada diagrama los repite desde su propio punto de entrada. Si quien invoca pide representar varios casos/historias, genera un diagrama independiente por cada uno.
- Si un caso de uso no tiene ramas ni decisiones (es una secuencia lineal de una sola vía, sin alternativas), sigue mereciendo diagrama igualmente: no lo descartes por "demasiado simple" — esa decisión (si el diagrama aporta o no frente a una frase) es de quien invoca, no de esta skill.

### Diagramas técnicos

- **Diagrama de flujo** (workflow): para representar un proceso interno con pasos y decisiones — el orden en que ocurre algo, condiciones que ramifican el camino, casos límite encadenados. Un único actor/hilo de ejecución avanzando por pasos.
- **Diagrama de secuencia**: para representar comunicación entre componentes — qué mensajes/llamadas se intercambian, en qué orden, entre qué actores o partes (usuario↔sistema, cliente↔servidor, módulo↔módulo). Úsalo en cuanto haya dos o más partes intercambiando información, no solo un flujo interno de un único componente.
- Si lo que hay que representar tiene ambas dimensiones (un flujo con pasos/decisiones que además implica comunicación entre componentes en algún punto), genera los dos diagramas por separado en vez de forzar uno solo a cubrir ambas cosas — cada uno se lee mejor centrado en su propia dimensión.
- A diferencia de los funcionales, sí puede tener sentido un único diagrama técnico que cubra varios pasos relacionados de un mismo cambio, si quien invoca lo pide así explícitamente como una sola unidad — esta skill no lo impone, pero tampoco lo divide por su cuenta si se lo piden junto.

## Reglas específicas de Mermaid

Estas son las reglas de sintaxis/notación Mermaid en sí, separadas de las reglas generales de arriba para que un proyecto pueda sustituir esta skill por otra notación sin perder las reglas generales (que viven en `pv-internal-workflow`/`pv-new`/`pv-fix`/`pv-how`, no aquí).

### Elegir el tipo de diagrama Mermaid

- **Funcional** → `flowchart` (`TD` de arriba a abajo salvo que `LR` quede más legible por el número de pasos). Los diagramas funcionales representan la experiencia de un usuario avanzando por pasos y decisiones, que es exactamente lo que expresa un flowchart. No uses `sequenceDiagram` para un diagrama funcional: implica actores/componentes técnicos intercambiando mensajes, que es justo lo que un diagrama funcional no debe mostrar.
- **Flujo técnico** → `flowchart` (`TD` o `LR` según legibilidad).
- **Secuencia técnica** → `sequenceDiagram`.
- Si lo que hay que representar es explícitamente una máquina de estados (un componente/entidad con estados con nombre propio y transiciones entre ellos, más que una secuencia de pasos), `stateDiagram-v2` es una alternativa válida a `flowchart` tanto para lo funcional como para lo técnico — solo úsala cuando el concepto de "estado con nombre" sea real en el dominio, no como sinónimo de flowchart.

### Sintaxis `flowchart`

```
flowchart TD
    A[Paso o acción] --> B{¿Decisión?}
    B -->|Sí| C[Resultado A]
    B -->|No| D[Resultado B]
    C --> E[Fin]
    D --> E
```

- Nodos: `[Texto]` rectángulo (paso/acción), `{Texto}` rombo (decisión), `(Texto)` óvalo (inicio/fin), `((Texto))` círculo (evento puntual) — usa el que mejor describa semánticamente el nodo, no solo el rectángulo por defecto.
- Flechas: `-->` para la transición normal; `-->|texto|` para etiquetar la condición o el resultado de una decisión. Toda salida de un nodo `{Decisión}` debe llevar etiqueta que dependa de cuál sea (`Sí`/`No`, o el caso concreto) — una decisión sin las etiquetas de sus ramas no se entiende.
- Agrupa pasos relacionados con `subgraph Nombre ... end` solo si el diagrama tiene fases claramente diferenciadas y el agrupado ayuda a leerlo — no lo uses por defecto en flujos cortos.
- Etiquetas de nodo en el vocabulario del dominio/usuario (funcional) o del sistema (técnico) que dé quien invoca — nunca genéricas tipo "Paso 1", "Paso 2".
- Si una etiqueta necesita comillas, paréntesis u otros caracteres que Mermaid pueda interpretar como sintaxis, envuélvela entre comillas dobles: `A["Texto con (paréntesis)"]`.

### Sintaxis `sequenceDiagram`

```
sequenceDiagram
    actor Usuario
    participant Frontend
    participant Backend

    Usuario->>Frontend: Acción concreta
    Frontend->>Backend: Petición concreta
    Backend-->>Frontend: Respuesta
    Frontend-->>Usuario: Resultado visible

    alt Condición
        Frontend->>Backend: Camino alternativo
    else Otra condición
        Frontend->>Usuario: Aviso
    end
```

- `actor Nombre` para personas/roles humanos, `participant Nombre` para componentes/sistemas — declara solo los que de verdad intervienen, en el orden en que conviene leerlos (normalmente de "más externo/usuario" a "más interno").
- Flechas: `->>` mensaje/llamada síncrona, `-->>` respuesta o retorno, `-)` mensaje asíncrono (fire-and-forget, sin esperar respuesta). Usa siempre la que describa correctamente si quien envía espera respuesta o no.
- `alt/else/end` para ramas condicionales dentro de la secuencia, `loop ... end` para repetición, `Note over A,B: texto` para una aclaración puntual que no es un mensaje en sí.
- Cada flecha lleva una etiqueta breve y concreta (qué se pide o qué se devuelve) — nunca una flecha sin texto.

### Sintaxis `stateDiagram-v2` (solo cuando aplique, ver arriba)

```
stateDiagram-v2
    [*] --> Estado1
    Estado1 --> Estado2 : evento/condición
    Estado2 --> [*]
```

- `[*]` representa el punto de entrada/salida (no un estado real). Cada transición lleva `: texto` con el evento o condición que la dispara.

### Reglas de higiene comunes a los tres tipos

- El diagrama va siempre en un bloque de código con lenguaje `mermaid` (` ```mermaid ` ... ` ``` `), nunca como texto suelto.
- No mezcles dos tipos de diagrama (p.ej. nodos de `flowchart` dentro de un `sequenceDiagram`) en el mismo bloque.
- Etiquetas cortas y concretas — si una idea necesita una frase larga para quedar clara, es una señal de que ese matiz pertenece a una nota en prosa junto al diagrama, no dentro de una etiqueta.
- No hace falta forzar el mismo diagrama a explicarlo absolutamente todo: lo que no quede claro con el propio diagrama, quien invoca puede añadirlo como nota breve en prosa junto a él — esta skill no escribe esas notas, solo el diagrama.

## Pasos

1. Para cada diagrama de la lista recibida, elige el tipo de diagrama Mermaid según "Elegir el tipo de diagrama Mermaid" y redáctalo siguiendo las reglas generales y de sintaxis de arriba.
2. Devuelve a quien invoca, en el mismo turno, un bloque ```mermaid``` por cada diagrama pedido (en el mismo orden en que se pidieron). No presentes nada al usuario ni pidas confirmación, ni escribas el resultado en ningún fichero — eso lo hace quien invoca.
