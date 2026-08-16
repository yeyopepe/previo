---
name: pv-version
description: Prepara una entrega/versión del proyecto en {workFolder}/versions/{XXXX}/ — genera el entregable, copia la documentación técnica vigente y encadena pv-internal-changelog para el changelog funcional. Parte del framework pv-*. Trigger: /pv-version <XXXX>, o cuando el usuario pide preparar/empaquetar una versión entregable.
argument-hint: <XXXX de la versión a preparar>
model: claude-sonnet-5
effort: medium
metadata:
  version: 0.9.1
  uses: [pv-internal-changelog]
---

# pv-version

Orquesta la preparación de una entrega del proyecto: resuelve los change/fix pendientes de cerrar, genera el entregable, copia la documentación técnica vigente, y encadena `pv-internal-changelog` para redactar el changelog funcional a partir de `{workFolder}/changes/closed/`.

`{workFolder}` es el valor de `framework.workFolder` en `.claude/pv-context.json` (por defecto `"/"`, la raíz del repo). Dentro de él, `changes/` y `versions/` son subcarpetas de nombre fijo que el framework crea por sí mismo — no se preguntan ni se configuran por separado. `{workFolder}/versions/{XXXX}/` es un espacio de numeración de texto libre, elegido por el usuario en cada invocación, sin ninguna relación con el `xxxx` de change/fix ni con ninguna otra carpeta llamada "versions" que pueda existir en el repo (p.ej. la salida propia de un build script): esta skill nunca lee ni escribe fuera de `{workFolder}/versions/`.

## 0. Framework inicializado

Lee `.claude/pv-context.json` en la raíz del repo. Si no existe, o le falta la sección `framework`, no continúes: dile al usuario que primero debe ejecutar la skill `pv-init` para inicializar/completar el framework en este proyecto, y detente ahí.

```
Este proyecto todavía no tiene el framework `pv-*` inicializado (o le falta configuración). Ejecuta primero `/pv-init` antes de volver a invocarme.
```

## 0.1. Diagrama del proceso, bajo demanda

En cualquier momento de la invocación, si el usuario pregunta cómo funciona el proceso o pide explícitamente "el diagrama"/"el flujo", muestra el contenido íntegro de [`version-flow-diagram.template.md`](version-flow-diagram.template.md) tal cual (sin regenerarlo ni parafrasearlo) y continúa donde se había quedado el flujo.

## 0.2. Invocación puramente informativa sobre el proceso de build

Es posible que el usuario invoque esta skill únicamente para informar de un cambio en el procedimiento de compilación/generación del entregable (p.ej. "ahora el build también genera un PDF de reglas", "cambia el comando de compilación a..."), sin pedir explícitamente preparar una entrega ahora mismo.

Si esa es la intención: actualiza `{workFolder}/framework/how-to-compile-version.md` con la información nueva, siguiendo [`how-to-compile-version.template.md`](how-to-compile-version.template.md) (incluido su soporte para procesos de varios pasos/artefactos si aplica — ver el propio template), y **no continúes con el resto del flujo**. Pregunta explícitamente al usuario si quiere lanzar el proceso de versionado ahora con este procedimiento ya actualizado. Solo si confirma específicamente, continúa con el paso 0.5; si no confirma (o no contesta a eso), detente aquí.

## 0.5. Guardarraíl: `implemented/` debe estar vacío antes de empezar

Al arrancar el proceso de versionado no puede haber ningún change/fix en estado `implemented`. Lista las carpetas de `{workFolder}/changes/implemented/`; si hay alguna, **no se puede avanzar de ninguna manera** (ni crear la carpeta de versión, ni nada de lo que sigue) hasta resolverlas todas.

Por cada carpeta encontrada, pregunta explícitamente al usuario si ese change/fix pasa a `closed`:

- Si confirma, ejecuta (desde la raíz del repo):

  ```
  python .claude/skills/pv-internal-workflow/scripts/move-change.py --xxxx <xxxx> --from implemented --to closed
  ```

