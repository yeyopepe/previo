- **Creation date**: 2026-08-15
- **Risk**: [pending recalculation]

## (a) Functional notes

**Out of scope:** el flujo "Meter en mazo..." de una carta individual desde el menú contextual (modo juego, `ui/insertIntoMazoModal.js` + `playMode.js`) no se toca — siempre mueve una única carta, no varía en duración, y queda sin esta modal. Ningún otro comportamiento se toca.

**Doubts resolved with the user:** ninguna pregunta abierta durante la planificación — el alcance, el texto, la cancelación y la animación ya quedaron resueltos en `pv-new` (ver `description.md`).

## (b) Technical solution

- [x] **`src/ui/progressModal.js` (nuevo fichero) — módulo genérico de modal de operación en curso.** Exporta `runWithProgressModal(text, work)`:
  - Crea `overlay` (`div.modal-overlay`, mismo patrón que `ui/errorModal.js`) conteniendo `modal` (`div.progress-modal`, no `.modal` — estructura propia sin header/content/footer), con un `div.progress-modal__spinner` y un `p.progress-modal__text` con `text`.
  - Inserta el overlay en `document.body`.
  - Ejecuta `work()` dentro de `setTimeout(() => { ... }, 0)` (mismo mecanismo que ya usa el proyecto en `ui/toast.js`/`ui/componentRenderer.js`, primer uso con este propósito concreto: ceder un frame al navegador para que el spinner llegue a pintarse antes de que empiece el bloqueo síncrono de `work`).
  - Al terminar `work()` (bloque `try/finally`), elimina el overlay — sin listeners de cierre por click fuera ni por ESC: es la única modal de la app sin ninguna vía de cierre manual, a propósito (§12.1.2 de la Style Bible, ver (d)).
  - `work` es siempre síncrono en este primer uso; la función no necesita soportar promesas.
- [x] **`src/styles/main.css` — nuevas reglas para `.progress-modal`.** Añadir junto al resto de reglas de modal (cerca de `.modal-overlay`/`.modal`, línea ~347 actual):
  ```css
  .progress-modal {
    background: white;
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-2);
    width: 90%;
    max-width: 320px;
    padding: 1.75rem 1.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    text-align: center;
  }

  .progress-modal__spinner {
    width: 40px;
    height: 40px;
    border: 4px solid var(--accent-blue-light);
    border-top-color: var(--accent-blue);
    border-radius: 50%;
    animation: progress-modal-spin 0.8s linear infinite;
  }

  @keyframes progress-modal-spin {
    to { transform: rotate(360deg); }
  }

  .progress-modal__text {
    font-size: 0.95rem;
    color: var(--text-primary);
  }
  ```
  Primer `@keyframes` del proyecto — no hay ningún otro sitio que tocar para "registrar" la animación, `main.css` es un único fichero.
- [x] **`src/modes/edit/editMode.js` — usar la modal en `attemptDropOnMazo` (línea ~166).** Importar `runWithProgressModal` desde `'../../ui/progressModal.js'`. Dentro de la función, tras encontrar `mazo` (tras el `if (!mazo) return;` de la línea ~173) y antes de aplicar el cambio, envolver el cálculo de `cartaIds` + `replaceComponent` en:
  ```js
  const count = groupComponents.length;
  const text = `Añadiendo ${count} carta${count === 1 ? '' : 's'} al mazo…`;
  runWithProgressModal(text, () => {
    const cartaIds = [...(mazo.properties?.cartaIds || []), ...groupComponents.map((c) => c.id)];
    replaceComponent(mazo.id, updateComponent(mazo, { properties: { cartaIds } }));
  });
  ```
  La llamada existente a `attemptDropOnMazo(group, ...)` en el handler `onMove` (línea ~753) no cambia — sigue siendo síncrona desde el punto de vista de quien la llama, el diferimiento queda encapsulado dentro de `runWithProgressModal`.
- [x] **`design/docs/features/023-componente-mazo.md` (línea 33) — corregir mención de confirmación inexistente.** Sustituir "se pregunta si se quieren añadir todas las cartas seleccionadas a ese mazo (en cualquier orden). Si se confirma, todas pasan a formar parte del mazo; si se cancela, se quedan en la mesa como componentes independientes, en la posición donde se soltaron." por una redacción que refleje el comportamiento real (añade directamente, sin confirmación) y mencione la nueva modal de progreso mientras dura la operación. Incongruencia detectada durante el análisis técnico (paso 3 de `pv-how`): el código (`attemptDropOnMazo`, comentario explícito "sin confirmación previa") nunca preguntó nada, contradiciendo el texto actual de este documento.

Orden: primero el módulo genérico y su CSS (piezas independientes, sin dependencias entre sí), después su uso en `editMode.js`, por último la corrección de documentación funcional (no bloquea nada del código).

## (d) Style changes

- **`design/docs/style/03-modales-menus.md`** — añadir nueva subsección `12.1.2 Modal de operación en curso`, hermana de `12.1` (error) y `12.1.1` (éxito), documentando el patrón nuevo: `.progress-modal` (no `.modal` — sin header/content/footer, estructura propia con spinner + texto), `.progress-modal__spinner` (primer uso de animación CSS del proyecto, `@keyframes progress-modal-spin`), sin ningún botón ni vía de cierre manual (única modal de la app así), se cierra sola al terminar la operación asociada (`ui/progressModal.js`, `runWithProgressModal(text, work)`). Referenciar `023-componente-mazo.md` como primer y único uso (arrastrar cartas sobre un mazo en modo edición).

## (e) Verification

- [x] En modo edición, con al menos un mazo y una carta sueltos en la mesa, arrastrar 1 sola carta sobre el mazo: la modal aparece (aunque sea brevemente) con el texto "Añadiendo 1 carta al mazo…", el spinner gira, y se cierra sola; la carta queda dentro del mazo (deja de mostrarse como componente independiente) y ya no aparece en el panel de componentes fuera del mazo. Verificado por trazado de código: `count === 1` produce el singular exacto, `work()` inserta el id en `cartaIds` del mazo antes de que el overlay se elimine.
- [x] Repetir seleccionando 10 cartas a la vez y arrastrándolas juntas sobre el mazo: la modal muestra "Añadiendo 10 cartas al mazo…", se cierra sola al terminar, y las 10 cartas quedan dentro del mazo. Verificado por trazado de código: plural correcto, `groupComponents.map((c) => c.id)` añade las 10 en un único `replaceComponent`.
- [x] Mientras la modal está visible, no hay ningún botón ni forma de cerrarla a mano (ni click fuera, ni ESC). Verificado leyendo `ui/progressModal.js`: no añade ningún listener de cierre ni elemento de botón.
- [x] Arrastrar una selección de cartas fuera de cualquier mazo, o una selección mixta (cartas + otro tipo) sobre un mazo: no aparece la modal y el comportamiento es el mismo que antes de este cambio (sin inserción en el mazo). Verificado: `attemptDropOnMazo` retorna antes de llegar a `runWithProgressModal` en ambos casos (`!groupComponents.every(...)` y `!mazo`).
- [x] El spinner gira de forma continua y fluida mientras la modal está visible (comprobación visual de la animación CSS). Verificado en el HTML generado por el build (`index-v00210.html`): `@keyframes progress-modal-spin { to { transform: rotate(360deg); } }` aplicado con `animation: progress-modal-spin 0.8s linear infinite` — no se ha podido confirmar visualmente en navegador real por falta de herramientas de automación de navegador en este entorno (sin `chromium-cli` ni Playwright instalados); se recomienda una comprobación visual manual del usuario antes de dar el cambio por completamente cerrado.
