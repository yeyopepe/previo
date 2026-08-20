# Prompt history — 00214

Historical information about the analysis process, not current information. Records, verbatim and without rephrasing, the successive prompts with which the user raised and expanded this entry — they can be incomplete or contradictory with each other, since they reflect how the request evolved session by session, not the final result (that lives in `description.md`).

**Exclusive use of `pv-new` and `pv-fix`.** No other skill in the framework (`pv-how`, `pv-do`, `pv-status`, etc.) should read this file or take it into account: the source of truth for what's being asked is always `description.md`.

## 2026-08-15 — initial session

hay operaciones que tardan un tiempo en ejecutarse y dejan al jugador bloqueado hasta que terminan. Debemos implementar un sistema que al menos informe al jugador de lo que está ocurriendo y le devuelva el control cuando todo termine: una pequeña modal con un breve texto descriptivo y una animación.
Impleméntalo y úsalo cuando metemos cartas en un mazo, porque es una operación que puede tardar mucho o poco según el número de cartas que se están intentando introducir en el mazo. Puedes hacer la prueba con 1 carta y con 10.
