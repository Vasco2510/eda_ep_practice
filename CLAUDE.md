# Proyecto: asistente de competitiva para el examen de EDA (Java 21, Codeforces)

Responde en español.

## Estructura
- `src/plantillas/*.java`: estructuras persistentes del curso (paquete `plantillas`). Cada archivo tiene una
  sola `public class` en la columna 0 y un comentario de uso arriba.
- `src/problemas/<slug>/JSolution.java` (W): donde se programa. `tests/*.in|.out`, `problem.json`, `enunciado.*`.
- `entrega/<slug>/Main.java` (F): se genera desde W con `tools/eda.py` (no se edita a mano). Es lo que se envía.
- `entrega/<slug>/Main_ia.java`, `entrega/<slug>/ia/`: solución generada por `eda ia`.

## Comandos (PowerShell, desde esta carpeta)
- `.\eda test [slug]`: renderiza W → F, compila y corre los tests. Úsalo para verificar cualquier cambio en W.
- `.\eda list`, `.\eda use <slug>`: problemas; sin slug se usa el problema actual.
- `.\eda selftest`: verifica todas las plantillas contra fuerza bruta. Córrelo si tocas `src/plantillas`.
- `.\eda ia --clip --solve`: resolución automática con un LLM (ver TUTORIAL_IA.md).

## Al resolver un problema con el usuario
- Escribe la solución en `src/problemas/<slug>/JSolution.java`, dentro de `solve()`, respetando la plantilla
  (`FastScanner in`, `PrintWriter out`, `t = in.nextInt()` si hay varios casos).
- Si una plantilla encaja (heap, pila, cola, BST, segment tree, trie, arreglo persistente), úsala con
  `import plantillas.Nombre;` y solo por sus métodos `public`: el curso evalúa su uso. No copies su código en W.
- Verifica con `.\eda test`. Si hay dudas de correctitud, agrega casos propios en `tests/` (p. ej. comparando
  contra una fuerza bruta).
- Explica la idea, por qué es correcta y la complejidad: el usuario está aprendiendo.
- No edites archivos de `entrega/` a mano; se regeneran.
