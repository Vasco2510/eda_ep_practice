# Prueba del flujo en VS Code — modo manual, modo `work` y respuesta del juez

Recorrido para validar todo de principio a fin. Marca cada casilla; si algo no sale como dice
"Esperado", anótalo y se ajusta. La referencia completa está en [TUTORIAL.md](TUTORIAL.md).

## 0. Requisitos

| Dónde | Qué | Estado |
|---|---|---|
| Navegador | Extensión **Competitive Companion** | Instalada |
| VS Code | Extension Pack for Java | Instalada |
| PC | Python 3 y JDK (Java 21) | Instalados |
| PC | **Motor A** con sesión iniciada (modo `work`) | `.\eda work --ping` → `✓ el motor respondió: OK` |
| Opcional | Clave del motor B en `tools/claves.env` (respaldo) | `.\eda work --ping --proveedor B` |

## 1. Abrir el proyecto
- [ ] VS Code → *File → Open Folder…* → `Z:\C26-2\EDA\ExamenEDA\Competitiva` (esa carpeta exacta).
- [ ] Espera a que Java termine de cargar. Abre la terminal (Ctrl+ñ).
- [ ] `.\eda selftest` → ✅ `OK: todas las plantillas pasaron (418812 comprobaciones)`.
- [ ] El listener debe estar corriendo (arranca solo; VS Code puede preguntar "Allow"). Si no:
      `.\eda` en una terminal que dejas abierta. ✅ `eda escuchando Competitive Companion en el puerto 27121`.
      Los demás comandos van en **otra** terminal.

---

## Parte A — Modo manual con Watermelon (Codeforces 4A)

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

## Parte B — Modo `work`

**B1. Ciclo completo sin gastar nada** (respuestas simuladas del problema D: la 1 está mal, la 2 no usa la
plantilla, la 3 es correcta)
- [ ] ```
      .\eda work cf710567D --desde tools\demo\w_ejemplo_D --como A --usar PersistentLeftistHeap
      ```
- [ ] ✅ intento 1 `✗ WA` → intento 2 `3/3 tests OK` pero `✗ No usaste las plantillas obligatorias` →
      intento 3 `3/3 tests OK` y `Pasamos test en cf710567D en 3 intento(s)`. Al final imprime lo que va en
      tu W y lo deja en el portapapeles.
- [ ] Borra `tools\demo\w_ejemplo_D\encargo*.md` (lo que se habría enviado).

**B2. Solo pegando (modo `work`)** con un problema público fácil: 71A *Way Too Long Words*
- [ ] Abre https://codeforces.com/problemset/problem/71/A → clic en Companion → ✅ `▶ A. Way Too Long Words`.
- [ ] **Ctrl+A, Ctrl+C** en esa misma página.
- [ ] `.\eda work` → ✅ `enunciado: portapapeles, verificado: contiene «Way Too Long Words»`, la
      explicación y `Pasamos test en cf71A en 1 intento(s)`.
- [ ] Abre `src/problemas/cf71A/JSolution.java`: pega el `import` arriba y reemplaza `solve()` con lo del
      portapapeles (si avisa, descomenta `t = in.nextInt();`). Guarda.
- [ ] `.\eda test` → ✅ `N/N tests OK`.
- [ ] `.\eda copy` → pega en Codeforces (Java 21) → ✅ Accepted.

**B3. Todo automático (`go`)** con otro problema público: 231A *Team* (o el que prefieras)
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
      `unidades: entrada N (+M de caché)`. ✅ En el segundo problema, `M` es mucho mayor que `N` (la guía de
      plantillas se leyó de caché).
- [ ] `.\eda work --nueva-sesion` en un problema → ✅ abre un hilo nuevo (`M` bajo otra vez).

**B6b. Consumo del cupo**
- [ ] `.\eda uso` → ✅ `hoy: N llamadas · entrada … · salida …` y
      `Sesión de 5 h: X% usado → te queda ≈ Y%` con la hora de reinicio.
- [ ] Un problema con `.\eda go --uso` → ✅ al final: `consumo de esta resolución: …` y
      `tu sesión de 5 h: X% → Z% (esta resolución ≈ N punto(s))`.
- [ ] `.\eda uso --completo` → ✅ imprime el detalle completo.

**B7. Respaldo (opcional)**
- [ ] `.\eda work --ping --proveedor B` → ✅ `✓ el motor respondió: OK`.
- [ ] Para simular que el motor A falla: cierra su sesión (ver PRIVADO.md) y corre `.\eda work` → ✅ `↪ motor A falló: sigo
      con el respaldo (motor B)`. Vuelve a iniciar sesión.

---

## Parte C — Modo disparador: `work` + Tab dentro del editor (sin comandos)

**C0. Listener en segundo plano (una vez)**
- [ ] Cierra cualquier terminal que tenga `.\eda` corriendo (para no confundirte con dos).
- [ ] `.\eda autostart on` → ✅ `el listener arrancará solo cada vez que inicies sesión en Windows` y
      `estado ahora: corriendo`. (Para quitarlo cuando quieras: `.\eda autostart off`.)
