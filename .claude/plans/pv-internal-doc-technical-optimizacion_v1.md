# Plan de implementación — optimización de `pv-internal-doc-technical`

Implementa las propuestas **aprobadas** en [pv-internal-doc-technical-optimizacion_01.md](pv-internal-doc-technical-optimizacion_01.md): #2, #4, #6, #7, #8, #10, #11, #12, #13.

Fuera de alcance (no implementar en este plan): #1 y #3 (descartadas), #5 y #9 (siguen en estado "🔍 analizando" — no aprobadas todavía). Si se aprueban más tarde, extienden este mismo documento con una fase adicional.

Archivo único a modificar: [.claude/skills/pv-internal-doc-technical/SKILL.md](../skills/pv-internal-doc-technical/SKILL.md).

## Mapeo propuesta → cambio en SKILL.md

| Propuesta | Sección afectada | Tipo de cambio |
|---|---|---|
| #6 notación compacta | Regla 2 (ya existe) | Ampliar ejemplo/alcance: no solo firmas de función, también parámetros con default/opcionalidad sueltos en prosa |
| #7 anti-anafóricas | Reglas 1/8 | Nueva regla explícita |
| #8 sin intensificadores sin cifra | Reglas 1/8 | Nueva regla explícita |
| #10 término único por concepto | — | Nueva regla explícita |
| #2 tag `[gotcha]` | Regla 6 (tags fijos) | Extender el vocabulario cerrado de tags con `[gotcha]` + criterio de uso |
| #4 IDs estables citables | — | Nueva sección de convención (anchors + sintaxis de referencia cruzada) |
| #11 grafo de dependencias | — | Nueva sección de convención (`depends_on:`/`invalidates:` por sección) |
| #12 invariantes como asserts | — | Nueva regla + ejemplo |
| #13 notación de contrato | — | Nueva regla + ejemplo + acotación de cuándo NO aplica |

## Fase 1 — Reglas de redacción (extienden la lista numerada actual)

Insertar como nuevas reglas dentro de "## Writing rules" (renumerando 9+), sin tocar la numeración de las 8 existentes salvo el punto de ampliación de la regla 2:

