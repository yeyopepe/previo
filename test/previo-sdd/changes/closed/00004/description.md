- **Name**: Ordenar el listado de clientes por fecha de alta
- **Code**: 00004
- **Type**: change
- **Creation date**: 2026-07-20

## Full description

El listado de clientes ahora se ordena por defecto por fecha de alta descendente (los más recientes primero), en vez de por nombre alfabético. El usuario puede seguir cambiando el criterio de orden pulsando en las cabeceras de columna, como ya podía hacer antes.

## Technical notes

Cambio del `defaultSort` en `customerListQuery`, sin tocar el resto de la lógica de ordenación por columnas.
