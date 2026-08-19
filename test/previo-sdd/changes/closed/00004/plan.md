- **Creation date**: 2026-07-21
- **Risk**: 1 — Minimal risk — local change, with a safety net (tests) or easily reversible

## (a) Functional notes

**Out of scope:** No se cambia la posibilidad de reordenar por columna, que sigue disponible igual que antes.

**Doubts resolved with the user:** no open questions — el orden por defecto pedido quedó claro desde el principio.

## (b) Technical solution

- [x] **`src/customers/services/customerListQuery.ts` — cambiar `defaultSort`.** Cambiar `{ field: 'name', direction: 'asc' }` por `{ field: 'createdAt', direction: 'desc' }`.

## (e) Verification

- [x] Abrir el listado de clientes sin tocar ninguna cabecera: el primero de la lista es el cliente dado de alta más recientemente.
- [x] Pulsar la cabecera "Nombre" y comprobar que el reordenado manual por columna sigue funcionando.
