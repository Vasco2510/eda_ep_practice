# Prueba del flujo en VS Code — modo manual y modo `work` (IA)

Recorrido para validar todo de principio a fin. Marca cada casilla; si algo no sale como dice
"Esperado", anótalo y se ajusta. La referencia completa está en [TUTORIAL.md](TUTORIAL.md).

## 0. Requisitos

| Dónde | Qué | Estado |
|---|---|---|
| Navegador | Extensión **Competitive Companion** | Instalada |
| VS Code | Extension Pack for Java | Instalada |
| PC | Python 3 y JDK (Java 21) | Instalados |
| PC | **Claude Code** con sesión iniciada (modo `work`) | `claude auth status --text` → no debe decir `Not logged in` |
| Opcional | Clave de Groq en `tools/claves.env` (respaldo) | `.\eda work --ping --proveedor groq` |

## 1. Abrir el proyecto
- [ ] VS Code → *File → Open Folder…* → `Z:\C26-2\EDA\ExamenEDA\Competitiva` (esa carpeta exacta).
- [ ] Espera a que Java termine de cargar. Abre la terminal (Ctrl+ñ).
- [ ] `.\eda selftest` → ✅ `OK: todas las plantillas pasaron (418812 comprobaciones)`.
- [ ] El listener debe estar corriendo (arranca solo; VS Code puede preguntar "Allow"). Si no:
      `.\eda` en una terminal que dejas abierta. ✅ `eda escuchando Competitive Companion en el puerto 27121`.
      Los demás comandos van en **otra** terminal.

---

## Parte A — Modo manual (sin IA) con Watermelon (Codeforces 4A)

**A1. Recibir el problema**
- [ ] Abre https://codeforces.com/problemset/problem/4/A y haz clic en Competitive Companion.
- [ ] ✅ En el listener: `▶ A. Watermelon  (nuevo)` y `1 tests de muestra`. Existen
      `src/problemas/cf4A/JSolution.java` y `tests/sample1.in` (`8`) / `sample1.out` (`YES`).

**A2. Resolver**
- [ ] Abre `src/problemas/cf4A/JSolution.java`, escribe en `solve()` y guarda (Ctrl+S):
```java
    static void solve() {
        int w = in.nextInt();
        out.println(w % 2 == 0 && w > 2 ? "YES" : "NO");
    }
```
- [ ] ✅ En el listener: `✓ hh:mm:ss entrega\cf4A\Main.java  [FastScanner]` (F se regenera al guardar).

**A3. Probar**
- [ ] `.\eda test` → ✅ `1/1 tests OK`.
- [ ] Cambia `"YES"` por `"SI"`, guarda, `.\eda test` → ✅ `✗ WA` con entrada, esperado y obtenido. Devuélvelo a `"YES"`.
- [ ] Crea `src/problemas/cf4A/tests/mio1.in` con `2` y `mio1.out` con `NO` → `.\eda test` → ✅ `2/2 tests OK`.

**A4. Probar una plantilla (sin enviar)**
- [ ] En `solve()` escribe `PersistentStack<Integer> ps = new PersistentStack<>();`, pon el cursor sobre
      `PersistentStack` → **Ctrl+.** → *Import 'PersistentStack'*. Guarda.
- [ ] ✅ `entrega/cf4A/Main.java` línea 1: `Plantillas incluidas: FastScanner, PersistentStack`.
- [ ] Borra esa línea y su import, guarda → ✅ la pila desaparece de `Main.java`.

**A5. Enviar**
- [ ] `.\eda test --copy` → ✅ `1/1 tests OK` y `copiado al portapapeles`.
- [ ] Codeforces → *Submit Code* → problema 4A → **Java 21** → pega → Submit → ✅ **Accepted**.

---

## Parte B — Modo `work` (IA)

**B1. Ciclo completo sin gastar nada** (respuestas simuladas del problema D: la 1 está mal, la 2 no usa la
plantilla, la 3 es correcta)
- [ ] ```
      .\eda work cf710567D --desde tools\demo\ia_simulada_D --como claude-code --usar PersistentLeftistHeap
      ```
- [ ] ✅ intento 1 `✗ WA` → intento 2 `3/3 tests OK` pero `✗ No usaste las plantillas obligatorias` →
      intento 3 `3/3 tests OK` y `✓ IA resolvió cf710567D en 3 intento(s)`. Al final imprime lo que va en
      tu W y lo deja en el portapapeles.
