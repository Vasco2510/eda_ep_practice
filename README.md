# EDA — asistente de competitiva (Java + plantillas persistentes)

Recibes el problema de Codeforces, lo resuelves con tus plantillas (`src/plantillas/`) y sale un único `Main.java`
listo para enviar. Solo Windows.

## 1. Puesta en marcha (una vez por PC)

**Necesitas:** Python 3.10+, JDK 21, VS Code + *Extension Pack for Java*, la extensión **Competitive Companion**
y el **motor A** con sesión (ver `PRIVADO.md`: **no está en git**, llévatelo aparte; última sección "Otra computadora").

```powershell
git clone <url-del-repo> ; cd <carpeta>
.\eda selftest        # debe terminar en: OK: todas las plantillas pasaron
.\eda work --ping     # debe responder: ✓ el motor respondió: OK
.\eda autostart on    # el listener arranca solo con Windows, sin ventana
```
Abre la carpeta en VS Code y recarga la ventana (Ctrl+Shift+P → *Reload Window*).

**El listener** recibe los problemas y dispara `work`. Sin `autostart`, déjalo a mano: `.\eda` en una terminal abierta
(o la tarea *EDA: iniciar* al abrir la carpeta). Estado: `.\eda autostart status` · reiniciar: `.\eda autostart restart`.

## 2. Modos (del más sutil al más explícito)

En todos: **clic en Competitive Companion** en el problema y luego, en su página, **Ctrl+A, Ctrl+C**.

1. **Trigger:** en `JSolution.java`, línea vacía, escribe `work` + **Tab**. Espera el globo "listo".
2. **go:** `.\eda go`
   → ambos dejan `JSolution.java` resuelto y `Main.java` en el portapapeles.
3. **work:** `.\eda work` → pega en `JSolution.java` → `.\eda test` → `.\eda copy`
4. **Manual:** escribes `solve()` → `.\eda test` → `.\eda copy`

**Si el juez rechaza:** copia el veredicto (Ctrl+A, Ctrl+C) y escribe `resp` + **Tab** (o `.\eda resp`).

Envía como **Java 21**. `.\eda copy` copia el problema *actual*; con varios abiertos: `.\eda copy <slug>`.

## 3. Útiles

`.\eda go --usar PersistentTreap` (obliga una plantilla; en trigger: `//@work PersistentTreap`) ·
`.\eda list` / `.\eda use <slug>` · `.\eda uso` (cuánto llevas gastado) · `.\eda work --nueva-sesion` ·
`.\eda autostart off`

## 4. Si falla

- **`work` + Tab no hace nada:** ¿`autostart status` dice *corriendo*? ¿Recargaste VS Code? ¿Quedó `//@work`? Si no, escríbela a mano.
- **Quedó `// work falló: …`:** el motivo está en esa línea (p. ej. faltaba copiar el enunciado). Corrige y repite.
- **Companion no envía:** el listener no corre, o el puerto 27121 está ocupado (`tools/config.json` + *Custom ports*).
- **Sin `PRIVADO.md`:** el respaldo se configura en `tools/claves.env` (copia `tools/claves.env.example`).
- Detalle: `TUTORIAL.md` · checklist: `PRUEBA_VSCODE.md`.
