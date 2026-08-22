- **Creation date**: 2026-08-07
- **Risk**: [pending recalculation]

## (a) Functional notes

**Out of scope:** ningún otro comportamiento se toca. En particular:
- No se limpia el campo `imagenResourceId` cuando una cara cambia su fondo a color (`ui/componentModal.js`, `onAddColor` de `renderCartaSpecificFields`, y el equivalente de `visualEditorModal.js`, `onAddColor` de `openAdjustSession`'s caller): dejarlo así es intencional para este fix — la causa raíz real y suficiente para arreglar el síntoma reportado está en los puntos de lectura de "Ajustar imagen...", no en dejar de escribir el dato obsoleto. Limpiar el campo en origen sería un cambio de higiene de datos más amplio (afectaría también, por ejemplo, a la detección de "recurso en uso" de `core/resource.js`, que no ha sido reportada como rota) y queda fuera de este fix.
- `ui/cardShapeModal.js` (botón "Ajustar imagen…" de una `Forma` dentro del editor) no se toca: su bloque "Imagen" (con ese botón) solo es visible cuando el fondo de la figura ya está en modo imagen, así que el usuario no puede llegar a ver el botón con un `imagenResourceId` obsoleto de un fondo de color — no reproduce el síntoma reportado. Confirmado leyendo `refreshImagePreview`/`bgImageBlock`.

**Doubts resolved with the user:** el reporte inicial (bug 00192) no se pudo reproducir con la reproducción automatizada inicial (dos caras con imagen). El usuario aclaró la causa real: "si no uso ninguna imagen en una cara y solo uso un color de fondo (o texto/figuras), en Ajustar imagen... me muestra la última imagen que tuvo" — confirma que el campo `imagenResourceId` queda huérfano al cambiar el fondo de una cara a color, y que "Ajustar imagen..." lo sigue usando en vez de tratar esa cara como sin imagen.

## (b) Technical solution

Causa raíz: `ui/visualEditorModal.js` decide en el lienzo si una cara tiene imagen mirando **tanto** `cara.fondoTipo` como `cara.imagenResourceId` (`renderFace`, línea ~743: `if (cara.fondoTipo === 'color') { pinta color } else { pinta imagen si `imagenResourceId` existe }`), pero los tres puntos que alimentan el botón/modal "Ajustar imagen..." solo miran `imagenResourceId`, ignorando `fondoTipo` — así que si una cara tuvo imagen y luego pasó a fondo de color, `imagenResourceId` sigue apuntando al recurso antiguo (nunca se limpia) y esos tres puntos la siguen tratando como "cara con imagen".

El criterio correcto de "esta cara tiene imagen visible", igual que ya aplica `renderFace`, es `cara.fondoTipo !== 'color' && !!cara.imagenResourceId` (fondo ausente/`'imagen'` se comportan igual que hoy, ver comentario ya existente en el fichero sobre compatibilidad con caras guardadas sin este campo — solo `'color'` excluye la imagen).

1. **`src/ui/visualEditorModal.js` — `renderFaces`, cálculo de `adjustImageBtn.disabled` (línea ~482).** Cambiar:
   ```js
   adjustImageBtn.disabled = faces.every(({ key }) => !working[key].imagenResourceId);
   ```
   por:
   ```js
   adjustImageBtn.disabled = faces.every(({ key }) => working[key].fondoTipo === 'color' || !working[key].imagenResourceId);
   ```
2. **`src/ui/visualEditorModal.js` — `openAdjustSession`, cálculo de `initialFace` (línea ~500).** Cambiar:
   ```js
   const initialFace = faces.find(({ key }) => working[key].imagenResourceId);
   ```
   por:
   ```js
   const initialFace = faces.find(({ key }) => working[key].fondoTipo !== 'color' && working[key].imagenResourceId);
   ```
3. **`src/ui/visualEditorModal.js` — `openAdjustSession`, cálculo de `resource` por cada entrada de `faces.map(...)` (línea ~511).** Cambiar:
   ```js
   const resource = cara.imagenResourceId ? getResources().find((r) => r.id === cara.imagenResourceId) : null;
   ```
   por:
   ```js
   const resource = cara.fondoTipo !== 'color' && cara.imagenResourceId ? getResources().find((r) => r.id === cara.imagenResourceId) : null;
   ```

Con estos tres cambios, una cara con `fondoTipo === 'color'` se trata siempre como "sin imagen" en el botón/modal "Ajustar imagen...", tanto si `imagenResourceId` está a `null` como si conserva un valor obsoleto de una imagen anterior — igual que ya ocurre en el lienzo del propio editor.

Ordena las tareas en el orden en que se deberían implementar (son independientes entre sí, pero conviene aplicarlas juntas por estar en el mismo fichero/función).

## (e) Verification

1. Crear una carta, asignar una imagen a la cara trasera (sin cara frontal), y luego cambiar el fondo de esa misma cara trasera a "Color de fondo…" (sin volver a elegir imagen). Al abrir "Editar diseño de la carta", el botón "Ajustar imagen…" debe aparecer **deshabilitado** si ninguna otra cara tiene imagen (antes del fix, quedaba habilitado y abría la imagen antigua).
2. Repetir el caso anterior pero con la cara frontal también con una imagen propia: "Ajustar imagen…" debe seguir habilitado, abrir enfocado en la cara frontal (la única con imagen real) y la cara trasera (con fondo de color) debe aparecer sin ninguna imagen en su recuadro del modal.
3. Reproducir el flujo original del bug (copiar estilo de "Cara trasera" de una carta cuya cara trasera tiene fondo de color con un `imagenResourceId` obsoleto, pegar en otra carta con imagen en la cara trasera, abrir el editor y pulsar "Ajustar imagen…"): la cara trasera del modal debe aparecer sin imagen, no con la imagen antigua de la carta destino.
4. Una cara con `fondoTipo` ausente o `'imagen'` y una imagen válida sigue funcionando exactamente igual que antes del fix (sin regresión): "Ajustar imagen…" la muestra y permite ajustarla con normalidad.
5. `ui/cardShapeModal.js` (Ajustar imagen de una figura) sigue funcionando igual que antes — no debería verse afectado por este cambio (fichero no tocado).
