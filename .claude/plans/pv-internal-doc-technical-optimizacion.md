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
| [13](#13-notación-lógicacontrato-para-invariantes-complejas--aprobado) | Notación lógica/de contrato (pre/post/inv, lógica proposicional) para invariantes complejas | ✅ aprobado |

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

## 13. Notación lógica/de contrato para invariantes complejas — APROBADO

Para invariantes con condicionales largos, usar notación de contrato (`pre:`, `post:`, `inv:` al estilo Hoare logic) o lógica proposicional directa en vez de la prosa condicional equivalente — asumiendo que, como modelo entrenado en mucho código y matemáticas, esa notación se parsea más rápido y sin ambigüedad que su equivalente en prosa.

Ejemplo — invariante de renovación de token:

Prosa:
```
Un token solo puede renovarse si no ha expirado y si no ha sido revocado manualmente; si el usuario cambió su contraseña después de emitido el token, la renovación también se rechaza, salvo que el token sea de un cliente marcado como "trusted", en cuyo caso se permite igualmente aunque haya cambio de contraseña.
```

Notación de contrato:
```
renew(token):
  pre:  token.expiry > now
        AND NOT token.revoked
        AND (token.issued_at > user.password_changed_at OR token.client.trusted)
  post: token'.expiry == now + ttl
```

Comparación real de este ejemplo: la notación de contrato es más rápida de leer para el lector-modelo en este caso concreto, pero no porque la notación matemática sea intrínsecamente superior — es porque el hecho de fondo ya es una conjunción de condiciones booleanas, y la prosa tiene que serializar ese árbol booleano en conectores ("salvo que", "en cuyo caso") que luego hay que reconstruir al leer; el contrato entrega el árbol ya hecho. En tokens, el ahorro existe pero es moderado (~30-40% en este ejemplo, no un orden de magnitud), porque los identificadores completos (`token.issued_at`, `user.password_changed_at`) siguen siendo el grueso del coste en ambos formatos.

Acotación de aprobación: la regla aplica solo a invariantes que son composiciones de condiciones booleanas (pre/post/invariantes de estado). No debe forzarse sobre contenido no-lógico (justificación de una decisión de diseño, descripción de un flujo con efectos secundarios) — ahí la prosa sigue siendo mejor, y empaquetar eso en notación pre/post lo empeoraría.
