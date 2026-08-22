# Changelog de Previo v0.9.5b11 (desde v0.9.21)

## Índice

- ⭐[Novedades](#novedades)
  - Auditoría y reparación de la configuración del framework (`pv-update`)
  - Todas las skills ahora bloquean su ejecución hasta verificar la configuración del framework
  - Configuración de idioma por tipo de documento
  - Reglas de estilo de escritura para la documentación técnica
  - Andamiaje automático del proyecto
  - Generación de documentación para código ya existente
  - La documentación existente puede adoptarse tal cual
  - Puntuación de riesgo visible en los informes de estado
  - Recuento de versiones en el resumen de estado
  - Refinamiento colaborativo al promover una idea del todo
  - Posibilidad de eliminar una idea del todo
  - La redacción del changelog ahora queda aislada de cierres concurrentes
- ✏️[Cambios](#cambios)
  - La carpeta de trabajo ya no es configurable al inicializar, y su valor por defecto cambió
  - El fichero del procedimiento de build se movió a una carpeta de proyecto renombrada
  - La documentación de marcador de posición se genera después del andamiaje, no durante las preguntas
  - Se aumentó el ancho de la numeración de códigos de cambio
  - La línea base de `skillModels` ahora se registra siempre
  - El informe de estado tolera la ausencia de la carpeta de cambios
  - Cambió el orden de "en curso" en el informe de estado
  - La carpeta de staging de cambios cerrados queda excluida de los recuentos de estado
  - Se amplió el script independiente `pv.py`

## ⭐Novedades

- **Auditoría y reparación de la configuración del framework (`pv-update`)** — Una nueva skill audita `pv-context.json` contra el esquema del framework, comprueba que las skills referenciadas y las rutas en disco existan, verifica que los documentos de cambio/fix no se hayan alterado ni traducido incorrectamente, detecta códigos de cambio duplicados, confirma que todas las skills `pv-*` compartan la misma versión, y concilia la versión instalada con la última verificada. Corrige lo que puede determinar sin ambigüedad y solo se detiene a preguntar al usuario cuando `pv-context.json` no se puede interpretar o se detecta un downgrade. `pv-init` ahora le cede el control cuando sus propias comprobaciones detectan algo roto.
- **Todas las skills ahora bloquean su ejecución hasta verificar la configuración del framework** — `pv-new`, `pv-fix`, `pv-how`, `pv-do`, `pv-status`, `pv-todo` y `pv-version` ahora comprueban al arrancar la versión instalada del framework contra la última versión verificada registrada en `pv-context.json`, y se niegan a continuar si no coinciden, si nunca se registró una verificación, o si se detectó un downgrade. **Acción requerida al actualizar: ejecuta `pv-update` una vez antes de usar cualquier otra skill `pv-*`.**
- **Configuración de idioma por tipo de documento** — El framework ahora puede configurarse con idiomas distintos para la conversación, los documentos de cambio/fix en curso, el changelog de versión, la documentación funcional y la documentación técnica, en lugar de un único idioma implícito para todo. `pv-init` pregunta esto durante la configuración inicial, y cada skill `pv-*` que escribe contenido de cara al usuario ahora lo hace en el idioma configurado para ese tipo de documento. Esto añade nuevos campos al esquema de `pv-context.json`.
- **Reglas de estilo de escritura para la documentación técnica** — Una nueva skill, `pv-internal-doc-technical`, impone cómo se escribe la documentación de arquitectura y la guía de estilo (fragmentos densos de hechos, código/firmas en lugar de prosa explicativa, tablas para estructuras paralelas, etiquetas de vocabulario fijo), ya que esta documentación la leen otros pasos del framework y no una persona. `pv-do` ahora carga estas reglas antes de redactar o editar esa documentación.
- **Andamiaje automático del proyecto** — `pv-init` ahora crea por sí mismo toda la estructura de carpetas base del framework justo después de escribir la configuración, en lugar de dejar la creación de carpetas a la primera skill que las necesitara.
- **Generación de documentación para código ya existente** — Cuando `pv-init` se ejecuta sobre un proyecto que ya tiene código fuente, ahora ofrece analizar ese código y generar documentación de arquitectura, estilo y funcionalidades a partir de él, con una profundidad "mínima" o "completa" a elección del usuario.
- **La documentación existente puede adoptarse tal cual** — Si un proyecto ya tiene documentación de arquitectura, estilo o funcionalidades fuera de la carpeta de trabajo del framework, `pv-init` ahora ofrece moverla sin modificarla, en lugar de solo reconocer la que ya está en su sitio o exigir una migración completa.
- **Puntuación de riesgo visible en los informes de estado** — Los informes de `pv-status` ahora muestran la puntuación de riesgo de cada entrada ya planificada junto al resto de sus datos; las entradas aún sin planificar se muestran sin puntuar.
- **Recuento de versiones en el resumen de estado** — El informe principal de `pv-status` ahora también muestra cuántas versiones se han preparado, junto a los totales existentes por estado.
- **Refinamiento colaborativo al promover una idea del todo** — Convertir una idea del todo en un cambio documentado ahora ofrece explícitamente seguir desarrollando la idea en conversación antes de redactarla, en lugar de documentarla tal cual.
- **Posibilidad de eliminar una idea del todo** — Una idea en cola en el backlog del todo ahora puede eliminarse directamente, en lugar de solo poder promoverse al flujo normal de cambio/fix.
- **La redacción del changelog ahora queda aislada de cierres concurrentes** — `pv-internal-changelog` ahora traslada cada entrada cerrada pendiente a una copia de trabajo aislada antes de redactar el changelog, de forma que un cambio/fix cerrado en otro sitio mientras se prepara una versión ya no puede interferir con el changelog que se está redactando.

## ✏️Cambios

- **La carpeta de trabajo ya no es configurable al inicializar, y su valor por defecto cambió** — `pv-init` ya no pregunta dónde debe guardar su trabajo el framework: ahora siempre se fija en una subcarpeta dedicada en la raíz del repositorio (antes el valor por defecto era la propia raíz del repositorio, y siempre se preguntaba al usuario si quería confirmarla o cambiarla). Quien quiera una ubicación distinta debe editar `pv-context.json` a mano.
- **El fichero del procedimiento de build se movió a una carpeta de proyecto renombrada** — El procedimiento de build específico del proyecto que lee y escribe `pv-version` ahora vive en una carpeta llamada `stuff/` en lugar de `framework/`. Los proyectos existentes necesitan reubicar este fichero en la nueva carpeta; `pv-update` cubre esto en su paso de reparación.
- **La documentación de marcador de posición se genera después del andamiaje, no durante las preguntas** — Antes, `pv-init` redactaba a mano una versión inicial de la documentación de arquitectura, estilo y funcionalidades que faltara mientras hacía las preguntas de configuración. Ahora el paso de andamiaje crea primero las carpetas con un marcador de posición mínimo, y solo después pregunta qué quiere añadir el usuario.
- **Se aumentó el ancho de la numeración de códigos de cambio** — El ancho por defecto, con ceros a la izquierda, de los códigos de cambio/fix aumentó de 4 a 5 dígitos, y ahora siempre se escribe explícitamente en la configuración.
- **La línea base de `skillModels` ahora se registra siempre** — `pv-init` ahora siempre inspecciona y escribe el modelo/esfuerzo real de cada skill instalada como línea base de `skillModels`, incluso cuando el usuario no personaliza nada; antes esta sección solo se escribía si el usuario pedía cambiar algo.
- **El informe de estado tolera la ausencia de la carpeta de cambios** — `pv-status` ya no da error en un proyecto recién inicializado que todavía no tiene carpeta de cambios; ahora se informa igual que una carpeta existente pero vacía.
- **Cambió el orden de "en curso" en el informe de estado** — Dentro del informe de estado completo, las entradas ya planificadas (pendientes de implementación) ahora se listan antes que las entradas pendientes de análisis técnico, al revés que antes.
- **La carpeta de staging de cambios cerrados queda excluida de los recuentos de estado** — `pv-status` ahora reconoce el área transitoria de staging que se usa mientras se redacta un changelog y la excluye de los totales y listados, en lugar de contarla como una entrada real.
- **Se amplió el script independiente `pv.py`** — La herramienta `pv.py` que se distribuye en cada proyecto (utilizable sin Claude Code) ganó un submenú de ajustes/configuración, una forma de explorar versiones anteriores y leer su changelog, búsquedas por id y por contenido, y una opción para eliminar ideas, además de exponer los cambios del framework descritos arriba (como la sincronización de modelos de skill).
