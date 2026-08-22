# Versión 0.9.5b11

Comparativa de responsabilidades entre las skills internas de documentación `docs.tech`/`docs.functional`, tras la incorporación de `pv-internal-doc-style`.

| | `pv-internal-doc-features` | `pv-internal-doc-technical` | `pv-internal-doc-style` |
|---|---|---|---|
| Decide **qué** dice el contenido | No — lo hace `pv-do` | No — solo estilo de redacción, tema/estructura libres | **Sí** — checklist de categorías + qué debe registrar cada una |
| Decide **cómo redactarlo** | No | **Sí** — reglas de escritura generales (fragmentos densos, tablas, código, tags fijos) | **Sí** — reglas de escritura propias, encima de las de `doc-technical` |
| Gestiona el fichero (numeración, `INDEX.md`, `find`/`upsert`) | **Sí** | No | No — eso sigue siendo de `pv-do` |
| Escribe algo en disco | **Sí** (acción `upsert`) | No | No, nunca |
| A qué campo aplica | `docs.functional.featuresDocPathDir` | `docs.tech.architectureDocDir` **y** `docs.tech.styleBibleDocDir` | `docs.tech.styleBibleDocDir` únicamente |

`pv-internal-doc-technical` queda como el caso más "puro" de las tres: ni decide contenido ni gestiona fichero, solo carga una regla de redacción compartida por las dos áreas de `docs.tech`. `pv-internal-doc-style` se apoya en ella (la sigue invocando `pv-do` como base) y le añade la capa de "qué" que a `doc-technical` le falta, pero solo para `styleBibleDocDir`.
