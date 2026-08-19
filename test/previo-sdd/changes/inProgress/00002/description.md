- **Name**: El filtro de fecha no incluye el día final
- **Code**: 00002
- **Type**: fix
- **Creation date**: 2026-08-14

## Full description

Al filtrar el listado de pedidos por rango de fechas, el pedido creado justo el día indicado como "hasta" no aparece en los resultados. Por ejemplo, filtrando "hasta el 2026-08-14", un pedido creado ese mismo día a las 18:00 queda fuera. El usuario espera que el filtro incluya cualquier momento dentro del día final, no solo hasta las 00:00.

## Technical notes

La comparación de fecha "hasta" se hace contra `00:00:00` del día indicado en vez de `23:59:59`.
