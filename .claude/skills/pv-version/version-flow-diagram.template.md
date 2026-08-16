# Cómo funciona `/pv-version`

Diagrama general del proceso de preparar una entrega, sin detalle de scripts ni nombres de parámetros — pensado para mostrarse tal cual si el usuario pregunta "¿cómo funciona `/pv-version`?" durante la invocación, o como referencia en la documentación del proyecto.

```mermaid
flowchart LR
    Guard{"implemented/\n¿vacío?"}
    Resolve["Resolver cada entrada\n(usuario confirma → closed)"]
    Folder["Crear versions/XXXX\n(files/, docs/)"]
    Compile["Generar el entregable\n(how-to-compile-version.md)"]
    Docs["Comprimir y copiar documentación\ntécnica y funcional vigente a docs/"]
    Changelog["pv-internal-changelog\nredacta changelog.md desde closed/"]
    Confirm["Confirmar entrega\nal usuario"]

    Guard -- No --> Resolve --> Guard
    Guard -- Sí --> Folder --> Compile --> Docs --> Changelog --> Confirm

    classDef guardrail fill:#e03131,color:#fff
    classDef core fill:#2b6cb0,color:#fff
    classDef internal fill:#805ad5,color:#fff
    classDef done fill:#2f9e44,color:#fff
    class Guard,Resolve guardrail
    class Folder,Compile,Docs core
    class Changelog internal
    class Confirm done
```

Leyenda: rojo = guardarraíl de `implemented/` (bloquea hasta resolverse); azul = pasos mecánicos de `pv-version`; morado = delegado en `pv-internal-changelog`; verde = fin del proceso.
