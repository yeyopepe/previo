---
name: pv-internal-tech-risks
description: Procedimiento compartido, agnóstico al proyecto, para valorar el riesgo de romper algo al implementar la solución técnica ya escrita en plan.md de un change/fix. Evalúa 9 factores (uso compartido, alcance, profundidad, cobertura de tests, criticidad, reversibilidad, datos persistentes, superficie de seguridad, datos sensibles) puntuados 0-10, y devuelve la lista factor=valor más la mediana. Uso interno de la skill pv-how, invocada solo cuando plan.md ya está escrito.
user-invocable: false
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.0
  uses: []
---

# pv-internal-tech-risks

Procedimiento único y compartido para valorar el riesgo de romper algo al implementar una solución técnica ya diseñada. Solo lo invoca `pv-how`, y solo después de que `plan.md` esté escrito — con la solución ya decidida es cuando hay información suficiente para valorar el riesgo, no antes. No está pensado para invocación directa por el usuario.

**Esta skill no escribe ni edita nada.** Es puramente de análisis: evalúa y devuelve el resultado a quien invoca. Qué hacer con ese resultado (qué se escribe en `plan.md`, cuánto detalle se muestra al usuario) lo decide siempre `pv-how`.

## Entrada esperada de quien invoca

- La ruta (o el contenido ya leído) de `plan.md` de la entrada, con la solución técnica ya escrita.
- La ruta (o el contenido ya leído) de `description.md` de esa misma entrada, como contexto funcional.

## 0. Cargar el contexto del proyecto

Lee `.claude/pv-context.json` en la raíz del repo (si no lo has hecho ya en esta sesión). No valides aquí que el framework está inicializado — eso ya lo ha comprobado `pv-how` antes de invocar esta skill.

## 1. Los 9 factores de riesgo

Evalúa cada uno de estos 9 factores con un valor entero de 0 a 10, usando el ancla en 0, el ancla en 10, y la tabla de significado general de la sección siguiente para interpolar los valores intermedios.

| # | Factor | Pregunta guía | Ancla 0 | Ancla 10 |
|---|--------|---------------|---------|----------|
| 1 | Uso compartido | ¿Quién más usa el código que se toca? | Código nuevo o exclusivo de este cambio, nadie más lo usa | Función/módulo core consumido por muchas features distintas |
| 2 | Alcance | ¿Cuántos puntos distintos se tocan? | 1 solo fichero, 1 función | Muchos ficheros dispersos en capas distintas (UI, lógica, datos...) |
| 3 | Profundidad del cambio | ¿Se cambia comportamiento interno o un contrato? | Detalle interno no observable desde fuera | Cambio de firma/interfaz/esquema del que otros dependen directamente |
| 4 | Cobertura de tests | ¿Hay red de seguridad automática? | Código bien cubierto por tests que fallarían si algo se rompe | Sin ningún test que ejercite este código |
| 5 | Criticidad del flujo | ¿Qué tan grave es si esto falla? | Funcionalidad secundaria o cosmética | Flujo crítico de negocio (auth, pagos, datos core) |
| 6 | Reversibilidad | ¿Qué cuesta deshacerlo si sale mal? | Revertir el commit basta, sin rastro | Requiere deshacer una migración de datos/estado en producción |
| 7 | Datos persistentes | ¿Se toca cómo se guardan los datos? | No se toca esquema ni formato de datos guardados | Migración de esquema/datos en producción |
| 8 | Superficie de seguridad | ¿Se toca entrada de usuario o control de acceso? | No hay entrada de usuario ni control de acceso implicado | Cambio en autenticación, autorización o validación de entrada |
| 9 | Datos sensibles | ¿Se maneja algo que no debería filtrarse? | No hay credenciales, PII, tokens ni secretos implicados | El cambio maneja o puede exponer credenciales, PII, tokens o secretos |

## 2. Tabla de significado del valor de riesgo (referencia para interpolar y para presentar el resultado)

| Valor | Significado |
|---|---|
| 0 | Sin riesgo — cambio totalmente aislado, imposible que afecte a nada más |
| 1–2 | Riesgo mínimo — cambio local, con red de seguridad (tests) o fácilmente reversible |
| 3–4 | Riesgo bajo — toca algo de superficie compartida o varios puntos, pero sin tocar contratos ni datos |
| 5–6 | Riesgo moderado — comparte código con otras partes, cobertura de test parcial, o toca un contrato/firma usado por otros |
| 7–8 | Riesgo alto — cambio profundo en código muy compartido y/o sin tests, en un flujo relevante, datos persistentes o seguridad |
| 9 | Riesgo muy alto — cambio estructural en flujo crítico de negocio, difícil de revertir, sin tests |
| 10 | Riesgo extremo — cambio profundo y amplio en código crítico y muy compartido, sin tests, sin reversibilidad fácil, tocando datos y/o seguridad a la vez |

## 3. Reunir la información necesaria

1. Lee `plan.md` (en concreto la sección (b) Solución técnica, y (c)/(d) si existen) y `description.md` de la entrada.
2. Con eso, valora cuántos de los 9 factores ya se pueden puntuar con confianza. Para los que no (p.ej. si hay tests que cubran un fichero concreto, o si una función la usan otras partes del proyecto), explora puntualmente el código real usando `framework.sourcecodeDir` (si está configurado, o el repo en general si no) — solo lo necesario para confirmar ese factor concreto, sin explorar el repo entero sin rumbo.

## 4. Puntuar y calcular la mediana

1. Asigna un valor entero 0-10 a cada uno de los 9 factores.
2. Calcula la mediana de los 9 valores (el valor central al ordenarlos) — con 9 valores siempre es un entero, sin redondeos necesarios.

## 5. Devolver el resultado a quien invoca

No redactes ningún fichero ni muestres nada al usuario directamente. Devuelve a `pv-how`, en el mismo turno:

- **Lista de factores**: cada uno de los 9 como `{factor} = {valor}`, en el mismo orden de la tabla del paso 1.
- **Mediana final**: el valor entero calculado en el paso 4.

Quien invoca decide qué hacer con este resultado (qué escribe en `plan.md`, qué muestra al usuario); esta skill no vuelve a intervenir sobre eso.
