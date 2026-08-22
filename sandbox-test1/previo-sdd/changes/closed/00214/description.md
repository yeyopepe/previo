- **Name**: Modal de operación en curso al meter cartas en un mazo
- **Code**: 00214
- **Type**: change
- **Creation date**: 2026-08-15

## Full description

Hay operaciones del juego que tardan un tiempo perceptible en ejecutarse y dejan al jugador sin poder hacer nada hasta que terminan, sin ningún tipo de aviso mientras tanto. Se introduce un sistema genérico de "operación en curso": una modal breve que informa de que se está ejecutando una operación potencialmente lenta y devuelve el control automáticamente al jugador en cuanto termina.

- Mientras dura la operación asociada se muestra una modal pequeña, centrada, con el mismo aspecto que el resto de modales de la aplicación: un texto descriptivo breve (p. ej. "Añadiendo 10 cartas al mazo…") junto a una animación de espera (spinner circular giratorio).
- La modal no tiene ningún botón — ni "Cancelar" ni "Cerrar". Es puramente informativa: aparece al empezar la operación y desaparece sola en cuanto termina, sin que el jugador pueda intervenir mientras tanto ni cerrarla a medias.
- No hay tiempo mínimo de visualización artificial: si la operación es casi instantánea (p. ej. con muy pocas cartas), la modal puede llegar a no percibirse — se acepta como comportamiento normal, priorizando que el tiempo mostrado sea siempre el real.
- Es un mecanismo genérico y reutilizable, pensado para aplicarse a cualquier operación lenta del juego, no solo a la de este cambio.

**Primer caso de uso: arrastrar varias cartas seleccionadas sobre un mazo (modo edición).** Al soltar una selección múltiple de cartas sobre un mazo, la aplicación las añade todas a él de golpe; la duración de esta operación depende del número de cartas que se estén insertando a la vez, así que es el caso que se beneficia de este aviso. Se debe poder comprobar que la modal se muestra y se cierra correctamente tanto insertando 1 carta como 10.

Queda fuera de este cambio la acción "Meter en mazo..." del menú contextual de una carta individual (modo juego): siempre mueve una única carta, su duración no varía, y no se le aplica esta modal.

### Casos límite
- Operación completada sin incidencias: la modal se cierra sola, el jugador recupera el control con el mazo ya actualizado.
- No se contempla cancelación ni error a medias: hoy la inserción de cartas en un mazo no falla ni tiene puntos intermedios desde los que abortar.
- Con una sola carta, la modal puede no llegar a percibirse por lo breve de la operación — comportamiento aceptado explícitamente, sin forzar un tiempo mínimo.

### Convivencia con lo existente
Sistema nuevo: no existía ningún mecanismo de aviso de progreso o carga en la aplicación. No sustituye ni modifica ningún modal existente (informativo, de error o de éxito) — se suma como una variante más para este tipo de situación.

### Alcance de los datos
Estado puramente transitorio de la interfaz (si hay una operación en curso o no). No se guarda, no se exporta, y no persiste entre sesiones ni recargas.

### Quién puede usarlo
Disponible en modo edición, que es donde existe hoy la operación de arrastrar varias cartas seleccionadas sobre un mazo.

## Technical notes

- Todo el código del proyecto es hoy síncrono (sin `async`/`await`, sin workers). El "tiempo que tarda" la operación no es progreso real reportado por el propio proceso, sino bloqueo del hilo principal por: recalcular estado (`replaceComponent`), re-renderizar toda la mesa (`renderComponentsOnTable`, coste proporcional al nº total de componentes) y autoguardado síncrono (`core/persistence.js`, `localStorage.setItem(JSON.stringify(...))` de todo el estado, incluidas imágenes en base64). Para que el spinner llegue a pintarse y animarse antes de que empiece el bloqueo, hace falta ceder al menos un frame al navegador (p. ej. `requestAnimationFrame` o `setTimeout(0)`) entre mostrar la modal y ejecutar el trabajo pesado de inserción/render/autoguardado.
- Punto de inserción del nuevo sistema: en torno a la llamada a `attemptDropOnMazo(group, ...)` en `src/modes/edit/editMode.js` (línea ~753), o dentro de la propia función `attemptDropOnMazo`.
- No existe hoy ningún componente de modal genérico "sin botones" en `src/ui/` — los modales existentes (`ui/errorModal.js`, patrón de modal de éxito §12.1.1 de la Style Bible, etc.) siempre tienen al menos un botón de cierre/acción; este es el primer caso sin ningún control interactivo.
- No existe hoy ninguna animación CSS (`@keyframes`) en el proyecto — el spinner sería el primer uso de este patrón.
- Incongruencia doc/código detectada durante el análisis (ajena a este cambio, pero a corregir de paso si se toca esta zona): `design/docs/features/023-componente-mazo.md` (línea 33) dice que arrastrar cartas seleccionadas sobre un mazo "se pregunta si se quieren añadir" (confirmación previa), pero el código real (`src/modes/edit/editMode.js`, función `attemptDropOnMazo`, comentario explícito "mismo criterio que en modo juego: sin confirmación previa") no pregunta nada — añade directamente. El código manda; conviene actualizar esa frase de la documentación funcional.