1. **Regla 2 (editar, no añadir):** ampliar el enunciado y ejemplo para cubrir explícitamente parámetros/valores con default u opcionalidad expresados en prosa (caso #6), no solo firmas completas de función. Ejemplo a añadir: `timeout: number = 30s (opcional)` en vez de "recibe un parámetro opcional que por defecto es 30 segundos".
2. **Regla nueva — prohibir referencias anafóricas (#7).** Nunca "esto", "dicho X", "el mismo", "el anterior" cuando se puede repetir el nombre exacto del identificador/concepto. Aplica también a nombres de sección referenciados en prosa.
3. **Regla nueva — prohibir intensificadores sin cifra (#8).** Ningún adjetivo/adverbio de intensidad ("muy", "bastante", "poco frecuente", "rápido") sin una cifra o unidad que lo respalde. O se cuantifica (ms, %, número de casos) o no se escribe la afirmación.
4. **Regla nueva — término único por concepto (#10).** Una vez elegido un término para un concepto del proyecto (p.ej. "endpoint"), prohibida la variación sinonímica ("ruta", "handler") dentro de todo `docs.tech`, incluso entre documentos distintos. Aclarar que esto prevalece sobre estilo/elegancia de redacción — la repetición no es un defecto aquí.
5. **Regla nueva — anti-expectativa `[gotcha]` (#2):** añadir al vocabulario cerrado de tags de la regla 6 actual. Redacción: `[gotcha]` marca un hecho que contradice el patrón/convención por defecto que un lector con conocimiento general de software asumiría. Ejemplo a incluir (tomado del doc de análisis): `deleteUser(id)` no borra físicamente, solo `active=false`.
6. **Regla nueva — invariantes como asserts ejecutables (#12).** Cuando una invariante es verificable mecánicamente, expresarla como assert en pseudo-código/código real (`assert token.expiry <= 3600`) en vez de (o adicionalmente a) prosa.
7. **Regla nueva — notación de contrato para invariantes compuestas (#13).** Para invariantes que son composición de condiciones booleanas (pre/post/inv), usar notación tipo Hoare (`pre:`, `post:`, `inv:`) o lógica proposicional en vez de prosa condicional encadenada ("salvo que", "a menos que"). **Acotación explícita a copiar del doc _01**: esta regla aplica solo a contenido lógico-booleano; no debe forzarse sobre justificación de diseño ni descripción de flujos con efectos secundarios, donde la prosa sigue siendo mejor. Incluir el ejemplo completo de `renew(token)` del doc de análisis (versión prosa vs. contrato) como ilustración canónica.

## Fase 2 — Convenciones estructurales nuevas (secciones nuevas, no reglas de estilo de frase)

Añadir dos subsecciones nuevas después de "## Writing rules" y antes de "## Language-independence":

### 2.1 IDs estables y referencias cruzadas (#4)

- Sintaxis fija: `<!-- id: kebab-case-id -->` inmediatamente antes del bloque/sección que define el hecho o decisión.
- Sintaxis de referencia desde otro documento: `ver docs.tech#id` (o equivalente en el idioma resuelto, manteniendo `docs.tech#id` literal como parte fija, análogo a los tags ingleses de la regla 6).
- Regla de uso: si un hecho/invariante ya tiene id en otro doc `docs.tech`, referenciarlo en vez de reescribirlo — mismo principio que la regla 5 actual (apuntar en vez de duplicar), extendido a documento↔documento.
- Aclarar que el id se asigna solo a hechos/decisiones candidatas a ser citadas desde otro doc, no a cada línea — evitar sobre-etiquetado.

### 2.2 Grafo de dependencias entre secciones (#11)

- Bloque fijo al principio de cada sección (cuando la sección tenga dependencias relevantes): `depends_on: [id1, id2]` / `invalidates: [id3]`, usando los mismos ids de 2.1.
- `depends_on`: secciones/ids que el lector-modelo debería tener en contexto antes de confiar en esta sección.
- `invalidates`: ids de otras secciones/documentos que esta sección reemplaza o contradice (útil si una decisión posterior anula una anterior documentada en otro sitio).
- Aclarar que el bloque es opcional por sección — solo cuando existe una dependencia real; no rellenar con `depends_on: []` por defecto.

## Fase 3 — Consistencia con "Language-independence"

Revisar si alguna regla nueva necesita entrar en la lista de "structural rather than grammatical" al final del archivo:

- `[gotcha]` → mismo trato que los tags ingleses ya existentes (`[breaking]`, etc.): añadir a la frase que dice "fixed English tags" para que quede explícito que el vocabulario cerrado ahora incluye `[gotcha]`.
- Anti-anafóricas, anti-intensificadores, término único, asserts, notación de contrato → son estructurales/léxicas, no gramaticales de un idioma concreto; añadir cada una a la enumeración final ("Everything else above... is structural rather than grammatical, so it transfers unchanged...") para mantener la garantía explícita que ya hace el documento para las reglas actuales.
- Ojo particular con notación de contrato (#13): verificar que `pre:`/`post:`/`inv:` como palabras clave fijas no dependan del idioma — ya lo son en la propuesta aprobada (van en inglés, mismo patrón que los tags), dejarlo explícito.

## Fase 4 — Actualizar metadata de la skill

- Bump de `metadata.version` en el frontmatter de [SKILL.md](../skills/pv-internal-doc-technical/SKILL.md) (actualmente `0.9.5b11`) según la convención de versionado que uses para cambios de skill (a decidir en el momento: probablemente se resuelve con `/dev-generate-version` o el flujo `pv-version`, no manualmente).

## Fase 5 — Verificación

- Releer el SKILL.md completo tras los cambios y comprobar que:
  - Ninguna regla nueva contradice una existente.
  - El ejemplo de `renew(token)` y el de `deleteUser(id)` quedan reproducidos fielmente desde el doc _01 (no reformulados a mitad).
  - El documento sigue sin prescribir estructura/secciones del doc.tech en sí (fuera de scope — eso es la propuesta #9, no aprobada).
- No hace falta tocar `pv-internal-doc-style` ni `pv-internal-tech-analysis`: ambas consumen `docs.tech` ya escrito, no generan la guía de estilo — confirmar con una lectura rápida de [pv-internal-doc-style/SKILL.md](../skills/pv-internal-doc-style/SKILL.md) que no duplica ninguna de estas reglas antes de cerrar el plan (evitar que quede una regla contradictoria en dos sitios).

## Orden de ejecución sugerido

1. Fase 1 (reglas de redacción) — cambios más mecánicos y aislados.
2. Fase 2 (convenciones estructurales) — requiere más cuidado porque introduce sintaxis nueva (`<!-- id: -->`, `depends_on:`).
3. Fase 3 (consistencia language-independence) — pasada de revisión sobre lo ya escrito.
4. Fase 5 (verificación) antes de Fase 4 (bump de versión), para no versionar algo a medio revisar.
