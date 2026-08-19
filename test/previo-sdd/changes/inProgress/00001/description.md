- **Name**: Exportar listado de clientes a CSV
- **Code**: 00001
- **Type**: change
- **Creation date**: 2026-08-10

## Full description

Se añade un botón "Exportar CSV" en la pantalla de listado de clientes. Al pulsarlo, se descarga un fichero `.csv` con todos los clientes visibles según los filtros aplicados en ese momento (no solo la página actual). El fichero incluye nombre, email, teléfono y fecha de alta, en ese orden, con cabecera.

Si el listado filtrado no tiene resultados, el botón se muestra deshabilitado.

## Technical notes

Reutilizar el mismo servicio de filtrado que ya usa el listado paginado, en vez de duplicar la lógica de consulta.
