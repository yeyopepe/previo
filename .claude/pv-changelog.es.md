# Previo v0.9.5b10 changelog (desde v0.9.21)

## Índice

- ⭐ [Nuevo](#nuevo)
  - Soporte multi-idioma configurable
  - Verificación de versión del framework
  - Añadida la skill `pv-update`
  - Añadida una skill compartida de estilo de escritura para documentación técnica
  - El framework ahora incluye una guía de usuario
  - Indicador de riesgo visible en los informes de estado
  - Búsqueda añadida a la vista de estado en terminal
  - Nueva subcarpeta fija para ficheros diversos del framework
- ✏️ [Cambios](#cambios)
  - Umbral de riesgo para fixes "fast" relajado
  - Carpeta de trabajo por defecto de `pv-init` cambiada y configuración simplificada
  - Documentación de marcador de posición creada vacía en vez de pre-redactada
  - `pv-init` ahora delega la reparación de desviaciones/corrupción en `pv-update`
  - Desglose de "en curso" reordenado y renombrado en `pv-status`
  - `pv-status` ya no falla en un proyecto nuevo
  - Datos internos de staging excluidos del recuento de estado
  - Informe de estado en terminal reestructurado en páginas
  - La redacción del changelog ahora aísla las entradas en staging
  - Corregida una resolución incorrecta de carpetas para configuraciones de carpeta de trabajo personalizadas

## ⭐Nuevo

- **Soporte multi-idioma configurable** — `pv-init` ahora pregunta, en la configuración inicial, el idioma de interacción en el chat y, opcionalmente, idiomas separados para los documentos de cambios/fixes en curso, el changelog de versión, la documentación de features y la documentación técnica. Todas las skills que escriben o hablan con el usuario (`pv-do`, `pv-fix`, `pv-how`, `pv-new`, `pv-status`, `pv-todo`, `pv-version`, y las skills compartidas `pv-internal-doc-features`, `pv-internal-mockups-ascii`/`html`, `pv-internal-tech-mermaid`, `pv-internal-workflow`, `pv-internal-changelog`) ahora respetan esta configuración en vez de escribir siempre en inglés, manteniendo fijas en inglés un conjunto de etiquetas estructurales (p.ej. `Area`, `Available in`, `Code`, `Since`) para que los scripts que las parsean sigan funcionando. Los proyectos que consumen el framework deberían volver a ejecutar `pv-update`/`pv-init` para incorporar los nuevos campos de configuración.
- **Verificación de versión del framework** — `pv-context.json` ahora guarda un campo `frameworkStatus` con la última versión verificada del framework y si está actualmente bloqueado. Antes de hacer cualquier trabajo, `pv-do`, `pv-fix`, `pv-how`, `pv-init`, `pv-new`, `pv-status`, `pv-todo` y `pv-version` comparan ahora ese valor con la versión instalada del framework y se detienen, indicando al usuario que ejecute `pv-update`, si no coinciden o el framework está marcado como bloqueado. Los proyectos que consumen el framework deberían ejecutar `pv-update` tras actualizar el framework para que este estado quede registrado.
- **Añadida la skill `pv-update`** — una nueva skill que audita la configuración y el estado instalado del framework en un proyecto (la forma de `pv-context.json`, las skills referenciadas, las rutas en disco, si el script de lanzamiento distribuido está actualizado, desviaciones de modelo/esfuerzo, marcadores estructurales en los documentos de cambios, códigos de cambio duplicados, y consistencia de versión entre skills) y corrige automáticamente lo que puede determinar sin ambigüedad, deteniéndose a preguntar al usuario solo cuando la configuración no se puede interpretar o una versión instalada parece un downgrade.
- **Añadida una skill compartida de estilo de escritura para documentación técnica** — `pv-internal-doc-technical` prescribe un estilo de escritura denso y centrado en hechos (fragmentos en vez de prosa, tablas para datos paralelos, etiquetas de estado fijas en inglés) para los documentos de arquitectura y biblia de estilo, ya que los leen otras skills del framework en vez de una persona. `pv-do` ahora la sigue siempre que redacta o edita esa documentación.
- **El framework ahora incluye una guía de usuario** — se añadió un documento `pv-guide` (en inglés y español) que recorre de principio a fin la configuración y el uso del framework: configuración inicial, estructura de carpetas, el flujo central documentar → planificar → implementar, la preparación de una versión, un ejemplo completo, y las opciones de personalización.
- **Indicador de riesgo visible en los informes de estado** — `pv-status` ahora lee la puntuación de riesgo técnico que `pv-how` calcula para un plan y la muestra en el informe general, en el listado filtrado por estado, y en las vistas de detalle de terminal, junto con un nuevo recuento total de versiones mostrado al principio del informe.
- **Búsqueda añadida a la vista de estado en terminal** — la pantalla de estado en terminal ahora puede buscar una entrada por su código o por texto coincidente en su descripción, a través de todos los estados del flujo, en vez de filtrar solo por un único estado.
- **Nueva subcarpeta fija para ficheros diversos del framework** — se añadió una subcarpeta `stuff/` junto a las carpetas existentes `changes/`/`versions/`, creada automáticamente durante la configuración, y el fichero de referencia del procedimiento de compilación ahora vive ahí.

## ✏️Cambios

- **Umbral de riesgo para fixes "fast" relajado** — los criterios de `pv-fix` para tratar un cambio como trivial ("fast", saltándose la planificación) ahora permiten hasta un 10% de riesgo para el resto de la aplicación, en vez de exigir exactamente cero riesgo.
- **Carpeta de trabajo por defecto de `pv-init` cambiada y configuración simplificada** — la carpeta de trabajo por defecto ya no es la raíz del repositorio; es una subcarpeta dedicada `previo-sdd`, y ya no se pregunta durante la configuración (se escribe automáticamente, igual que la elección de skills de maquetas/diagramas). Las rutas de las carpetas de documentación (arquitectura, biblia de estilo, features) ahora se resuelven relativas a esa carpeta de trabajo en vez de a la raíz del repositorio, y `pv-init` ofrece mover una carpeta de documentación existente a ella si se encuentra en otro sitio. Los proyectos que consumen el framework deberían volver a ejecutar `pv-init` para adoptar la nueva estructura de carpetas.
- **Documentación de marcador de posición creada vacía en vez de pre-redactada** — cuando `pv-init` configura nuevas carpetas de documentación, ahora las crea vacías y deja rellenar el contenido real para un paso posterior, en vez de generar contenido de marcador de posición estimado de antemano.
- **`pv-init` ahora delega la reparación de desviaciones/corrupción en `pv-update`** — si `pv-init` encuentra un `pv-context.json` roto o inconsistente (JSON inválido, una ruta configurada que ya no existe, un script de lanzamiento desactualizado, o un desajuste entre skills y configuración), ahora se detiene y delega la reparación en `pv-update` en vez de intentar arreglarlo por sí misma, reanudando después solo si la configuración sigue incompleta.
- **Desglose de "en curso" reordenado y renombrado en `pv-status`** — el grupo "planificado, pendiente de implementar" ahora se lista antes que "pendiente de análisis técnico", reflejando el orden más natural del progreso.
- **`pv-status` ya no falla en un proyecto nuevo** — una carpeta de cambios inexistente ahora se trata igual que una vacía, de modo que un proyecto sin nada registrado todavía obtiene un informe normal de "sin entradas" en vez de fallar.
- **Datos internos de staging excluidos del recuento de estado** — `pv-status` ahora omite la carpeta interna usada mientras se prepara una versión, de modo que ya no afecta a los totales ni a los listados.
- **Informe de estado en terminal reestructurado en páginas** — la vista en terminal ahora se divide en páginas de resumen/detalle/avisos con ritmo pausado en vez de un volcado largo único, y termina con una petición interactiva para consultar el detalle de una entrada concreta.
- **La redacción del changelog ahora aísla las entradas en staging** — al redactar el changelog de versión, las entradas cerradas se mueven ahora a una copia aislada de staging antes de leerse y clasificarse, y solo se lee y se borra de esa copia en staging. Esto significa que las entradas cerradas mientras se prepara una versión ya no corren el riesgo de interferir con el borrador del changelog en curso, y borrar las entradas ya incorporadas tras la redacción ya no necesita confirmación aparte del usuario, porque solo afecta a la copia aislada.
- **Corregida una resolución incorrecta de carpetas para configuraciones de carpeta de trabajo personalizadas** — la lógica de numeración de cambios y movimiento de carpetas usada en todo el framework corrigió un error por el cual una barra inicial en una carpeta de trabajo personalizada podía hacer que se descartara silenciosamente el resto de la ruta configurada, apuntando a la carpeta equivocada. Los proyectos que usan una carpeta de trabajo distinta de la por defecto deberían actualizar para obtener una resolución de rutas correcta.
