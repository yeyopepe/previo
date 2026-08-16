---
name: pv-internal-tech-security
description: Procedimiento compartido, agnóstico al proyecto, para contrastar un change/fix contra una checklist de categorías de seguridad (autenticación, autorización, validación de entradas/inyección, secretos, transporte, datos sensibles, dependencias, infraestructura, API, logging, hardening de cliente). Recibe un resumen de qué se está analizando y el contexto ya reunido, y devuelve solo las categorías aplicables — separadas entre ya cubiertas por el contexto y pendientes de revisar — sin decidir el diseño ni editar nada. Uso interno de pv-internal-tech-analysis (al terminar su propio análisis) y pv-how (al valorar el riesgo junto a pv-internal-tech-risks).
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.1.0
  uses: []
---

# pv-internal-tech-security

Procedimiento único y compartido para contrastar un change/fix contra una checklist de categorías de seguridad y señalar cuáles son relevantes y no están ya resueltas por el contexto disponible. Solo lo invocan otras skills del framework `pv-*` — no está pensado para invocación directa por el usuario.

**Esta skill no escribe ni edita nada, ni diseña la solución de seguridad.** Se limita a decir qué categorías de la checklist aplican al cambio y, de esas, cuáles quedan como punto pendiente de revisar por no estar ya cubiertas por el contexto recibido. Qué hacer con esos pendientes (resolverlos ahora, anotarlos en `plan.md`, preguntar al usuario, usarlos como motivo para no calificar de trivial) lo decide siempre quien invoca.

## Entrada esperada de quien invoca

- Un resumen breve de **qué se está analizando/cambiando** (el change/fix concreto, no la conversación entera).
- El **contexto ya reunido** hasta el momento (p.ej. lo que ya haya salido de los pasos 1-2 de `pv-internal-tech-analysis`, o la solución técnica de `plan.md`) — para no repetir exploración ya hecha y para poder marcar una categoría como resuelta si el contexto ya la cubre.

## 0. Cargar el contexto del proyecto

Lee `.claude/pv-context.json` en la raíz del repo (si no lo has hecho ya en esta sesión). No valides aquí que el framework está inicializado — eso ya lo ha comprobado la skill llamante antes de invocar esta.

## 1. La checklist de categorías

Para cada categoría, valora dos cosas: (a) si es **aplicable** al cambio concreto (no todo cambio toca todas las categorías — la mayoría de cambios solo tocan una o dos) y (b) si, siendo aplicable, el contexto recibido ya deja claro cómo se resuelve o si queda **pendiente de revisar**.

| Categoría | Qué comprobar |
|---|---|
| Autenticación | ¿Se toca login, sesión, tokens, cookies de sesión, recuperación de contraseña, MFA? |
| Autorización | ¿Se toca control de acceso, roles, propiedad de recursos (riesgo de IDOR), endpoints o funciones administrativas? |
| Validación de entradas / inyección | ¿Hay entrada de usuario que llegue a una query (SQL/NoSQL), un comando de sistema, un parser (XML/YAML), un motor de plantillas, una ruta de fichero, una deserialización, o una URL solicitada por el propio servidor (SSRF)? |
| Secretos y configuración | ¿Se añaden o mueven credenciales, API keys, tokens? ¿Cambia cómo se cargan, guardan o rotan? |
| Comunicación y transporte | ¿Se añade o cambia una llamada de red, interna o externa? ¿Queda cifrada (TLS) y con verificación de certificado? |
| Datos sensibles | ¿El cambio maneja PII, credenciales, datos de pago o salud? ¿Se cifran en reposo, se enmascaran o excluyen de logs? |
| Dependencias | ¿Se añade una librería, paquete o servicio de terceros nuevo? |
| Infraestructura y despliegue | ¿Se tocan permisos (IAM, roles de servicio), superficie expuesta (puertos, endpoints públicos), configuración de despliegue o contenedores? |
| API | ¿Se añade o modifica un endpoint? ¿Necesita autenticación, control de CORS, validación de esquema, o queda expuesto sin protección? |
| Logging y monitorización | ¿Se añaden logs que puedan capturar datos sensibles (secretos, PII)? ¿El cambio afecta a un evento que debería quedar registrado por motivos de seguridad (login fallido, cambio de permisos, acceso admin)? |
| Hardening de cliente | ¿Se renderiza HTML o contenido de usuario sin el escapado/sanitizado habitual del framework? ¿Se añade una operación que cambia estado y necesita protección CSRF? ¿Se cargan scripts de terceros? |

## 2. Contrastar contra el contexto recibido

Para cada categoría marcada como aplicable en el paso 1:

- Si el contexto ya reunido (documentación técnica, código explorado, `plan.md`) deja claro cómo se aborda esa categoría — p.ej. ya pasa por el ORM parametrizado del proyecto, ya usa el middleware de auth existente, ya sigue un patrón de sanitizado ya establecido — no la marques como pendiente: indícala como **cubierta**, en una frase, citando el patrón concreto que la resuelve.
- Si el contexto no lo deja claro, o el cambio introduce algo nuevo en esa categoría sin patrón existente que seguir, márcala como **pendiente de revisar**, con una frase de qué falta confirmar o decidir.
- No explores código de más solo para resolver esto: si hace falta más información de la que ya se tiene para decidir con confianza, es señal de que la categoría queda pendiente — no motivo para lanzar una exploración adicional del repo por cuenta propia.

## 3. Devolver el resultado a quien invoca

No redactes ningún fichero ni muestres nada al usuario directamente. Devuelve a quien invoca, en el mismo turno:

- **Categorías aplicables cubiertas**: lista (puede estar vacía) de `{categoría}: {por qué ya está resuelta}`.
- **Categorías pendientes de revisar**: lista (vacía si no hay ninguna) de `{categoría}: {qué falta confirmar o decidir}`.
- Las categorías no aplicables al cambio ni se mencionan en el resultado.

Quien invoca decide qué hacer con los pendientes (resolverlos con el usuario, anotarlos en `plan.md`, usarlos como motivo para no calificar de trivial en el atajo `fast` de `pv-fix`); esta skill no vuelve a intervenir sobre eso.
