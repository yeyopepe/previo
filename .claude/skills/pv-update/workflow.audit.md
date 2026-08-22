```mermaid
flowchart TD
    Start([Invocación de pv-update])

    Start --> S1Read[Leer .claude/pv-context.json best-effort]
    S1Read --> S1Exists{El fichero existe?}
    S1Exists -->|No| S1Info[INFO: el framework no está inicializado, ejecuta pv-init]
    S1Info --> End1([Fin: nada que auditar])
    S1Exists -->|Sí| S2Run

    S2Run[Ejecutar audit-context.py] --> S2Empty{problems viene vacío?}
    S2Empty -->|Sí, y lastVerifiedVersion ya existe| S2Healthy[INFO: configuración saludable]
    S2Healthy --> End2([Fin: nada que arreglar])
    S2Empty -->|Sí, pero sin lastVerifiedVersion| S35Run
    S2Empty -->|No, hay problemas| S3Loop

    S3Loop[Recorrer cada problema devuelto, en orden] --> S3Kind{Tipo de problema}
    S3Kind -->|context-invalid-json| S3Invalid[ASK: corregir el JSON a mano o indicar la estructura pretendida]
    S3Invalid --> S3InvalidDec{JSON ya corregido?}
    S3InvalidDec -->|Sí| S2Run
    S3InvalidDec -->|No, sigue esperando| End3Blocked([Fin: bloqueado por JSON inválido])

    S3Kind -->|version-check-downgrade| S3Downgrade[Ejecutar mark-verified.py --block]
    S3Downgrade --> S3DowngradeAsk[ASK: el downgrade fue intencional?]
    S3DowngradeAsk --> S3DowngradeDec{Respuesta del usuario}
    S3DowngradeDec -->|Fue intencional| S3DowngradeConfirm[Ejecutar mark-verified.py --confirm-downgrade]
    S3DowngradeConfirm --> S3Next
    S3DowngradeDec -->|No fue intencional| S3DowngradeGuide[INFO: cómo restaurar los ficheros correctos]
    S3DowngradeGuide --> End3Blocked2([Fin: bloqueado, blocked=true se mantiene])

    S3Kind -->|Cualquier otro id de problema| S3Fix[Aplicar el fix determinístico correspondiente]
    S3Fix --> S3Next{Quedan más problemas por procesar?}
    S3Next -->|Sí| S3Loop
    S3Next -->|No| S35Run

    S35Run[Ejecutar mark-verified.py --clear] --> S4Rerun[Rerun audit-context.py para confirmar]
    S4Rerun --> S4Report[INFO: informe final agrupado por área]
    S4Report --> EndOK([Fin: auditoría completada])
```

Leyenda:
- `[Texto]` — paso interno, la skill actúa sin hablar con el usuario.
- `[INFO: Texto]` — la skill informa al usuario; no bloquea, continúa sin esperar respuesta.
- `[ASK: Texto]` — la skill informa y pide confirmación/datos; bloqueante, no avanza sin respuesta del usuario.
- `{Texto}` — rama de decisión; cada arista de salida lleva su propia etiqueta.
