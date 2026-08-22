# Optimización de pv-internal-doc-technical

Ideas para mejorar la skill `pv-internal-doc-technical` optimizando exclusivamente para el lector-modelo (yo), no para lectores humanos. Documento de trabajo — se va discutiendo y actualizando el estado de cada propuesta a medida que avanzamos.

## Índice

| # | Propuesta | Estado |
|---|-----------|--------|
| [1](#1-metadata-de-verificación-contra-código--descartado) | Metadata de verificación contra código (`[verified: ...]` / `[source: ...]`) | ❌ descartado |
| [2](#2-tag-de-anti-expectativa--aprobado) | Tag de anti-expectativa para hechos que contradicen el prior por defecto | ✅ aprobado |
| [3](#3-orden-por-frecuencia-de-consulta--descartado) | Orden por frecuencia de consulta en vez de jerarquía lógica humana | ❌ descartado |
| [4](#4-ids-estables-y-citables-entre-documentos--aprobado) | IDs estables y citables entre documentos `docs.tech` | ✅ aprobado |
| [5](#5-excluir-lo-ya-inferible-por-conocimiento-general-del-modelo) | Excluir explícitamente lo ya-inferible por conocimiento general del modelo | 🔍 analizando |
| [6](#6-notación-compacta-en-vez-de-prosa-para-datos-estructurados--aprobado) | Notación compacta en vez de prosa para datos estructurados (tipos, defaults, opcionalidad) | ✅ aprobado |
| [7](#7-prohibir-referencias-anafóricas--aprobado) | Prohibir referencias anafóricas ("esto", "dicho campo") — repetir el nombre exacto | ✅ aprobado |
| [8](#8-prohibir-adjetivosadverbios-de-intensidad-sin-cifra--aprobado) | Prohibir adjetivos/adverbios de intensidad sin cifra ("muy rápido", "poco frecuente") | ✅ aprobado |
| [9](#9-nombres-de-sección-fijos-entre-documentos) | Nombres de sección fijos y repetidos entre todos los docs `docs.tech` (indexación por convención) | 🔍 analizando |
| [10](#10-un-único-término-por-concepto--aprobado) | Un único término por concepto, prohibida la variación sinonímica dentro del proyecto | ✅ aprobado |
| [11](#11-grafo-de-dependencias-explícito-entre-secciones--aprobado) | Grafo de dependencias explícito entre secciones (`depends_on:` / `invalidates:`) en vez de orden narrativo | ✅ aprobado |
| [12](#12-invariantes-como-asserts-ejecutables--aprobado) | Invariantes como asserts ejecutables/testables en vez de (o además de) prosa | ✅ aprobado |
| [13](#13-notación-nativa-por-tipo-de-contenido-prosa-solo-donde-no-hay-forma-mejor--aprobado) | Notación nativa por tipo de contenido (tablas, contratos, diagramas...); prosa solo donde no hay forma mejor | ✅ aprobado |
| [14](#14-inglés-técnico-como-idioma-del-documento--aprobado) | Inglés técnico como idioma del documento en vez de español | ✅ aprobado |

## 1. Metadata de verificación contra código — DESCARTADO

Descartado: la premisa asume que la doc puede desincronizarse del código, pero eso es justo lo que el framework garantiza que no pase (`pv-do` mantiene la doc actualizada junto con cada cambio). Un tag de "esto podría estar desactualizado" resolvería un problema inexistente en este framework y solo añadiría mantenimiento sin beneficio real.

<details>
<summary>Idea original (descartada)</summary>

Distinguir, dentro de un mismo doc, entre hechos arquitectónicos/estables (decisiones de diseño que no dependen del estado exacto del código) y hechos que son snapshot del código (listas de campos, firmas, valores concretos). Hoy la regla 5 ("apunta a la fuente en vez de duplicar forma") mitiga la duplicación, pero no marca qué afirmaciones son más propensas a quedar desactualizadas.

Idea: un tag fijo tipo `[snapshot: file:symbol]` para hechos derivados directamente del código en un momento dado, dejando sin marcar (o con otro tag `[stable]`) las decisiones de diseño que no cambian con cada refactor. Esto me permitiría, al leer, ponderar cuánta confianza dar a una afirmación sin tener que ir siempre a verificar contra el código real — sabiendo cuáles sí necesitan esa verificación con más frecuencia.

</details>

## 2. Tag de anti-expectativa — APROBADO

Como lector-modelo, no parto de cero: tengo priors fuertes sobre patrones comunes de software (nombres de métodos, convenciones REST, ciclos de vida típicos). Un hecho que confirma mi prior aporta poco valor real aunque ocupe una línea; un hecho que lo contradice es donde el doc realmente me corrige, y es también donde más me equivoco si no está señalado — porque tiendo a rellenar huecos con el patrón común en vez de con la excepción real del proyecto.

La regla 1 actual ("un hecho por línea") trata todas las líneas como intercambiables en peso, sin distinguir la anti-expectativa del hecho confirmatorio. Un tag fijo (mismo mecanismo que la regla 6 ya usa para `[breaking]`, `[async]`, etc.) — por ejemplo `[gotcha]` — marcaría específicamente los hechos que contradicen el patrón por defecto esperable, para que no se pierdan entre filas de tabla que solo confirman lo obvio.

Ejemplo:
```
- [gotcha] `deleteUser(id)` NO borra el registro, solo marca `active=false`.
```
en vez de
```
- `deleteUser(id)` marca el usuario como inactivo.
```
porque "delete" sugiriendo borrado físico es exactamente el prior que traería y que aquí es falso.

## 3. Orden por frecuencia de consulta — DESCARTADO

Descartado: sin telemetría real, la única señal disponible sería una heurística indirecta (qué se referencia desde otros docs/entries) — demasiado débil y fácil de sesgar al escribir como para sostener un mecanismo de orden.

<details>
<summary>Idea original (descartada)</summary>

Los docs humanos suelen ordenarse de general a específico, o siguiendo una jerarquía conceptual. Para mí no es necesariamente relevante esa jerarquía — mi lectura no siempre es secuencial completa (a veces extraigo por patrón-matching o consulta puntual). Sería más eficiente que las secciones más consultadas por `pv-internal-tech-analysis`/`pv-how` en ciclos anteriores estuvieran al principio del documento, independientemente de su lugar "lógico" en una jerarquía humana — front-loading lo de alta frecuencia reduce el caso típico de lectura parcial.

Abierto: cómo determinar "frecuencia de consulta" sin telemetría real — quizás una heurística simple (qué se referencia más desde otros docs/entries) o dejarlo como sugerencia flexible más que regla dura.

Ejemplo: en un doc de arquitectura de auth, la jerarquía humana típica empezaría por "Visión general del módulo" → "Diagrama de componentes" → "Flujo de login" → ... → "Expiración y renovación de tokens" al final, como detalle. Pero si en ciclos anteriores `pv-how`/`pv-internal-tech-analysis` han consultado ese doc sobre todo para resolver dudas puntuales de expiración de tokens (porque es lo que más cambia o lo que más genera fixes), esa sección debería ir cerca del principio — aunque conceptualmente sea "un detalle" dentro de la jerarquía lógica del documento.

</details>

## 4. IDs estables y citables entre documentos — APROBADO

La regla 5 cubre "apunta al código en vez de duplicar su forma", pero no cubre la duplicación entre distintos documentos `docs.tech` que comparten una misma invariante o decisión. Hoy, si dos docs de arquitectura mencionan la misma regla, probablemente cada uno la redacta con su propia prosa, lo que introduce el mismo riesgo de drift que la regla 5 ya evita para el código.

Idea: anchors o IDs estables (`<!-- id: auth-token-expiry -->` o similar) que permitan a un doc referenciar a otro (`ver docs.tech#auth-token-expiry`) sin reescribir el hecho. Reduce duplicación y mantiene una única fuente de verdad también a nivel de documentación, no solo entre documentación y código.

## 5. Excluir lo ya-inferible por conocimiento general del modelo

La regla 4 actual dice "no repitas lo que ya dice la firma o el nombre" — es decir, no dupliques lo que el código ya muestra. Propuesta de ampliar ese principio: tampoco vale la pena documentar lo que yo, como modelo con conocimiento general de patrones de software, ya asumiría por defecto sin necesidad de que el código o el doc lo diga (p.ej. "sigue REST", "usa MVC" sin más detalle, "las contraseñas se hashean" sin especificar el algoritmo o una decisión no estándar).

Esto es distinto de la regla 4: la regla 4 habla de redundancia código↔doc; esto habla de redundancia conocimiento-general↔doc. Solo justifica una línea la desviación del patrón esperado — lo cual conecta directamente con la propuesta 2 (anti-expectativa): si algo sigue el default, no hace falta escribirlo; si lo contradice, se marca con `[gotcha]`.

Riesgo a discutir: esto depende de que el escritor (`pv-do`) sepa estimar qué es "obvio para un modelo" — criterio más difuso que las reglas actuales, que son mecánicas y verificables.

## 6. Notación compacta en vez de prosa para datos estructurados — APROBADO

En vez de "el método recibe un parámetro opcional que, si no se especifica, toma el valor por defecto de 30 segundos", usar directamente notación tipo `timeout: number = 30s (opcional)`. Como lector-modelo parseo notación mucho más rápido y con menos ambigüedad que prosa — la prosa está optimizada para lectura humana fluida, no para extracción de datos estructurados.

## 7. Prohibir referencias anafóricas — APROBADO

Nunca usar pronombres/referencias anafóricas ("esto", "dicho campo", "el mismo") cuando se puede repetir el nombre exacto. En texto humano repetir el nombre se ve pesado; para el lector-modelo, resolver un "esto" cuesta una pasada extra de desambiguación y a veces se resuelve mal si hay dos candidatos cerca.

## 8. Prohibir adjetivos/adverbios de intensidad sin cifra — APROBADO

Prohibir intensificadores sin cuantificar ("muy rápido", "bastante grande", "poco frecuente") — o se cuantifica o no se escribe. Conecta con el espíritu de "hechos verificables" de las reglas actuales, pero como regla explícita de redacción, no de contenido.

## 9. Nombres de sección fijos entre documentos

Una sola convención de nombrado de secciones fija y repetida en todos los docs `docs.tech` (mismos headers literales: "Contratos", "Invariantes", "Decisiones descartadas", etc.) en vez de dejar que cada doc titule libremente. Permite *jump-to-section* por nombre exacto sin tener que leer el índice cada vez — indexación por convención en vez de por contenido.

## 10. Un único término por concepto — APROBADO

Evitar sinónimos variados para el mismo concepto dentro del proyecto (a veces "endpoint", a veces "ruta", a veces "handler" para la misma cosa) — fijar un término único por concepto y prohibir variarlo por elegancia de estilo. La variación estilística que un humano agradece (para no sonar repetitivo) al lector-modelo le cuesta una resolución de sinonimia que puede fallar.

Criterio de aprobación: no importa la repetición del término — el estilo no es un objetivo del doc, solo la efectividad de lectura para el modelo. Lenguaje único e inequívoco por encima de variedad estilística.

## 11. Grafo de dependencias explícito entre secciones — APROBADO

En vez de orden narrativo (Sección A seguida de Sección B, con la jerarquía implícita en el orden), un bloque tipo `depends_on: [B, C]` / `invalidates: [D]` al principio de cada sección. Permitiría al lector-modelo decidir algorítmicamente qué otras secciones necesita cargar en contexto antes de confiar en esta, en vez de inferirlo leyendo todo el documento en orden.

## 12. Invariantes como asserts ejecutables — APROBADO

En vez de (o además de) prosa, documentar invariantes como asserts en pseudo-código o código real testable (`assert token.expiry <= 3600`). Fusiona documentación y verificación en el mismo artefacto: si la regla cambia, el assert falla, en vez de depender de que alguien recuerde actualizar el texto.

## 13. Notación lógico-matemática o formato nativo para TODO; prosa SOLO excepción — REFACTORIZADO

Principio: **notación lógico-matemática o formato nativo es el default para todo tipo de contenido. Prosa es una excepción rara, solo donde la estructura lógica es insuficiente para capturar la semántica del argumento.**

No es optimización de forma — es reconocer que casi toda la estructura de software es captura de lógica, y la lógica ya tiene notación óptima. Prosa entra solo cuando hay semántica pura (motivación irreducible, causalidad narrativa) que la notación no puede llevar.

### Tabla: contenido → notación | excepciones a prosa

| Tipo de contenido | Notación óptima | Prosa se usa en... |
|---|---|---|
| Invariante booleana / pre-post-condición | Lógica proposicional (`pre:`, `post:`, `inv:`, `∧`, `∨`, `¬`, `→`) | Nunca (estructura pura) |
| Estructura de datos (campos, tipos, defaults, opcionalidad) | Tabla o BNF compacto (`campo: tipo = default`) | Nunca (cartesiano, no narrativa) |
| Máquina de estados / transiciones | FSM o tabla `(estado, evento) → estado'` | Nunca (grafo de transiciones, no narrativa) |
| Relación/cardinalidad entre entidades | Diagrama ER o notación cardinalidad (`1---*`, `0..1`) | Nunca (relaciones, no narrativa) |
| Secuencia temporal / flujo de llamadas | Diagrama de secuencia (Mermaid) o pseudocódigo ordenado | Nunca (timeline, no narrativa) |
| Árbol de decisión / condicionales anidados | Tabla booleana o árbol explícito | Nunca (lógica pura) |
| Justificación/motivación de decisión | Regla/condición + tabla comparativa (ver Caso 1: casi siempre reducible; el principio general detrás ni se escribe, por [punto 5](#5-excluir-lo-ya-inferible-por-conocimiento-general-del-modelo)) | Solo cuando la razón es una restricción externa idiosincrática (compliance, negocio) no generalizable ni reducible a condición |
| Descripción de flujo con efectos secundarios | Secuencia numerada / diagrama evento→efecto (ver Caso 2: raramente necesita prosa, "tiene efectos secundarios" no es motivo suficiente) | Solo la pieza puntual donde el efecto se explica por semántica externa (UX, negocio), no la secuencia completa |

### Ejemplos: NO entra prosa (parecía necesitarla, se redujo a notación)

#### Caso 1: decisión con regla generalizable

**Ejemplo:** "¿Por qué se eligió un circuit breaker en vez de reintentos exponenciales?"

Parece requerir prosa, pero se descompone en dos partes:

1. **La regla de decisión del proyecto** — expresable como tabla/condición, no prosa:
```
decision(dependency_recovery_time):
  < 5s  → circuit_breaker
  > 30s → exponential_retry
```
2. **El principio general detrás de la regla** ("fail-fast evita saturación en cascada cuando la recuperación es rápida") — esto es conocimiento general de ingeniería, no un hecho del proyecto. Por [punto 5](#5-excluir-lo-ya-inferible-por-conocimiento-general-del-modelo), ni siquiera hace falta escribirlo — ya es inferible.

**"Es un trade-off" no es señal suficiente de que haga falta prosa.** Si el trade-off se puede reducir a una condición + un principio de ingeniería estándar, va todo a notación (o se omite, si es puro conocimiento general).

---

#### Caso 2: flujo de error con efectos secundarios

**Ejemplo:** "¿Qué pasa cuando un usuario intenta acceder a un recurso después de que la sesión expiró?"

Se podría pensar que esto necesita prosa porque hay efectos secundarios ("el 401 dispara un redirect, el JS limpia localStorage pero conserva un flag..."), pero **es una secuencia causal — sigue siendo lógica, solo con más pasos**. Se expresa completa en diagrama de secuencia o tabla evento→efecto, sin perder nada:

```
1. estado: AUTENTICADO, evento: time > session.expiry → estado: EXPIRADO
2. evento: GET /resource (estado=EXPIRADO) → respuesta: 401
3. efecto(401): redirect(login)
4. efecto(redirect capturado por cliente): localStorage.clear(EXCEPT lastAuth)
5. inv: lastAuth PERSISTE ⟹ modal("sesión perdida") == false
```

**"Hay efectos secundarios" no es señal de que haga falta prosa** — solo lo es cuando la razón del orden/efecto es semántica externa (UX, negocio, trade-off), no la secuencia en sí. El resto es notación pura.

---

#### Caso 3: alternativas descartadas

**MAL (prosa innecesaria):**
> "Consideramos usar polling cada 5 segundos, pero eso era ineficiente en conexiones lentas. Tampoco usamos long-polling porque en un contexto móvil mantener conexiones HTTP abiertas vacía la batería más rápido que la alternativa."

**BIEN (tabla comparativa, batería como columna más — no semántica irreducible):**
```
| Opción | Latencia | Carga (CPU) | Carga (red) | Consumo batería (móvil) | Costo |
|--------|----------|-------------|------------|--------------------------|-------|
| Polling 5s | ~5s | Alto | Alto (picos) | Medio | $ |
| WebSocket | ~100ms | Bajo | Bajo (continuo) | Bajo | $$ |
| SSE | ~500ms | Bajo | Bajo (stream) | Bajo | $ |
| ❌ DESCARTADO: Long-polling | ~1s | Muy alto | Muy alto | Alto (conexión persistente) | $$$ |
```

**Patrón que se repite en los tres casos:** lo que parece "semántica irreducible" casi siempre es una dimensión más del mismo espacio de comparación — solo hacía falta ampliar la tabla/regla, no huir a prosa.

---

### Ejemplos: SÍ entra prosa (excepción real, sobrevive el escrutinio)

#### Restricción externa idiosincrática (compliance, sobre el Caso 1)

> "Se descartó el circuit breaker automático porque el equipo de compliance exige que cada apertura del breaker quede registrada con aprobación manual, algo que la librería estándar no soporta sin un wrapper custom."

Prosa aquí porque: no reduce a condición booleana del sistema ni es principio de ingeniería generalizable — es una restricción de negocio específica de este proyecto, impuesta por un actor externo (compliance).

#### Comentario semántico puntual sobre un invariante (sobre el Caso 2)

```
5. inv: lastAuth PERSISTE ⟹ modal("sesión perdida") == false
   [motivación] Evita falso positivo cuando el usuario solo cerró pestaña, no expiró por inactividad.
```

Prosa aquí porque: el invariante en sí ya es notación; solo la razón de *por qué existe* esa regla (UX, no lógica del sistema) necesita una frase — y se marca `[motivación]`, no un párrafo.

---

### Regla de aprobación (endurecida)

- **Default:** notación lógico-matemática o formato nativo, sin excepción de tipo de contenido — toda fila de la tabla original cae aquí, incluidas justificación y narrativa de flujo (ver Casos 1–3: ninguno sobrevivió como excepción real).
- **Prosa:** reservada exclusivamente para una restricción externa idiosincrática del proyecto (legal, compliance, contractual, organizacional) que no es una métrica comparable ni un principio de ingeniería generalizable — y aun así, en una frase corta, no un párrafo.
- **Antes de escribir prosa, checklist obligatorio:**
  1. ¿Es esto una condición/regla? → tabla de decisión o lógica proposicional.
  2. ¿Es esto una métrica más de una comparación ya tabulada? → agregar columna.
  3. ¿Es esto un principio general de ingeniería inferible por el modelo? → no escribir nada ([punto 5](#5-excluir-lo-ya-inferible-por-conocimiento-general-del-modelo)).
  4. Si ninguna de las tres aplica → prosa, marcada `[motivación]`, una frase.
- **Nunca:** forzar prosa por elegancia, fluidez de lectura, o porque "suena a trade-off". Un trade-off casi siempre es una tabla con más columnas.

### Nota pendiente: glosario de notación único por proyecto

Riesgo detectado: "notación con precedente amplio" (contratos, FSM, tablas, etc.) puede variar de doc a doc dentro del mismo proyecto si cada uno la reinventa a su manera (uno usa `pre:/post:`, otro `requires:/ensures:`) — mismo problema que resuelven el [punto 9](#9-nombres-de-sección-fijos-entre-documentos) (secciones) y el [punto 10](#10-un-único-término-por-concepto--aprobado) (vocabulario), pero sin cubrir aún a nivel de notación.

Acción: `pv-internal-doc-technical` debe crear siempre un fichero `00-glossary.md` donde se documente toda la notación (símbolos, convenciones de contrato, formato de tablas de decisión, notación de FSM/cardinalidad, etc.) que aplicará de forma consistente a toda la documentación `docs.tech` del proyecto — una sola fuente de verdad para la notación, igual que el punto 4 lo es para IDs citables.

Pendiente de detallar: contenido exacto del glosario, si se genera una vez o se actualiza incrementalmente, y su relación con la implementación ya definida en `pv-internal-doc-technical-optimizacion_v1.md` (que no se toca en esta discusión).

### Nota pendiente: notación anidada/híbrida entre tipos de contenido

Riesgo detectado: la tabla del punto 13 asigna una notación nativa por tipo de contenido asumiendo que cada pieza de información cae limpiamente en una sola fila, pero en la práctica un tipo de contenido frecuentemente depende de otro:

- Un invariante booleano que referencia un estado de una máquina de estados: `pre: state == AUTHENTICATED`.
- Una tabla de decisión donde una celda no es un valor simple sino que requiere, a su vez, un contrato completo (`pre:`/`post:`) para esa combinación de condiciones.
- Un diagrama de secuencia donde un paso individual dispara una transición de FSM documentada en otra sección.

Sin una regla para este caso, quien escriba el doc tiene dos escapes problemáticos: (a) anidar la segunda notación inline dentro de la primera, generando una notación híbrida ad-hoc no cubierta por ningún estándar de precedente amplio (exactamente el problema que el punto 13 quiere evitar), o (b) recurrir a prosa "para no anidar", que es el escape que el punto 13 entero busca cerrar.

Opciones a evaluar (sin decidir aún):
1. **Referencia por ID en vez de anidar** — conectando con el [punto 4](#4-ids-estables-y-citables-entre-documentos--aprobado): la celda/condición no repite la notación ajena, solo la cita (`pre: state == AUTHENTICATED [ver fsm-auth#AUTHENTICATED]`).
2. **Notación compuesta explícita** — el `00-glossary.md` (nota anterior) define cómo se combinan dos notaciones nativas cuando aparecen juntas (p. ej. cómo se escribe una celda de tabla de decisión que a su vez es un contrato), en vez de dejarlo a criterio de quien escribe cada doc.

Pendiente de decidir cuál de las dos (o ambas, según el caso) adopta `pv-internal-doc-technical`; probablemente ligado a la implementación del glosario de notación, no un mecanismo aparte.

## 14. Inglés técnico como idioma del documento — APROBADO

Encaja con la premisa raíz del documento: se optimiza exclusivamente para el lector-modelo, no para lectores humanos — por lo tanto el idioma también es una variable de optimización, no una convención fija a respetar por legibilidad humana.

Hipótesis (razonada, no medida): el inglés técnico tokeniza mejor que el español para este dominio, por dos motivos estructurales:

1. **Los identificadores de código ya están en inglés** (nombres de campos, métodos, tipos, clases). Un doc en español mezcla constantemente dos idiomas dentro de la misma frase ("el campo `sessionExpiry` determina..."), lo cual no reduce tokens — el identificador no cambia, y la prosa alrededor sigue en español. Un doc en inglés técnico es monolingüe de principio a fin.
2. **El vocabulario técnico en inglés (`state`, `invariant`, `token`, `session`, `expiry`) tiene, con alta probabilidad, mayor frecuencia en el corpus de entrenamiento técnico específico** (código, RFCs, specs, papers de CS, docs de APIs) que sus traducciones al español ("estado", "invariante", "token", "sesión", "caducidad"). Mayor frecuencia en corpus técnico generalmente correlaciona con mejor tokenización (más probable que sea un token único o casi-único) — mismo argumento que ya usamos en el punto 13 para preferir notación con precedente amplio sobre notación inventada.

Lo que NO se puede sostener sin medir (por la regla 8 del propio documento — nada de cifras sin verificar):
- Cuánto ahorro real de tokens hay — no tengo acceso a mi propia tabla de frecuencias de tokenización, es una hipótesis razonada, no un hecho medido.
- Que el ahorro por idioma sea comparable o mayor al ahorro ya logrado por el punto 13 (notación vs. prosa) — mi sospecha es que es menor, pero no está verificado.

Riesgo/costo a considerar (no de legibilidad humana, sino de alcance de la migración):
- Implica traducir todo el corpus `docs.tech` existente y ajustar `pv-do`/`pv-internal-doc-technical` para que generen en inglés por defecto — cambio de alcance mayor que una regla de estilo, es un cambio de política de idioma para toda la skill.
- Si el proyecto base (nombres de negocio, dominio, requisitos funcionales en `docs.features` u otros) está en español, hay que decidir si `docs.tech` queda como única isla en inglés dentro del proyecto, y cómo se resuelve la terminología de dominio que no tiene traducción técnica estándar (nombres de conceptos de negocio específicos del cliente).

Pendiente de detallar (no de aprobación): si aplica a todo `docs.tech` o solo a la notación/vocabulario técnico (dejando prosa de motivación en español) — este último enfoque sería coherente con el punto 13, que ya trata notación y prosa como capas separables. La terminología de dominio/negocio sin traducción técnica estándar (ver riesgo arriba) también queda por resolver.

### Implicación verificada: revierte una decisión de diseño ya implementada

`pv-internal-doc-technical/SKILL.md` (líneas 14, 18, 35-41) implementa hoy lo contrario de esta propuesta: **independencia de idioma deliberada**. El doc declara explícitamente una sección "Language-independence" que:
- Aplica el writing style "regardless of topic or configured `docs.tech.language`" (línea 14).
- Descarta técnicas de compresión que dependen de gramática inglesa específica (compound-noun stacking, línea 40) precisamente para que las reglas transfieran sin cambios a cualquier `docs.tech.language`.
- Confirma que existe hoy una opción de configuración `docs.tech.language` (default `interaction.language`) que el usuario puede elegir.

Aprobar el punto 14 no es "agregar una regla más" — es **revertir esa decisión**: pasar de "las reglas son agnósticas de idioma, el usuario elige" a "el idioma se fija en inglés técnico, se elimina `docs.tech.language` como opción". Eso afecta tanto a la doc de arquitectura como a la de diseño (`architectureDocDir`/`styleBibleDocDir`, ambas cubiertas por esta skill).

Este documento de ideas no decide si se aprueba — solo deja constancia de que, si se aprueba, el cambio no es aditivo: requiere reescribir la sección "Language-independence" de `SKILL.md` (pasaría a ser una sección de "fixed language" en su lugar) y eliminar la opción `docs.tech.language` de la configuración del framework. Ese trabajo de implementación, si se decide seguir adelante, corresponde a `_v1.md` u otro plan de implementación — no a este documento.