- [ ] `.\eda autostart status` → ✅ `inicio automático de Windows: SÍ` y `listener … corriendo`.
- [ ] Cierra y abre VS Code → la tarea *EDA: iniciar* debe decir `el listener de eda ya está corriendo` (no se duplica).
- [ ] (Opcional) Cierra sesión de Windows y vuelve a entrar: el listener sigue sin abrir ninguna ventana.

**C1. Problema completo con el disparador** — usa un problema público fácil que no hayas hecho, p. ej.
231A *Team* (o 158A *Next Round*)
- [ ] Companion en su página → ✅ **`JSolution.java` se abre solo en VS Code** (no tocaste la terminal).
- [ ] En la página del problema: Ctrl+A, Ctrl+C.
- [ ] En `JSolution.java`, en una línea vacía (debajo del `solve()` vacío o arriba), escribe `work` y presiona
      **Tab** → ✅ se inserta `//@work `.
- [ ] Espera sin tocar el archivo → ✅ globo de Windows *"EDA work: Resolviendo…"* (~3 s después) y, tras
      20–90 s, *"EDA work: listo"*.
- [ ] ✅ `JSolution.java` ya tiene la solución y la línea `//@work` desapareció. Existe
      `entrega/<slug>/Main.java` y el portapapeles tiene ese archivo.
- [ ] `.\eda test` → ✅ `N/N tests OK`. Pega en Codeforces (Java 21) → ✅ Accepted.

**C2. Plantilla obligatoria**
- [ ] Con otro problema, escribe `work` + Tab y a continuación en la misma línea `PersistentLeftistHeap`
      (`//@work PersistentLeftistHeap`), rápido (antes de 2 s) → ✅ la solución importa esa plantilla
      (`Plantillas incluidas: … PersistentLeftistHeap` en `Main.java`).

**C3. Cuando falla, lo dice**
- [ ] Sin copiar ningún enunciado (portapapeles con otra cosa), escribe `work` + Tab en un problema nuevo
      → ✅ globo *"falló"* y en tu W, en lugar de `//@work`: `// work falló: no tengo el enunciado…`.
- [ ] Copia el enunciado y vuelve a escribir `work` + Tab → ✅ esta vez resuelve.

**C4. Revisar la bitácora**
- [ ] Abre `.eda_listener.log`: ✅ muestra `▶ work (disparador) <slug>`, los intentos y el resultado.

---

## Parte D — Respuesta del juez: `resp` (corrección)

**D1. Corrección con un veredicto real** — usa un problema que ya resolviste con `work`/`go` y fuerza un error:
- [ ] En tu `JSolution.java` cambia algo para que falle (por ejemplo una condición al revés), guarda y envía a
      Codeforces → ✅ el juez responde con error (Wrong answer / Runtime error).
- [ ] En el resultado del envío: **Ctrl+A, Ctrl+C**.
- [ ] En `JSolution.java`, línea vacía: escribe `resp` y **Tab** → ✅ se inserta `//Respuesta: error `.
- [ ] Espera el globo *"Corrigiendo…"* y luego *"listo"* → ✅ tu `JSolution.java` ya no tiene el cambio malo y
      el portapapeles tiene el `Main.java` nuevo.
- [ ] Si el veredicto era *Wrong answer* con entrada y respuesta correcta: ✅ existe `tests/juez1.in` / `.out`
      y `.\eda test` los incluye.
- [ ] Revisa `entrega/<slug>/w/respuesta_juez.md` (el veredicto guardado) y `w/log.md` (agrega `# corrección`).

**D2. Con nota** — repite D1 escribiendo después del marcador: `//Respuesta: error creo que es el caso n=1`
- [ ] ✅ el globo dice *Corrigiendo…* y la nota llega junto con el veredicto.

**D3. Desde la terminal**
- [ ] Copia otro veredicto y corre `.\eda resp` → ✅ `Corregiremos <slug>`, `respuesta del juez: N caracteres`, y termina
      con `✓ LISTO: entrega/<slug>/Main.java está en el portapapeles`.

**D4. Avisos**
- [ ] Con el **enunciado** en el portapapeles (no el veredicto), `resp` + Tab → ✅ en tu W: `// work falló: el portapapeles
      parece el enunciado, no la respuesta del juez…`.
- [ ] En un problema donde todavía no hay solución en tu W, `resp` + Tab → ✅ `// work falló: no hay una solución previa…`.

**D5. Enviaste el archivo equivocado** (lo más común: un error de lectura de entrada en el ejemplo)
- [ ] `.\eda copy` copia el del problema *actual*; con varios problemas abiertos usa `.\eda copy <slug>` → ✅ el
      juez acepta el ejemplo del problema correcto.

---

## Qué reportar
- Pasos que fallaron o te sobraron, y qué decía la terminal.
- Problemas donde no salió: lee `entrega/<slug>/w/log.md` y pásame el enunciado y lo que falló.
- Comandos que prefieras con otro nombre, o métodos que falten en las plantillas.
