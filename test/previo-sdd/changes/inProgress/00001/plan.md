- **Creation date**: 2026-08-11
- **Risk**: 3 — Low risk — touches some shared surface or several spots, but doesn't touch contracts or data

## (a) Functional notes

**Out of scope:** No se añade selección de columnas ni otros formatos de exportación (Excel, PDF); solo CSV con las cuatro columnas descritas.

**Doubts resolved with the user:** ¿Exportar solo la página actual o todo el filtrado? → Todo el filtrado, sin paginar.

## (b) Technical solution

- [ ] **`src/customers/list/CustomerListPage.tsx` — añadir botón "Exportar CSV".** Botón junto a la barra de filtros, deshabilitado cuando `results.length === 0`. Al click, llama a `exportCustomersCsv(currentFilters)`.
- [ ] **`src/customers/services/customerExport.ts` — nuevo servicio `exportCustomersCsv`.** Reutiliza `customerFilterService.query(filters)` (sin paginar) para obtener todos los resultados, genera CSV con cabecera `Nombre,Email,Telefono,FechaAlta` y dispara la descarga en el navegador.

## (e) Verification

- [ ] Con clientes filtrados por ciudad, exportar y comprobar que el CSV descargado contiene solo esos clientes, en el orden de columnas indicado.
- [ ] Con un filtro sin resultados, comprobar que el botón aparece deshabilitado.
