---
name: es-translate
description: Revisión literaria y traducción al español de cualquier texto técnico o destinado a usuario final (documentación, manuales de usuario, textos de interfaz, mensajes de error, ayuda contextual, README, notas de versión...). Si el texto ya está en español, hace una pasada de revisión editorial (claridad, tono, gramática, terminología consistente); si está en otro idioma, lo traduce al español con esos mismos criterios en vez de traducir literalmente. Preserva código, marcado, variables/placeholders y estructura del documento. Trigger: /es-translate, o cuando el usuario pide traducir o revisar en español un texto técnico o de cara a usuario.
argument-hint: <texto a traducir/revisar, o ruta a un fichero>
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.4-beta1
  uses: []
---

# es-translate

Traduce al español o revisa editorialmente en español cualquier texto técnico o destinado a usuario final, priorizando siempre que el resultado sea **claro, natural y legible** para quien lo lea — nunca una traducción literal palabra por palabra ni un español artificioso o calcado del inglés. Es una skill autónoma, de uso directo por el usuario; no depende del framework `pv-*` ni de `.claude/pv-context.json`.

Sirve tanto para **documentación/textos largos** (manuales, guías, README, changelog) como para **microcopy de interfaz** (etiquetas, botones, mensajes de error, tooltips, notificaciones) — el criterio de calidad es el mismo en ambos casos, pero las restricciones de espacio y tono cambian: el microcopy debe ser lo más corto posible sin perder claridad.

## 1. Determinar el input y el idioma de origen

- Si el usuario ha pasado el texto directamente en el prompt, trabaja sobre ese texto.
- Si ha pasado una ruta de fichero, léelo con la herramienta `Read`. Si es un fichero grande o con muchas secciones independientes (p.ej. documentación con varios apartados), puedes procesarlo por secciones, pero mantén coherencia terminológica entre todas.
- Detecta el idioma de origen del texto. Si ya está en español, el trabajo es una **revisión editorial** (paso 3). Si está en cualquier otro idioma, el trabajo es una **traducción** (paso 3), aplicando los mismos criterios de calidad que en la revisión — no una conversión mecánica.
- Decide la variante de español antes de empezar: por defecto usa **español neutro** (sin modismos marcadamente regionales, válido tanto para España como para Latinoamérica), salvo que el usuario indique una variante concreta (p.ej. español de España, con "vosotros" y su léxico, o español latinoamericano). Si el texto de origen ya está en una variante concreta de español y no hay instrucción explícita, respétala en la revisión.
- Si el texto mezcla fragmentos que no deben tocarse (código, nombres de comandos, rutas de fichero, nombres propios de producto) con prosa que sí, distíngueles antes de empezar (ver paso 4).

## 2. Entender el destinatario y el registro

Antes de traducir/revisar, identifica el tipo de texto para ajustar el registro:

| Tipo de texto | Registro |
|---|---|
| Documentación técnica (arquitectura, API, guías para developers) | Preciso, directo, terminología técnica consistente. Se asume lector con conocimiento técnico. |
| Manual de usuario / ayuda / onboarding | Sencillo, sin jerga innecesaria, orientado a la tarea que el usuario quiere completar. Se asume lector sin conocimientos técnicos. |
| Microcopy de UI (botones, labels, tooltips, mensajes de error/éxito) | Muy breve, imperativo o nominal según el elemento, sin ambigüedad, cabe en el espacio disponible. |
| Comunicación (changelog, notas de versión, emails) | Claro y directo, tono cercano pero profesional, sin relleno. |

Si no está claro a qué categoría pertenece el texto, pregunta al usuario antes de asumirlo — el registro cambia bastante el resultado. Decide también, si no es evidente por el contexto, si el texto debe tutear o tratar de usted al lector, y mantén esa decisión de forma consistente en todo el texto.

## 3. Traducir o revisar

Aplica siempre estos criterios, tanto si traduces como si revisas un texto ya en español:

