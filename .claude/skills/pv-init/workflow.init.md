```mermaid
flowchart TD
    Start([Invocación de pv-init])

    Start --> S0Base[Comprobar tooling base: git, python]
    S0Base --> S0Cond{Falta alguna herramienta?}
    S0Cond -->|No| S1Run
    S0Cond -->|Sí| S0Ask[ASK: cómo instalar la que falta]
    S0Ask --> S0Dec{Usuario quiere instalar ahora?}
    S0Dec -->|Sí, la instala| S0Verify[Reinstalar y reverificar la herramienta]
    S0Verify --> S1Run
    S0Dec -->|No quiere o no puede| S0Proceed[ASK: continuar sin ella o parar aquí?]
    S0Proceed --> S0ProceedDec{Continuar?}
    S0ProceedDec -->|Sí| S1Run
    S0ProceedDec -->|No| End0([Fin: init detenido]) 

    S1Run[Ejecutar check-context.py] --> S1Exists{.claude/pv-context.json existe?}
    S1Exists -->|No| S2Explore
    S1Exists -->|Sí, pero JSON inválido o check-context.py falla| S1Broken[Invocar pv-update]
    S1Broken --> S1Resume{pv-update deja algo pendiente para pv-init?}
    S1Resume -->|No| End1([Fin: resuelto por pv-update])
    S1Resume -->|Sí| S2Explore

    S1Exists -->|Sí, JSON válido, framework no existe| S2Explore
    S1Exists -->|Sí, JSON válido, framework completo| S1Complete{hasLanguage y sin opcionales pendientes?}
    S1Complete -->|Sí, todo completo| S1AskReset[ASK: reinicializar desde cero?]
    S1AskReset --> S1ResetDec{Usuario confirma reset?}
    S1ResetDec -->|Sí| S1Erase[Borrar framework actual]
    S1Erase --> S2Explore
    S1ResetDec -->|No| S5Scaffold

    S1Complete -->|Falta idioma y/o algún opcional| S1AskComplete[ASK: completar los campos pendientes o dejarlo así?]
    S1AskComplete --> S1CompleteDec{Usuario quiere completar?}
    S1CompleteDec -->|Sí| S3Ask
    S1CompleteDec -->|No| S5Scaffold

    S2Explore[Explorar el repo en busca de pistas: arquitectura, features, estilo, código fuente] --> S3Ask

    S3Ask[Recorrer los campos de framework en schema.json] --> S3Lang[ASK: idioma de interacción y si se reparte por área]
    S3Lang --> S3Docs[Confirmar/migrar architectureDocDir, styleBibleDocDir, featuresDocPathDir]
    S3Docs --> S3Src[ASK: confirmar sourcecodeDir propuesto]
    S3Src --> S3SrcCheck[Comprobar si esa carpeta existe y tiene contenido]
    S3SrcCheck --> S3SrcDec{Carpeta vacía o inexistente?}
    S3SrcDec -->|Sí| S3Num
    S3SrcDec -->|No, ya hay código| S3SrcAsk[ASK: elegir nivel de documentación a generar al terminar -- mínimo o completa]
    S3SrcAsk --> S3SrcMode[Guardar el modo elegido en memoria de la conversación]
    S3SrcMode --> S3Num

    S3Num[numberWidth: silencioso salvo que el usuario quiera otro valor] --> S3Skills[skills.mockups/diagrams: escribir defaults en silencio]
    S3Skills --> S3Models[Calcular skillModels con collect-skill-models.py y confirmar con el usuario]
    S3Models --> S4Write

    S4Write[Escribir/fusionar .claude/pv-context.json] --> S5Scaffold

    S5Scaffold[Ejecutar scaffold-project.py] --> S5NewDoc{Se generó algún placeholder nuevo de docs.tech?}
    S5NewDoc -->|Sí| S5Info[INFO: se generó el placeholder de architectureDocDir/styleBibleDocDir]
    S5Info --> S5Ask[ASK: qué quieres aportar al 01-overview.md?]
    S5Ask --> S5Edit[Editar 01-overview.md con la respuesta]
    S5Edit --> S55Check
    S5NewDoc -->|No| S55Check

    S55Check{En el paso 3 se detectó código existente y se eligió un modo?}
    S55Check -->|No| S6Verify
    S55Check -->|Sí| S55Analysis[Invocar pv-internal-tech-analysis sobre sourcecodeDir]
    S55Analysis --> S55Style[Invocar pv-internal-doc-technical para cargar el estilo de redacción]
    S55Style --> S55Arch[Redactar architectureDocDir según el modo elegido]
    S55Arch --> S55Bible[Redactar styleBibleDocDir según el modo elegido]
    S55Bible --> S55Features[Por cada feature detectada: pv-internal-doc-features find + upsert]
    S55Features --> S55Info[INFO: ficheros de documentación generados]
    S55Info --> S6Verify

    S6Verify[Reverificar con check-context.py] --> S6Scaffold[Comprobar salida de scaffold-project.py]
    S6Scaffold --> S6PvPy[Confirmar pv.py sobrescrito]
    S6PvPy --> S6Summary[INFO: resumen final de toda la configuración]
    S6Summary --> EndOK([Fin: init completado])
```

Leyenda:
- `[Texto]` — paso interno, la skill actúa sin hablar con el usuario.
- `[INFO: Texto]` — la skill informa al usuario; no bloquea, continúa sin esperar respuesta.
- `[ASK: Texto]` — la skill informa y pide confirmación/datos; bloqueante, no avanza sin respuesta del usuario.
- `{Texto}` — rama de decisión; cada arista de salida lleva su propia etiqueta.