- Si no confirma, **espera la confirmación del usuario** sin continuar el flujo — no se salta ni se ignora la entrada, no hay "seguir de todas formas".

Repite hasta que `implemented/` quede vacío; solo entonces continúa con el paso 1.

## 1. Resolver `XXXX`

Si no se indica al invocar, pregúntalo explícitamente — no lo asumas. Es texto libre elegido por el usuario, no se calcula ni se valida contra `numberWidth` (espacio de numeración independiente del de change/fix).

## 2. Crear la carpeta de la versión

Ejecuta desde la raíz del repo:

```
python .claude/skills/pv-version/scripts/init-version-folder.py --xxxx <XXXX>
```

Crea `{workFolder}/versions/{XXXX}/` con subcarpetas vacías `files/` y `docs/`, e imprime la ruta creada. Si `{workFolder}/versions/{XXXX}/` ya existe, el script termina en error sin tocar nada — en ese caso, pregunta al usuario si quiere continuar sobre lo ya existente (regenerar) o elegir otro `XXXX`, y vuelve a este paso con el nuevo valor si aplica.

## 3. Comprobar `how-to-compile-version.md`

Busca `{workFolder}/framework/how-to-compile-version.md` (fichero propio del proyecto, no de la skill ni de `pv-context.json`: es un procedimiento de shell/build, no configuración declarativa).

- **Si no existe**: pregunta al usuario el procedimiento exacto para generar el entregable de este proyecto (qué comando(s) ejecutar, dónde queda el fichero resultante y cómo identificarlo — o, si el proceso consta de varios pasos que generan artefactos distintos, cada paso con su propio comando y fichero resultante), y escríbelo siguiendo [`how-to-compile-version.template.md`](how-to-compile-version.template.md). No continúes con el paso 4 en la misma respuesta sin haber guardado el fichero.
- **Si ya existe**: léelo y síguelo tal cual, sin volver a preguntar.

## 4. Generar la versión

Ejecuta el/los comando(s) que indique `how-to-compile-version.md` (uno por cada paso, si el procedimiento consta de varios) y localiza el/los fichero(s) resultantes tal como describe. Si algún comando falla o el fichero esperado no aparece, para y explícaselo al usuario en vez de improvisar una solución alternativa.

Con todos los artefactos localizados, cópialos a `{workFolder}/versions/{XXXX}/files/` ejecutando desde la raíz del repo (un `--source` por artefacto, aunque provenga de un único paso):

```
python .claude/skills/pv-version/scripts/copy-build-artifacts.py --xxxx <XXXX> --source <ruta-artefacto-1> [--source <ruta-artefacto-2> ...]
```

## 5. Copiar documentación técnica y funcional

Solo si el paso 4 generó el entregable correctamente. Ejecuta desde la raíz del repo:

```
python .claude/skills/pv-version/scripts/copy-docs.py --xxxx <XXXX>
```

Lee `framework.docs.tech.architectureDocDir`, `framework.docs.tech.styleBibleDocDir` y `framework.docs.functional.featuresDocPathDir` de `.claude/pv-context.json` (los que estén configurados; si ninguno lo está, se omite sin preguntar, igual que hace `pv-do`), comprime cada uno en un `.zip` (carpeta completa con todos sus ficheros, incluido su `INDEX.md`; o el único fichero `.md`, si esa ruta no es una carpeta) y lo guarda en `{workFolder}/versions/{XXXX}/docs/`. Anota qué se copió y qué se omitió (lo devuelve el script en su JSON de salida) para el resumen del paso 7.

## 6. Generar el changelog

Invoca la skill `pv-internal-changelog` (herramienta Skill) pasándole la carpeta destino `{workFolder}/versions/{XXXX}/`.

## 7. Confirmar al usuario

Resume lo generado: entregable en `files/`, docs comprimidos en `docs/` (o cuáles se omitieron por no estar configurados), y que el changelog quedó en `changelog.md` — usa el resumen que te devuelva `pv-internal-changelog` (número de entradas por sección, incluida Fixes, y si se borraron o no las carpetas de `{workFolder}/changes/closed/`).