- **Naturalidad sobre literalidad.** Si una traducción literal suena forzada, calcada del inglés o poco natural en español, reformula la frase entera en vez de traducir palabra por palabra. El objetivo es que el resultado se lea como si se hubiera escrito originalmente en español, no como una traducción.
- **Frases claras, sin calcos sintácticos del inglés.** Evita estructuras copiadas directamente del inglés que suenan forzadas en español: voz pasiva en exceso (el español prefiere la voz activa o la pasiva refleja con "se"), gerundios usados como adjetivo ("una caja conteniendo" → "una caja que contiene"), o el uso excesivo de posesivos donde el español los omite ("levanta tu mano" → "levanta la mano").
- **Voz activa e imperativo.** Usa voz activa por defecto. Para instrucciones al usuario, usa el imperativo ("Selecciona el fichero", no "El fichero debería ser seleccionado" ni "Deberías seleccionar el fichero").
- **Terminología consistente.** Usa siempre el mismo término en español para el mismo concepto a lo largo de todo el texto — no varíes por variedad estilística. Si el texto forma parte de un producto con terminología ya establecida (nombres de funciones, botones, conceptos del dominio, anglicismos ya asentados como "email" o "software"), mantenla; si no la conoces, pregunta antes de inventar una traducción de un término clave que se repita.
- **Anglicismos con criterio.** No traduzcas a la fuerza anglicismos ya asentados y de uso natural en español técnico (software, email, hardware, backup, online) cuando forzar su traducción sonaría artificial. Sí evita anglicismos innecesarios cuando existe un término español igual de claro y de uso común (usa "aplicar"/"guardar" en vez de "aplicar un submit"; usa "iniciar sesión" en vez de "hacer login" si el registro es de cara a usuario final).
- **Convenciones estándar de español técnico**: tratamiento (tú/usted) consistente en todo el texto según lo decidido en el paso 2; puntuación española (signos de apertura ¿ ¡ en preguntas/exclamaciones cuando el registro es de cara a usuario, comillas angulares « » o comillas altas " " según la convención del proyecto — si no hay convención previa, usa comillas altas " " por ser las más comunes en contenido digital); coma antes de "y" solo cuando evita ambigüedad, no como norma fija (a diferencia de la coma de Oxford en inglés); números del cero al nueve en palabras salvo en UI (donde van en dígitos).
- **Tono según el registro del paso 2.** Un manual de usuario no debe sonar como documentación de API, y viceversa.
- **Ninguna ambigüedad.** Si el texto de origen es ambiguo (p.ej. un pronombre sin referente claro, una instrucción que podría interpretarse de dos formas), no traduzcas la ambigüedad tal cual: resuélvela con el sentido más probable y anótalo como duda al entregar el resultado (paso 5), o pregunta si el texto es corto y la ambigüedad es crítica.

## 4. Preservar lo que no se traduce

No traduzcas ni alteres:

- Bloques de código, nombres de variables, comandos, rutas de fichero, valores de configuración.
- Placeholders/variables de interpolación (`{nombre}`, `%s`, `{{var}}`, etc.) — mantenlos exactamente igual y en la misma posición relativa si la gramática española lo permite; si el orden natural en español obliga a mover el placeholder de sitio dentro de la frase, hazlo pero verifica que el placeholder sigue siendo válido sintácticamente en el nuevo contexto.
- Nombres propios de producto, marca, o términos que el usuario indique explícitamente que deben quedar igual.
- Marcado (Markdown, HTML, JSX, etc.): conserva la misma estructura de encabezados, listas, enlaces y énfasis del original, traduciendo solo el texto visible.

## 5. Entregar el resultado

- Si el input era texto directo en el prompt, entrega el resultado en el mismo turno, listo para copiar.
- Si el input era un fichero, pregunta al usuario si quiere que edites el fichero directamente (o un fichero nuevo, si se trata de una traducción que convive con el original en otro idioma) o si prefiere recibir el resultado en el chat — no asumas cuál de las dos quiere.
- Si al traducir/revisar tuviste que resolver alguna ambigüedad del original, decidir una variante de español, o tomaste una decisión de terminología no evidente (p.ej. un término del dominio sin traducción única establecida), enuméralas brevemente al final como **Notas de traducción** — no las mezcles en el cuerpo del texto entregado.
</content>
