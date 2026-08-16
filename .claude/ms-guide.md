# Guía de uso — MinSDD

MinSDD (nombre provisional para el framework `ms-*`) es un conjunto de skills de Claude Code que estandariza cómo se documentan, planifican e implementan los cambios en este proyecto. Todo cambio real en el código pasa por el mismo ciclo: **documentar la intención → planificar la solución técnica → implementar**. Empaquetar una entrega (generar el entregable, copiar la documentación técnica vigente y redactar el changelog funcional) también forma parte del framework: lo hace `/ms-version` (ver [Preparar una entrega: `/ms-version`](#preparar-una-entrega-ms-version)).

Todas las skills viven bajo `.claude/skills/ms-*` y comparten un único fichero de configuración: `.claude/ms-context.json`.

## Índice

- [Puntos fuertes](#puntos-fuertes)
- [Preparación](#preparación)
  - [1. Herramientas necesarias](#1-herramientas-necesarias)
  - [2. Inicializar el framework: `/ms-init`](#2-inicializar-el-framework-ms-init)
    - [Elegir el modelo/esfuerzo de cada skill: `skillModels`](#elegir-el-modeloesfuerzo-de-cada-skill-skillmodels)
- [Guía de uso rápida: el flujo natural](#guía-de-uso-rápida-el-flujo-natural)
  - [Paso 0 (opcional) — Apuntar ideas sueltas: `/ms-todo`](#paso-0-opcional--apuntar-ideas-sueltas-ms-todo)
  - [Paso 1 — Definir el cambio: dos maneras](#paso-1--definir-el-cambio-dos-maneras)
    - [1. `/ms-new` — funcionalidad nueva o cambio de comportamiento intencionado](#1-ms-new--funcionalidad-nueva-o-cambio-de-comportamiento-intencionado)
    - [2. `/ms-fix` — corregir un bug (o aplicar un cambio trivial al vuelo)](#2-ms-fix--corregir-un-bug-o-aplicar-un-cambio-trivial-al-vuelo)
  - [Paso 2 — Planificar e implementar: `ms-how` + `ms-do`](#paso-2--planificar-e-implementar-ms-how--ms-do)
- [Preparar una entrega: `/ms-version`](#preparar-una-entrega-ms-version)
- [Ejemplo de ciclo completo](#ejemplo-de-ciclo-completo)
- [Trucos](#trucos)
- [Notas](#notas)

## Puntos fuertes

- **Pensado para proyectos pequeños y medianos.** Aporta el control y la trazabilidad del *spec-driven development* (SDD) sin la sobrecarga de proceso que ese enfoque suele exigir en proyectos grandes.
- **100% conversacional y dirigido por IA.** Todo el ciclo — desde que surge la idea hasta que queda implementada — está pensado para que lo lleve una IA conversando con personas, no para rellenar formularios ni seguir un asistente rígido paso a paso.
- **Especificación completa, formato libre.** Cada entrada exige la estructura mínima necesaria para ser útil (intención, plan, estado), pero sin formatos de *spec* complejos y rígidos que haya que aprender o mantener a mano.
- **Sin herramientas adicionales.** No requiere más que Claude y Python instalados en la máquina de desarrollo — nada de servicios externos, bases de datos ni infraestructura propia que mantener.
- **Valida el diseño antes de tocar código.** No se limita a analizar y planificar el cambio: cuando hay componente visual, genera maquetas estáticas en HTML/CSS (`design_*.html`) que puedes abrir y revisar en el navegador para validar el aspecto antes de que se implemente nada — evitando el ciclo de "implementar → ver que no convence → rehacer".

## Preparación

### 1. Herramientas necesarias

El propio `ms-init` comprueba esto por ti la primera vez, pero para referencia:

- **Git** — el repo ya lo es; solo hace falta que el CLI funcione (`git --version`).
- **Python 3** — usado por los scripts internos de `ms-internal-workflow`, `ms-how` y `ms-do` (numeración de cambios, mover carpetas). Comprueba `python --version`.
- **Herramientas condicionales según el proyecto**, por ejemplo:
  - Node/npm si hay `package.json`.
  - Cualquier otro intérprete que necesite el proyecto.

Generar una versión del entregable **sí** forma parte del framework `ms-*`: `/ms-version` la empaqueta (ver [Preparar una entrega: `/ms-version`](#preparar-una-entrega-ms-version)). En este repo (Errantes), el comando de compilación que usa por debajo es `python ./src/scripts/build.py`, que autoincrementa `CURRENT_VERSION` en `src/data/version.js` y escribe `src/_output/versions/index-v{NNNN}.html` — carpeta y numeración propias del build script, sin relación con la numeración de `/ms-version`.

### 2. Inicializar el framework: `/ms-init`

Antes de poder usar cualquier otra skill `ms-*`, hay que ejecutar `/ms-init` una vez por proyecto. Genera `.claude/ms-context.json`, que es el único sitio donde vive la configuración: dónde se guardan los cambios, si el proyecto versiona entregables, dónde está el código fuente, qué documentos mantener sincronizados, etc.

`ms-init` explora el repo en busca de pistas (carpeta de cambios existente, `package.json`, docs de arquitectura...) y solo pregunta lo que no puede deducir. Si se vuelve a invocar sobre un proyecto ya inicializado, permite reconfigurar o completar campos que falten sin repetir todo el cuestionario.

Ejemplo de `.claude/ms-context.json` ya configurado en este proyecto:

```json
{
  "skillModels": {
    "_instructions": "Tras editar 'default' o 'overrides' de esta seccion, ejecuta desde la raiz del repo: python .claude/skills/ms-init/scripts/sync-skill-models.py -- reescribe el campo 'model'/'effort' en el frontmatter de cada SKILL.md 'ms-*' segun lo que quede configurado aqui. El harness de Claude Code solo lee ese frontmatter, no este JSON, asi que sin ejecutar el script los cambios de aqui no tienen efecto.",
    "default": { "model": "claude-sonnet-5", "effort": "medium" },
    "overrides": {
      "ms-status": { "model": "claude-haiku-4-5-20251001", "effort": "medium" },
      "ms-todo": { "model": "claude-haiku-4-5-20251001", "effort": "medium" },
      "ms-do": { "model": "claude-haiku-4-5-20251001", "effort": "high" }
    }
  },
  "framework": {
    "sourcecodeDir": "src",
    "workFolder": "/",
    "numberWidth": 5,
    "docs": {
      "functional": {
        "featuresDocPathDir": "design/docs/features"
      },
      "tech": {
        "architectureDocDir": "design/docs/architecture",
        "styleBibleDocDir": "design/docs/style"
      }
    }
  },
  "project": {
    "name": "Errantes",
    "summary": "Prototipo digital jugable en navegador del juego de mesa Errantes",
    "stack": ["JavaScript vanilla (ES modules)", "HTML/CSS", "Python build script"],
    "notes": "El entregable es un único HTML autocontenido por versión, generado sin Node.js"
  }
}
```

Todos los campos de `framework` son opcionales, incluido `workFolder` (default `"/"`, la raíz del repo) — el framework funciona sin `docs.tech.architectureDocDir`, `docs.functional.featuresDocPathDir` o `docs.tech.styleBibleDocDir`, simplemente usa menos contexto al analizar y no mantiene esos documentos sincronizados. `workFolder` es la única ruta que se elige: dentro de él, `changes/` y `versions/` son subcarpetas de nombre fijo que las skills crean por sí mismas, para que no se puedan desconfigurar por error.

#### Elegir el modelo/esfuerzo de cada skill: `skillModels`

`.claude/ms-context.json` también puede incluir una sección opcional `skillModels` que decide con qué modelo (Sonnet, Haiku...) y esfuerzo corre cada skill `ms-*` del proyecto — por ejemplo, para bajar a Haiku las skills más mecánicas (`ms-status`, `ms-todo`) o subir el esfuerzo de las que implementan código (`ms-do`) sin tocar las que razonan sobre arquitectura.

- `default`: modelo/esfuerzo que aplica a cualquier skill `ms-*` sin entrada propia en `overrides`.
- `overrides`: una entrada por nombre de skill (el `name:` de su `SKILL.md`) para las que necesiten algo distinto del `default`.

Importante: el harness de Claude Code solo lee el campo `model`/`effort` del frontmatter de cada `SKILL.md`, no este JSON — `skillModels` es solo la fuente de verdad declarativa. Tras editar `default` u `overrides`, hay que ejecutar desde la raíz del repo:

```
python .claude/skills/ms-init/scripts/sync-skill-models.py
```

Este script reescribe el frontmatter `model`/`effort` de cada `SKILL.md` `ms-*` según lo configurado, sin lo cual los cambios en `ms-context.json` no tienen ningún efecto. Es un script determinista (sin LLM); puede ejecutarse manualmente en cualquier momento tras editar `skillModels` a mano, o pedirle a `ms-init` que lo haga por ti la próxima vez que lo invoques.

## Guía de uso rápida: el flujo natural

```mermaid
flowchart LR
    T["/ms-todo\n(idea suelta)"]
    A["/ms-new o /ms-fix\n(documentar intención)"]
    B["ms-how\n(planificar: plan.md)"]
    C["ms-do\n(implementar código)"]
    F["queda en inProgress\npendiente de retomar"]
    G["/ms-fix\n(atajo interno: cambio trivial)"]
    H["fin de ciclo"]

    T -->|"/ms-new todo {código}"| A
    A -->|"inProgress"| B
    B -->|usuario confirma| C
    C -->|"implemented"| H
    B -->|usuario no confirma| F
    F -->|usuario confirma más tarde| C
    G -->|"inProgress → implemented\n(mismo turno, sin plan.md)"| H
    G -->|si no es trivial ni bug| A

    N1["comentario:\nno interfiere con\ninProgress/implemented\nni con la numeración xxxx"]
    N1 --- T
    N4["comentario:\nun bug se corrige de punta a punta\nen la misma invocación\n(alcance acotado a la causa raíz)"]
    N4 --- A

    class T,F,H opcional
    class A,B,C,G obligatorio
    class N1,N4 comentario
    classDef obligatorio fill:#4c6ef5,stroke:#364fc7,stroke-width:2px,color:#fff
    classDef opcional fill:#fff,stroke:#adb5bd,stroke-width:1px,color:#212529
    classDef comentario fill:#fff9c4,stroke:#e6d84a,stroke-width:1px,color:#333
    linkStyle 1 color:#8b0000,stroke:#8b0000,stroke-width:2px
    linkStyle 3 color:#8b0000,stroke:#8b0000,stroke-width:2px
    linkStyle 6 color:#8b0000,stroke:#8b0000,stroke-width:2px
```

Nodos azules = paso obligatorio del ciclo (Paso 1 y Paso 2) o vía directa equivalente (el atajo `fast` interno de `/ms-fix`, que aplica el código sin pasar por `plan.md` si el cambio — bug o no — califica como trivial). Nodos blancos = punto de entrada u operación opcional (`/ms-todo`, o quedarse pendiente en `inProgress`). Las flechas rojo oscuro con fondo blanco y texto rojo oscuro indican un cambio de estado (solo el nombre de la carpeta destino: `inProgress`, `implemented`); el resto de flechas indican solo una transición sin cambio de carpeta. Los cuadros amarillos son comentarios aclaratorios conectados sin flecha al nodo al que se refieren.

Cada entrada de trabajo vive en una carpeta numerada `xxxx` (p.ej. `00007`) que va viajando entre subcarpetas de `changesDir` según su estado: `inProgress/` → `implemented/`.

### Paso 0 (opcional) — Apuntar ideas sueltas: `/ms-todo`

Antes de que una idea sea un change o un fix, puede que solo quieras dejarla anotada para más adelante sin comprometerte a documentarla ni implementarla todavía. `/ms-todo <idea>` la guarda en `changes/todo/{código}/description.md` — una carpeta aparte que ninguna otra skill del framework usa ni tiene en cuenta, así que no interfiere con `inProgress`/`implemented` ni con la numeración `xxxx`.

- **Apuntar o ampliar**: `/ms-todo <idea>` crea una nueva; `/ms-todo {código} <más detalle>` sigue desarrollando una ya existente.
- **Consultar lo apuntado**: `/ms-status todo` lista las ideas pendientes con su código y texto completo.
- **Convertir en cambio**: cuando una idea de la lista madura y quieres llevarla al flujo real, `/ms-new todo {código}` arranca `ms-new` partiendo de esa idea en vez de una petición nueva, y borra la entrada de `todo/` automáticamente al terminar (sin pedir confirmación) — la idea pasa a vivir como entrada normal en `changes/inProgress/`.

### Paso 1 — Definir el cambio: dos maneras

El framework ofrece dos puntos de entrada según la naturaleza del cambio — la elección depende de si es un bug o funcionalidad/cambio intencionado. Dentro de `/ms-fix`, además, hay un atajo automático para lo trivial (ver más abajo).

#### 1. `/ms-new` — funcionalidad nueva o cambio de comportamiento intencionado

Para funcionalidad nueva o un cambio de comportamiento **intencionado** que no sea trivial. Ejemplo: `/ms-new añade un botón para barajar el mazo de eventos manualmente`.

#### 2. `/ms-fix` — corregir un bug (o aplicar un cambio trivial al vuelo)

Para un bug, algo que ya debería funcionar de otra forma. Ejemplo: `/ms-fix al recargar la página se pierde la partida en curso aunque estaba guardada`. También es el punto de entrada para algo tan pequeño que no merece pasar por `description.md` + `plan.md` + confirmación (un typo, un texto, un valor/constante puntual, un ajuste de estilo aislado, sea o no un bug): `/ms-fix corrige el texto del botón "Guradar" a "Guardar"`.

`ms-fix` primero valora si lo pedido es trivial (sin ambigüedad, como mucho 2 ficheros, sin comportamiento nuevo, sin tocar `docs.tech.architectureDocDir` ni `docs.tech.styleBibleDocDir`):

- **Si es trivial** (atajo `fast`, bug o no): aplica el cambio directamente en el código y, en la misma invocación, documenta lo hecho en `changes/implemented/{xxxx}/description.md` — pasa brevemente por `inProgress` (numeración `xxxx` normal vía `ms-internal-workflow`) y se mueve a `implemented` en el mismo turno, sin generar `plan.md` ni encadenar `ms-how`/`ms-do`.
- **Si no es trivial y es un bug**: sigue el flujo normal descrito abajo (documenta + encadena `ms-how`/`ms-do`).
- **Si no es trivial y no es un bug** (afecta a arquitectura/estilo, falta información, toca más de 2 ficheros, o es funcionalidad nueva): no toca nada de código, te avisa de por qué no encaja, e invoca directamente `ms-new` con tu petición para arrancar el flujo normal de documentación.

Para el caso no trivial (`/ms-new` y el `/ms-fix` que resulta ser un bug real), la skill:

1. Analiza el alcance y **anticipa** las dudas típicas (casos límite, convivencia con lo existente, alcance de los datos, quién puede usarlo, aspecto visual de alto nivel) y te propone respuestas razonables para que las confirmes o corrijas, en vez de preguntar a ciegas.
2. Genera `changes/inProgress/{xxxx}/description.md` con el resumen funcional (nunca solución técnica todavía).
3. Si el cambio tiene componente visual, crea maquetas estáticas `design_*.html` (solo HTML/CSS/SVG, sin lógica) como referencia visual navegable — para validar el diseño antes de escribir una sola línea de código real.

Diferencia clave: `/ms-fix` (caso no trivial) encadena automáticamente `ms-how` (que a su vez encadena `ms-do`) al terminar (un bug se corrige de punta a punta en la misma invocación, con alcance estrictamente acotado a la causa raíz). `/ms-new` solo documenta — decides tú cuándo planificar/implementar después.

Si ya existe una entrada en `inProgress` y quieres ampliarla en vez de crear una nueva, invoca `/ms-new {xxxx} <descripción de la ampliación>` — detecta que ya existe y añade a lo documentado en vez de crear otra carpeta.

### Paso 2 — Planificar e implementar: `ms-how` + `ms-do`

`/ms-how {xxxx}` toma una entrada ya documentada en `inProgress` y:

1. Analiza la causa raíz (fix) o diseña la solución técnica (change), usando como fuente de verdad el código real, la documentación de arquitectura (`docs.tech.architectureDocDir`) y la guía de estilo (`docs.tech.styleBibleDocDir`) — nunca lo que otras entradas de `changes/` asuman ni la memoria de la conversación.
2. Escribe `changes/inProgress/{xxxx}/plan.md` con tres secciones: (a) anotaciones funcionales, (b) solución técnica paso a paso, (c) cambios de arquitectura si aplica.
3. Pregunta si quieres implementarlo ya. Si confirmas, encadena directamente `ms-do`, que edita el código, actualiza `docs.tech.architectureDocDir`/`docs.functional.featuresDocPathDir`/`docs.tech.styleBibleDocDir` según corresponda, y mueve la carpeta a `changes/implemented/{xxxx}/`.

Si invocas `/ms-how` sin argumento, lista lo que hay pendiente en `inProgress` y te pregunta cuál quieres. Si `plan.md` ya existía (por ejemplo, quieres retomarlo), te pregunta si quieres regenerarlo desde cero o implementar directamente lo que ya dice (en ese caso encadena `ms-do` sin volver a analizar). También puedes invocar `/ms-do {xxxx}` directamente sobre una entrada que ya tenga `plan.md`, sin pasar por `ms-how` de nuevo.

## Preparar una entrega: `/ms-version`

Cuando ya hay trabajo listo (`changes/implemented/`) y quieres cortar una entrega, `/ms-version <XXXX>` empaqueta todo en `{workFolder}/versions/{XXXX}/`: genera el entregable, comprime y copia la documentación técnica y funcional vigente, y redacta el changelog funcional a partir de lo que se haya ido cerrando en `changes/closed/`. `{XXXX}` es texto libre que eliges tú en cada invocación (p.ej. `00001`, `v1`, `beta3`) — no tiene relación con la numeración `xxxx` de change/fix, ni con `src/_output/versions/` (la carpeta que ya genera `build.py` por su cuenta con su propio contador `NNNN`): son tres espacios completamente independientes.

Si invocas `/ms-version` solo para informar de un cambio en el procedimiento de build (p.ej. "ahora el build también genera un PDF de reglas"), sin pedir preparar una entrega, actualiza `{workFolder}/framework/how-to-compile-version.md` con eso y te pregunta si quieres lanzar el proceso de versionado ahora — no lo lanza por su cuenta.

```mermaid
flowchart LR
    Guard{"implemented/\n¿vacío?"}
    Resolve["Resolver cada entrada\n(usuario confirma → closed)"]
    Folder["Crear versions/XXXX\n(files/, docs/)"]
    Compile["Generar el entregable\n(how-to-compile-version.md)"]
    Docs["Comprimir y copiar documentación\ntécnica y funcional a docs/"]
    Changelog["ms-internal-changelog\nredacta changelog.md desde closed/"]
    Confirm["Confirmar entrega\nal usuario"]

    Guard -- No --> Resolve --> Guard
    Guard -- Sí --> Folder --> Compile --> Docs --> Changelog --> Confirm

    classDef guardrail fill:#e03131,color:#fff
    classDef core fill:#2b6cb0,color:#fff
    classDef internal fill:#805ad5,color:#fff
    classDef done fill:#2f9e44,color:#fff
    class Guard,Resolve guardrail
    class Folder,Compile,Docs core
    class Changelog internal
    class Confirm done
```

Leyenda: rojo = guardarraíl de `implemented/` (bloquea hasta resolverse); azul = pasos mecánicos de `ms-version`; morado = delegado en `ms-internal-changelog`; verde = fin del proceso.

En prosa:

1. **Guardarraíl de arranque**: si `changes/implemented/` tiene alguna entrada, `/ms-version` no avanza hasta resolverlas todas — por cada una pregunta si pasa a `closed` (irreversible sin confirmación) antes de seguir.
2. **Crear la carpeta de la versión**: `{workFolder}/versions/{XXXX}/{files,docs}/`. Si `{XXXX}` ya existe, pregunta si regenerar sobre lo existente o elegir otro código.
3. **Generar el entregable**: sigue el procedimiento de `{workFolder}/framework/how-to-compile-version.md` (se pregunta y se escribe la primera vez que hace falta, con un paso por artefacto si el build genera varios; en este repo ejecuta `python ./src/scripts/build.py`) y copia el resultado a `files/` mediante script.
4. **Comprimir y copiar documentación**: las rutas configuradas en `docs.tech.architectureDocDir`/`docs.tech.styleBibleDocDir`/`docs.functional.featuresDocPathDir` (las que estén configuradas) se comprimen en un `.zip` cada una y se guardan en `docs/`, como constancia de qué documentación estaba vigente en el momento de esta entrega.
5. **Changelog funcional**: `ms-internal-changelog` (skill interna) lee cada `description.md` de `changes/closed/`. Las entradas de tipo `fix` van directas a **Fixes**; el resto se compara contra el changelog de la versión anterior detectada en `{workFolder}/versions/` (confirmándotela antes de usarla) y se clasifica en **Nuevo** / **Cambios** / **Eliminado**. `changelog.md` lleva una cabecera con el número de entradas de cada sección, en lenguaje puramente funcional. Tras tu confirmación explícita, borra de `closed/` solo las carpetas ya incorporadas (nunca "todo `closed/`" a ciegas); si no confirmas el borrado, el changelog queda escrito igualmente y `closed/` no se toca.

Todo el copiado/borrado de ficheros de este proceso (artefacto del build, documentación, entradas de `closed/`) lo hacen scripts propios de las skills, nunca ediciones manuales.

Puedes preguntar "¿cómo funciona `/ms-version`?" en mitad de la invocación y te muestra este mismo diagrama.

## Ejemplo de ciclo completo

```
/ms-fix el temporizador de turno no se detiene al pausar la partida
```

1. `ms-fix` documenta el bug en `changes/inProgress/00008/description.md` y encadena `ms-how` automáticamente.
2. `ms-how` analiza la causa raíz, escribe `plan.md` (acotado solo a ese bug) y pregunta si implementar.
3. Confirmas → `ms-how` encadena `ms-do`, que edita el código, actualiza `FEATURES.md`/`design/docs/architecture/` si aplica, y mueve la carpeta a `changes/implemented/00008/`.
4. Cuando quieras cortar una nueva entrega: `/ms-version 00001` → mueve `00008` (y cualquier otra entrada de `implemented/`) a `closed`, genera el entregable (`python ./src/scripts/build.py` por debajo, que incrementa la versión en `version.js`), comprime y copia la documentación técnica y funcional vigente, y redacta `changelog.md` con lo acumulado en `closed/` (este `00008`, de tipo `fix`, cae en la sección Fixes).

Y para algo trivial:

```
/ms-fix corrige el texto del botón "Guradar" a "Guardar"
```

1. `ms-fix` valora que es trivial (un texto, un fichero) y aplica el cambio directamente.
2. Documenta lo hecho en `changes/inProgress/00009/description.md` (numeración normal vía `ms-internal-workflow`) y en el mismo turno mueve la carpeta a `changes/implemented/00009/`, sin haber generado `plan.md` ni haber encadenado `ms-how`/`ms-do`.

## Trucos

- **Reanálisis sobre una entrada ya en curso**: si invocas `/ms-new {xxxx} ...` o `/ms-how {xxxx}` sobre un `xxxx` que ya existe en `inProgress`, el framework no crea nada nuevo — reanaliza esa misma entrada (funcionalmente en el caso de `ms-new`, ampliando la documentación existente; técnicamente en el caso de `ms-how`, regenerando el `plan.md`). Útil para corregir el rumbo de un cambio sin perder lo ya documentado ni generar carpetas duplicadas.
- **`/ms-fix` para lo trivial**: si el cambio (bug o no) es tan pequeño que no merece pasar por `description.md`/`plan.md`, usa `/ms-fix` igualmente — ella misma detecta que es trivial y lo resuelve al vuelo, ver la opción 2 dentro del Paso 1 más arriba.

## Notas

- Nunca se escribe a mano el `description.md`, el `plan.md` ni se numeran/mueven carpetas — eso lo hace siempre `ms-internal-workflow` (skill interna, no invocable directamente) para mantener esa lógica en un único sitio.
- Un `xxxx` nunca se reutiliza ni se calcula a mano: siempre lo asigna el script de `ms-internal-workflow` recorriendo todas las subcarpetas de `changes/`.
- Las skills verifican siempre que `.claude/ms-context.json` existe y está completo antes de actuar; si falta algo, piden ejecutar/completar `ms-init` en vez de improvisar valores por defecto.
- Siempre que `ms-new`, `ms-fix` o `ms-how` necesitan contexto técnico, lo piden invocando `ms-internal-tech-analysis` (skill interna, no invocable directamente): primero lee la documentación de `framework.docs.tech` ya configurada, y solo explora código si hace falta completar información. Si documentación y código no coinciden, el código manda y la incongruencia se devuelve como hallazgo — nunca se corrige el documento dentro de esa misma skill sin que la skill llamante lo decida.
