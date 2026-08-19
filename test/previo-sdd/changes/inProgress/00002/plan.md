- **Creation date**: 2026-08-14
- **Risk**: 2 — Minimal risk — local change, with a safety net (tests) or easily reversible

## (a) Functional notes

**Out of scope:** No se toca el filtro de fecha "desde", que ya funciona correctamente incluyendo desde las 00:00:00 del día indicado.

**Doubts resolved with the user:** no open questions — el comportamiento esperado quedó claro en la petición original.

## (b) Technical solution

- [ ] **`src/orders/filters/dateRangeFilter.ts` — normalizar el límite "hasta" al final del día.** En `buildDateRangeFilter`, cambiar `toDate.setHours(0,0,0,0)` por `toDate.setHours(23,59,59,999)` antes de comparar.

## (e) Verification

- [ ] Crear un pedido hoy a última hora y filtrar pedidos "hasta hoy": el pedido debe aparecer en los resultados.
- [ ] El filtro "desde" sigue funcionando igual que antes (regresión).
