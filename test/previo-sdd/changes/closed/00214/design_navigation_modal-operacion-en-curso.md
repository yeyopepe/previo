# Navegación — Modal de operación en curso al meter cartas en un mazo

```mermaid
stateDiagram-v2
    [*] --> MesaEdicion: Modo edición, mesa con al menos un mazo

    MesaEdicion --> ArrastrandoCartas: Arrastra una selección de 1+ cartas

    ArrastrandoCartas --> MesaEdicion: Suelta fuera de cualquier mazo\n(sin cambios de este flujo)
    ArrastrandoCartas --> ModalOperacionEnCurso: Suelta sobre un mazo

    ModalOperacionEnCurso --> MesaEdicion: Operación termina\n(cierre automático, sin acción del jugador)

    note right of ModalOperacionEnCurso
        Sin botones. No se puede cerrar
        ni cancelar manualmente.
        Texto: "Añadiendo N carta(s) al mazo…"
        + spinner circular.
    end note
```

- **Suelta fuera de cualquier mazo**: el arrastre se comporta como hoy (las cartas quedan en su nueva posición sobre la mesa) — no interviene este cambio.
- **Suelta sobre un mazo**: las cartas se añaden al mazo (como ya ocurre hoy, sin confirmación previa) y, mientras dura esa operación, se muestra la modal. El jugador no tiene ninguna acción disponible durante ese estado — solo espera a que se cierre sola.
- Con 1 sola carta el ciclo `ArrastrandoCartas → ModalOperacionEnCurso → MesaEdicion` es el mismo, aunque la modal pueda no llegar a percibirse por lo breve de la operación.