- [ ] Borra `tools\demo\ia_simulada_D\prompt*.md` (lo que se le habría enviado al modelo).

**B2. IA real, solo pegando (modo `work`)** con un problema público fácil: 71A *Way Too Long Words*
- [ ] Abre https://codeforces.com/problemset/problem/71/A → clic en Companion → ✅ `▶ A. Way Too Long Words`.
- [ ] **Ctrl+A, Ctrl+C** en esa misma página.
- [ ] `.\eda work` → ✅ `enunciado: portapapeles, verificado: contiene «Way Too Long Words»`, la
      explicación de la IA y `✓ IA resolvió cf71A en 1 intento(s)`.
- [ ] Abre `src/problemas/cf71A/JSolution.java`: pega el `import` arriba y reemplaza `solve()` con lo del
      portapapeles (si avisa, descomenta `t = in.nextInt();`). Guarda.
- [ ] `.\eda test` → ✅ `N/N tests OK`.
- [ ] `.\eda copy` → pega en Codeforces (Java 21) → ✅ Accepted.

**B3. IA real, todo automático (`go`)** con otro problema público: 231A *Team* (o el que prefieras)
- [ ] Companion en https://codeforces.com/problemset/problem/231/A → Ctrl+A, Ctrl+C.
- [ ] `.\eda go`
- [ ] ✅ Termina con `✓ LISTO: entrega/cf231A/Main.java está en el portapapeles`. Tu `JSolution.java`
      ya trae la solución.
- [ ] Pega en Codeforces → ✅ Accepted.

**B4. Con plantilla obligatoria y el problema del curso (grupo privado)**
- [ ] Companion en el problema D del grupo → Ctrl+A, Ctrl+C en su página.
- [ ] `.\eda go --usar PersistentLeftistHeap`
- [ ] ✅ `Plantillas incluidas: FastScanner, PersistentLeftistHeap` en la línea 1 de `entrega/cf710567D/Main.java`.
      (Su `JSolution.java` está vacío, así que no hay respaldo. Si antes escribes algo tuyo ahí y repites
      `go`, tu versión queda en `JSolution.HHMMSS.antes.txt` junto al archivo.)

**B5. Verificaciones de seguridad del enunciado**
- [ ] Con un problema abierto, copia **otra** cosa (por ejemplo un párrafo cualquiera) y corre `.\eda work`
      → ✅ `el portapapeles no parece el enunciado de este problema: lo ignoro` (no resuelve otro problema).
- [ ] `.\eda work --clip` con ese mismo portapapeles → ✅ error: `el portapapeles no menciona «…»`.

**B6. Sesión continua**
- [ ] Después de B2 y B3, mira el consumo que imprime cada ejecución:
      `tokens: entrada N (+M de caché)`. ✅ En el segundo problema, `M` es mucho mayor que `N` (el manual de
      plantillas se leyó de caché).
- [ ] `.\eda work --nueva-sesion` en un problema → ✅ abre una conversación nueva (`M` bajo otra vez).

**B6b. Consumo del plan**
- [ ] `.\eda uso` → ✅ `hoy: N llamadas · entrada … · salida …` y
      `Sesión de 5 h: X% usado → te queda ≈ Y%` con la hora de reinicio.
- [ ] Un problema con `.\eda go --uso` → ✅ al final: `consumo de esta resolución: …` y
      `tu sesión de 5 h: X% → Z% (esta resolución ≈ N punto(s))`.
- [ ] En PowerShell: `claude -p "/usage"` → ✅ mismos porcentajes que `.\eda uso`.

**B7. Respaldo (opcional)**
- [ ] `.\eda work --ping --proveedor groq` → ✅ `✓ el proveedor respondió: OK`.
- [ ] Para simular que Claude falla: `claude auth logout`, luego `.\eda work` → ✅ `↪ claude-code falló: sigo
      con el respaldo (groq)`. Vuelve a entrar con `claude auth login`.

---

## Qué reportar
- Pasos que fallaron o te sobraron, y qué decía la terminal.
- Problemas donde la IA no acertó: lee `entrega/<slug>/ia/log.md` y pásame el enunciado y lo que falló.
- Comandos que prefieras con otro nombre, o métodos que falten en las plantillas.
