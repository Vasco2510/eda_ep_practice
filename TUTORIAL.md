# Asistente EDA — Tutorial (VS Code)

Tú trabajas en **W** (`JSolution.java`, un archivo Java normal con autocompletado). El sistema genera **F**
(`entrega/<slug>/Main.java`): tu lógica **más** el código de las plantillas que importaste, en un solo
archivo. **F es lo que se envía a Codeforces**; nunca se edita a mano.

Hay dos formas de llegar a la solución, y se pueden combinar:

| | Modo manual | Modo `work` | Disparador (sin comandos) |
|---|---|---|---|
| Quién codea `solve()` | Tú | `work` (motor A; motor B de respaldo) | `work` |
| Cómo lo inicias | `.\eda test` | `.\eda go` (todo) o `.\eda work` (tú pegas) | En `JSolution.java`: `work` + Tab |
| Qué se envía | `entrega/<slug>/Main.java` | `entrega/<slug>/Main.java` | `entrega/<slug>/Main.java` |

---

## 1. Flujo completo: del problema a Codeforces

### Paso 0 — Tener el listener corriendo (elige una forma, una sola vez)
El listener es el programa que recibe los problemas de Competitive Companion (y, en el modo disparador,
las órdenes de `work`). Tres formas de tenerlo:

| Forma | Cómo | Cuándo conviene |
|---|---|---|
| **En segundo plano desde que inicias Windows** (recomendada) | `.\eda autostart on` una sola vez. Crea un acceso directo en el inicio de Windows y lo arranca ya. Sin ventana; bitácora en `.eda_listener.log`. Quitarlo: `.\eda autostart off`; estado: `.\eda autostart status` | No quieres pensar en él: funciona aunque VS Code esté cerrado |
| Al abrir VS Code | La tarea *EDA: iniciar* arranca sola al abrir la carpeta `Competitiva` (VS Code puede preguntar si permites tareas automáticas: **Allow**) | No quieres nada instalado en el inicio de Windows |
| A mano | `.\eda` en una terminal que dejas abierta | Depuración |

Si el listener ya está corriendo, iniciar otro solo avisa `el listener de eda ya está corriendo` y termina
(no se duplican). Verás al arrancar: `eda escuchando Competitive Companion en el puerto 27121`.
Para los demás comandos abre **otra** terminal (el `+` del panel).
**Tras editar `tools/*.py`** (o tras actualizar el proyecto) el listener en segundo plano sigue con el código viejo: `.\eda autostart restart`.

### Paso 1 — Recibir el problema (común a los dos modos)
En Codeforces, abre el problema y haz clic en el ícono verde de **Competitive Companion**.
En la terminal del listener aparece:
```
▶ D. Ejercito supremo  (nuevo)
  W: src\problemas\cf710567D\JSolution.java
  F: entrega\cf710567D\Main.java
  1 tests de muestra
```
Se crea `src/problemas/<slug>/` con `JSolution.java` y los tests de ejemplo. Ese pasa a ser el
**problema actual** (todos los comandos siguientes lo usan si no indicas otro).
Si el problema ya existía, **tu código no se toca**: solo se actualizan los tests.

### Paso 2 — Elige el modo

#### Modo manual (tú escribes la solución)
1. Abre `JSolution.java` y escribe la lógica en `solve()`. Lectura lista: `in.nextInt()`, `in.nextLong()`,
   `in.nextIntArray(n)`, `in.nextLongArray1(n)`; salida con `out.println(...)`. Varios casos:
   descomenta `t = in.nextInt();` en `main()`.
2. ¿Necesitas una estructura persistente? Escribe su nombre (`PersistentStack`…) y acepta el auto-import
   (**Ctrl+.**), o escribe `import plantillas.PersistentStack;`. Si borras el import, la estructura
   desaparece de F.
3. Guarda (Ctrl+S) y corre **`.\eda test`**. Debe dar `N/N tests OK`.
4. Corre **`.\eda copy`** (o `.\eda test --copy`, que copia solo si todo pasó).

#### Modo `work` (resuelve tu problema)
1. En la **misma página del problema: Ctrl+A, Ctrl+C.** Copia el enunciado al portapapeles.
2. Elige cuánto quieres automatizar:

   | Comando | Qué hace | Después tú |
   |---|---|---|
   | **`.\eda go`** | Resuelve tu problema y entrégalo: aplica a tu W → prueba tu W → copia `Main.java` | Pegas en Codeforces. **Terminaste** |
   | **`.\eda work`** | Resuelve tu problema y deja en el portapapeles solo lo que va en tu W (imports + `solve()`) | Pegas en `JSolution.java`, `.\eda test`, `.\eda copy` |
   | `.\eda work --completo` | Resuelve tu problema y deja `Main_w.java` completo (sin pasar por tu W) | Pegas en Codeforces |

   Tarda entre 20 s y un par de minutos. Verás la explicación y cada intento con sus tests.
   **Solo entrega algo si pasa los tests de ejemplo** (hasta 4 intentos, corrigiéndose con el error).
3. Con `go` el flujo termina así:
   ```
   Pasamos test en cf710567D en 1 intento(s), 22 s
   ✓ solución aplicada a tu W: src\problemas\cf710567D\JSolution.java
   ── probando tu W con los ejemplos ──
   ✓ OK  sample1 …          3/3 tests OK
   ✓ LISTO: entrega/cf710567D/Main.java está en el portapapeles → pégalo en Codeforces (Java 21)
   ```
   Si tu W ya tenía código, se guarda antes en `JSolution.HHMMSS.antes.txt` (junto a tu W).
4. Con `work` (modo "tú pegas"), el portapapeles trae tres cosas: el `import plantillas.…` (va arriba,
   con los otros imports), `solve()` con sus funciones auxiliares (reemplaza tu `solve()` vacío) y, si lo
   avisa, hay que descomentar `t = in.nextInt();` en `main()`.

**Obligar a usar una plantilla** (por ejemplo, en un simulacro donde se pide usar la persistencia):
`.\eda go --usar PersistentLeftistHeap`. Si sale sin ella, el intento se rechaza.

#### Modo disparador: `work` + Tab dentro del editor (sin escribir comandos)
Es el mismo `go`, pero se dispara desde `JSolution.java`. Requiere el listener corriendo (Paso 0).

1. **Companion:** clic en la página del problema. Se crea el problema y **`JSolution.java` se abre solo
   en VS Code** (`open_with`).
2. **Copia el enunciado:** Ctrl+A, Ctrl+C en la página (antes de disparar; el listener lo lee en ese momento).
3. **En `JSolution.java`, en una línea vacía, escribe `work` y presiona `Tab`.** Se inserta `//@work`.
   Opcional, en la misma línea, nombres de plantillas para obligar a usarlas: `//@work PersistentTreap`.
4. **Espera.** VS Code guarda solo (autoguardado de 0,8 s), el listener ve la línea (espera 2 s sin
   cambios, por si sigues escribiendo nombres) y aparece un **globo de Windows: "Resolviendo…"**. Tarda
   entre 20 s y un par de minutos. **No edites `JSolution.java` mientras tanto.**
5. **Termina** con otro globo ("listo" o "falló"). Si salió bien: tu `JSolution.java` ya tiene la
   solución (la línea `//@work` desaparece), `entrega/<slug>/Main.java` está generado y **también está
   en el portapapeles**: pégalo en Codeforces. Si tu W tenía código, quedó en `JSolution.HHMMSS.antes.txt`.
6. **Si falló:** en lugar de `//@work` queda un comentario `// work falló: <motivo>` (por ejemplo, que no
   encontró el enunciado en el portapapeles). Corrígelo (copia el enunciado) y escribe `work` + Tab otra
   vez. Detalle en `entrega/<slug>/w/log.md`; si algo raro pasa, mira `.eda_listener.log`.

Notas: el snippet `work` está en `.vscode/eda.code-snippets` y necesita en `.vscode/settings.json`
`files.autoSave` (guardado automático) y `editor.tabCompletion: onlySnippets` (Tab expande snippets);
ambos ya están puestos. Usa los mismos motores que `work`/`go` (PRIVADO.md). Opciones extra para
el disparador (p. ej. `["--effort", "medium"]`): `trigger_args` en `tools/config.json`.

#### Cuando el juez rechaza tu envío: `resp` (respuesta y corrección)
Si Codeforces responde con error (Runtime error, Wrong answer, Time limit…), en vez de reescribir a mano:

1. En el resultado del envío: **Ctrl+A, Ctrl+C** (el veredicto completo: caso, salida, log del checker).
2. En `JSolution.java`, en una línea vacía, escribe **`resp`** y **Tab**. Se inserta `//Respuesta: error`.
   Puedes agregar una nota en la misma línea: `//Respuesta: error creo que es el caso n=1`.
3. Espera el globo *"Corrigiendo…"*. Se toma el veredicto del portapapeles y se envía junto con el enunciado y
   **tu código enviado**; se busca la causa real y se corrige. Si el veredicto trae **entrada y respuesta
   correcta** (Wrong answer), ese caso queda como test local (`tests/juezN.in` / `.out`) y la corrección tiene
   que pasarlo también.
4. Al terminar: tu `JSolution.java` trae la corrección y el nuevo `Main.java` ya está en el portapapeles.
   Repite las veces que haga falta.

Desde la terminal: `.\eda resp` (mismo efecto, toma el portapapeles). Notas:
- Hay que haber resuelto antes con `work`/`go`: así queda guardado el enunciado (`enunciado.md`) y hay una solución en tu W.
- Sigue el mismo hilo: sabe lo que ya intentó. El veredicto queda en `entrega/<slug>/w/respuesta_juez.md` y la
  bitácora `w/log.md` se **agrega** (no se pisa).
- Si copiaste otra cosa (por ejemplo el enunciado), el aviso queda en tu W: `// work falló: …`.
- **Antes de enviar, mira que sea el problema correcto.** Un error de lectura de entrada (`NumberFormatException:
  Cannot parse null string`) en el ejemplo casi siempre es un `Main.java` de otro problema. `.\eda copy` copia el
  del problema *actual*; con varios abiertos usa `.\eda copy <slug>`.

### Paso 3 — Enviar
1. Si no lo hiciste ya: **`.\eda copy`** copia `entrega/<slug>/Main.java`.
   (Sin pasar por W, lo de `work` está en `.\eda copy --work`.)
2. En Codeforces → **Submit Code** → Lenguaje **Java 21** → pega → Submit. Es un solo archivo con
   `public class Main`, sin `package` ni `import plantillas`.

### Resumen de una línea
```
Companion (clic)  →  [manual: escribe solve() → .\eda test]  o  [work: Ctrl+A, Ctrl+C → .\eda go]
                  o  [disparador: Ctrl+A, Ctrl+C → en JSolution.java "work" + Tab]      →  .\eda copy  →  pegar en Codeforces
                                                                            (go y el disparador ya dejan Main.java en el portapapeles)
```

---

## 2. Comandos

Escríbelos en PowerShell dentro de `Competitiva` con el prefijo `.\eda`. Sin `[slug]` se usa el problema actual.

| Comando (atajo) | Qué hace |
|---|---|
| `.\eda` | Listener de Competitive Companion + re-render de F en vivo + disparador `work` + Tab. Déjalo abierto (o usa `autostart`) |
| `.\eda autostart on` / `off` / `status` / `restart` | El listener arranca solo al iniciar Windows, en segundo plano y sin ventana (Paso 0) |
| `.\eda go` | **Resuelve tu problema y entrégalo**: aplica a tu W → prueba → copia `Main.java` |
| `.\eda work` (`w`) | Resuelve tu problema y deja en el portapapeles lo que va en tu W |
| `.\eda test` (`t`) | Genera F, lo compila y lo corre contra `tests/*.in`. Muestra OK / WA / RE / TLE con la diferencia |
| `.\eda test --copy` | Igual, y si todo pasa copia F al portapapeles |
| `.\eda resp` | Corrige tu solución con la respuesta del juez que copiaste (§1) |
| `.\eda copy` (`c`) | Copia `Main.java` al portapapeles (`.\eda copy <slug>` para uno concreto) |
| `.\eda render` (`r`) | Genera F una vez (el listener ya lo hace solo) |
| `.\eda new <slug>` | Crea un problema a mano (sin Competitive Companion) |
| `.\eda use <slug>` / `.\eda list` (`l`) | Cambia / lista los problemas |
| `.\eda uso` (`u`) | Unidades que gastó `work` en esta máquina + cuánto llevas usado de tu cupo (§5) |
| `.\eda selftest` | Verifica todas las plantillas (~420 mil comprobaciones contra fuerza bruta) |
| `.\eda demo` | Crea o reinicia el problema de práctica `demo_pila` |

Opciones de `work` y `go`:

| Opción | Efecto |
|---|---|
| `--usar A,B` | Obliga a usar esas plantillas |
| `--aplicar` | (`work`) escribe la solución en tu W en vez de copiarla (es lo que hace `go`) |
| `--completo` | (`work`) copia `Main_w.java` completo |
| `--clip` / `--forzar` | Exige el portapapeles como enunciado (ver §5); `--forzar` salta la verificación |
| `--nueva-sesion` | Abre un hilo nuevo (por defecto continúa el anterior) |
| `--error` / `--nota "…"` | (`work`) corrige con el veredicto del portapapeles (es lo que hace `resp`); nota opcional |
| `--proveedor A\|B\|C\|D`, `--modelo Y`, `--effort Z`, `--intentos N` | Motor, versión, esfuerzo y nº de intentos (detalle en PRIVADO.md) |
| `--ping` | Prueba la conexión con una solicitud mínima |
| `--uso` | Al terminar, muestra cuánto bajó tu plan por esta resolución (consulta `/usage` antes y después) |

(`--solve` y `--copy` siguen funcionando: son el modo por defecto de `work` y `--completo`.)

### Atajos en VS Code
**Ctrl+Shift+P → "Tasks: Run Task"** lista: *iniciar*, *go*, *work*, *test*, *test + copiar* y *copiar*.
*Tasks: Run Test Task* corre `EDA: test`. Para atajos de teclado, agrega esto a `keybindings.json`
(Ctrl+Shift+P → "Preferences: Open Keyboard Shortcuts (JSON)"):
```json
{ "key": "ctrl+alt+g", "command": "workbench.action.tasks.runTask", "args": "EDA: go (resuelve tu problema y entrégalo)" },
{ "key": "ctrl+alt+t", "command": "workbench.action.tasks.runTask", "args": "EDA: test" },
{ "key": "ctrl+alt+c", "command": "workbench.action.tasks.runTask", "args": "EDA: copiar Main.java" }
```
(IntelliJ: las mismas acciones están en `.run/` — `EDA go`, `EDA work`, `EDA test`, `EDA copiar`… — y aparecen en el selector de ejecución.)

---

## 3. Estructura de carpetas

```
Competitiva/
├── src/plantillas/          plantillas (paquete `plantillas`). Se incrustan en F solo si W las importa
├── src/problemas/<slug>/    uno por problema
│   ├── JSolution.java       ← W: aquí trabajas
│   ├── tests/               *.in / *.out (muestras de Companion + los tuyos: mio1.in / mio1.out)
│   └── problem.json         nombre, URL y límites
├── entrega/<slug>/
│   ├── Main.java            ← F: lo que se envía (se genera solo)
│   ├── Main_w.java          lo que generó work, renderizado (sin pasar por tu W)
│   └── w/                   JSolution.java de work, solve.java.txt, log.md y respuesta_juez.md
├── tools/                   eda.py, work.py, plantilla de W, config, claves.env (tus claves; no se sube a git)
├── tests/PlantillasTest.java verificación de las plantillas contra fuerza bruta
└── borradores/              tus archivos anteriores
```

## 4. Plantillas

| Estructura | Plantilla | Operaciones |
|---|---|---|
| Arreglo persistente | `PersistentArray<T>` | `set`, `get`, `copy` |
| Segment tree (suma, update puntual, k-ésimo) | `PersistentSegmentTree` | `set`, `add`, `query`, `kth` |
| Segment tree con update en rango | `PersistentLazySegmentTree` | `rangeAdd`, `query` |
| Trie de strings | `PersistentTrie` | `insert`, `erase`, `count`, `countPrefix` |
| Trie binario (XOR) | `PersistentBinaryTrie` | `insert`, `erase`, `maxXor`, `minXor`, `kth` |
| Pila / Cola | `PersistentStack<T>`, `PersistentQueue<T>` | `push`, `pop`, `peek`, `size`, `copy` |
| BST balanceado (treap) | `PersistentTreap` | `insert`, `erase`, `contains`, `rank`, `kth`, `floor`, `ceiling` |
| Heap | `PersistentLeftistHeap` (O(log n) garantizado) | `insert`, `merge`, `extractMin` |
| Fibonacci heap | `PersistentFibonacciHeap` (sin `decreaseKey`) | `insert`, `merge`, `extractMin` |
| Lectura rápida | `FastScanner` (siempre incluido) | `nextInt`, `nextLong`, `nextIntArray`, … |

Todas usan **versiones con id entero**: cada operación que modifica devuelve el id de la versión nueva y
las anteriores no cambian. La versión 0 es la estructura vacía. Ejemplos:

```java
// Arreglo persistente de cualquier tipo, índices [0, n-1]
PersistentArray<Integer> arr = new PersistentArray<>(n, 0);      // o new PersistentArray<>(Integer[] a)
int a1v = arr.set(0, pos, x);  arr.get(a1v, pos);  arr.get(0, pos);

// Segment tree persistente (suma, update puntual) sobre [1, n]
PersistentSegmentTree st = new PersistentSegmentTree(1, n);
int[] root = new int[q + 1];
root[0] = st.build(a);                 // a[1..n] (usa in.nextLongArray1(n)); o root[0] = 0 si todo es 0
root[i] = st.set(root[j], pos, val);   // o st.add(root[j], pos, delta)
long s = st.query(root[i], l, r);
// k-ésimo menor en a[l..r]: comprime valores a 1..m, pre[i] = st.add(pre[i-1], comp(a[i]), 1)
int idx = st.kth(pre[l - 1], pre[r], k);   // índice comprimido (-1 si no hay k)

// Update en rango
PersistentLazySegmentTree lz = new PersistentLazySegmentTree(1, n);
int v1 = lz.rangeAdd(v0, l, r, x);  long s2 = lz.query(v1, l, r);

// Trie de strings ('a'..'z') y trie binario (XOR)
PersistentTrie tr = new PersistentTrie();
int t1 = tr.insert(0, "abc"); tr.count(t1, "abc"); tr.countPrefix(t1, "ab"); int t2 = tr.erase(t1, "abc");
PersistentBinaryTrie bt = new PersistentBinaryTrie();             // valores < 2^30 (cambia BITS para long)
pre[i] = bt.insert(pre[i - 1], a[i]);                            // pre[0] = 0
long best = bt.maxXor(pre[l - 1], pre[r], x);                     // también minXor y kth en [l, r]

// BST persistente (treap, multiconjunto de long)
PersistentTreap bst = new PersistentTreap();
int b1 = bst.insert(0, 5); int b2 = bst.erase(b1, 5);
bst.contains(b1, 5); bst.rank(b1, k); bst.kth(b1, 1); bst.floor(b1, k); bst.ceiling(b1, k); bst.size(b1);

// Pila y cola (genéricas)
PersistentStack<Long> ps = new PersistentStack<>();
int v = ps.push(0, 5L); v = ps.pop(v); ps.peek(v); ps.size(v); ps.copy(v);
PersistentQueue<Long> pq = new PersistentQueue<>();
int w = pq.push(0, 5L); pq.peek(w); pq.back(w); w = pq.pop(w);

// Heaps (min-heap de long, con un id opcional; para max-heap inserta -key)
PersistentLeftistHeap h = new PersistentLeftistHeap();          // o PersistentFibonacciHeap
int a1 = h.insert(0, key, id); h.minKey(a1); h.minId(a1); int a2 = h.extractMin(a1); int m = h.merge(a1, a2);
```

`peek`/`back` de pila y cola devuelven `null` si está vacía. En los heaps revisa `isEmpty(v)` antes de `minKey`.

**Fibonacci heap:** un Fibonacci heap clásico necesita punteros al padre y cortes en cascada para
`decreaseKey`, y eso no se puede compartir entre versiones. La versión persistente hace `insert`/`merge`
perezosos y consolida por grado en `extractMin`, sin `decreaseKey`. Si repites `extractMin` sobre
versiones viejas, usa `PersistentLeftistHeap`. **Si tu profesor definió la estructura de otra forma,
adapta esta plantilla.** Si el problema **no** pide persistencia en el heap (se acepta la "STL"), usa
`java.util.PriorityQueue` (max-heap: `new PriorityQueue<>(Comparator.reverseOrder())`).
**Memoria de `PersistentTrie`:** 26 hijos por nodo → 10^6 caracteres insertados ≈ 110 MB; para muchos
caracteres, reduce `ALPHA` o usa el trie binario.

### Agregar o modificar plantillas
Crea `src/plantillas/Nombre.java` con `package plantillas;` y **una** clase `public class Nombre`
declarada en la columna 0 (como las existentes). El render le quita el `public` y la pega al final de F.
Si una plantilla usa otra, la incluye sola. Después corre `.\eda selftest`.
**Comenta bien la plantilla:** el bloque `/** … */` de arriba (qué es, cuándo usarla, un ejemplo) y una
línea encima de cada método público. De ahí sale la guía que usa `work` (PRIVADO.md).

---

## 5. Motores, cupo y consumo

`work`, `go` y `resp` usan un **motor principal (A)** y, si falla (sin sesión, límite de uso, error), siguen solos
con un **motor de respaldo (B)**. Qué es cada uno, cómo configurarlo, sus límites, el hilo continuo y la guía de
plantillas: **`PRIVADO.md`** (archivo local; no se sube al repo).

- **Probar la conexión:** `.\eda work --ping`.
- **¿Cuánto llevo gastado y cuánto me queda?** `.\eda uso` (unidades por llamada y % de tu cupo, con la hora de
  reinicio). `.\eda go --uso` muestra cuánto bajó tu cupo por esa resolución. `.\eda uso --completo` imprime el detalle.
- **El enunciado:** `work`/`go` toman el del portapapeles automáticamente, **solo si es el de este problema** (texto
  largo con Input/Output, no es código y menciona el título que envió Companion). Si no, usan `enunciado.md`/`.pdf`
  de la carpeta del problema o la URL. `--clip` lo exige (falla si no coincide); `--forzar` salta la verificación.
- **Hilo continuo:** cada problema continúa el hilo del anterior (la guía de plantillas queda en caché);
  `--nueva-sesion` abre un hilo nuevo si algo se confunde.
- **Ajustes** (`tools/config.json`, todos opcionales): `w_motor`, `w_respaldo`, `w_version`, `w_esfuerzo`, `w_intentos`,
  `w_max_problemas_hilo`, `open_with` (editor que abre el W al recibir un problema), `trigger_debounce`, `trigger_args`,
  `notificaciones`. Valores y significado: `PRIVADO.md`.
- **Ojo:** "pasa los tests" significa que pasa los **ejemplos** (y los que agregues en `tests/`). Puede pasarlos y aun
  así fallar en Codeforces: lee la explicación en `entrega/<slug>/w/log.md`, y si el juez lo rechaza usa **`resp`** (§1).

---

## 6. Problemas comunes

| Síntoma | Qué hacer |
|---|---|
| `.\eda` no se reconoce | La terminal debe estar en `…\Competitiva` |
| Escribo `work` y Tab pero no pasa nada | ¿Está el listener? `.\eda autostart status`. ¿Quedó la línea `//@work` (si no, el snippet no se expandió: escríbela a mano)? ¿Se guardó el archivo (autoguardado)? ¿Es una línea propia, no al final de otra? Mira `.eda_listener.log` |
| `resp` + Tab y no pasa nada | Igual que `work`: ¿listener corriendo?, ¿quedó la línea `//Respuesta: error`?, ¿se guardó? Y ¿copiaste el veredicto (Ctrl+A, Ctrl+C en el resultado del envío)? |
| Quedó `// work falló: …` en mi W | Lee el motivo, corrígelo (p. ej. copia el enunciado con Ctrl+A, Ctrl+C) y escribe `work` + Tab otra vez |
| El disparador usa código viejo después de editar `tools/*.py` | `.\eda autostart restart` |
| No aparecen los globos de Windows | Revisa que el modo "No molestar" esté apagado; el resultado igual queda en tu W y en `.eda_listener.log` (`"notificaciones": false` los desactiva) |
| "el puerto 27121 está ocupado por otro programa" | Lo usa otra cosa (p. ej. la extensión CPH): cambia `port` en `tools/config.json` y agrégalo en Companion → Custom ports. (Si es otro `eda`, solo avisa que ya corre) |
| Companion no envía nada | Abre un problema **individual** (no la lista del concurso), recarga la página y revisa que el listener siga corriendo |
| `el portapapeles no parece el enunciado de este problema` | Estás en otra página o copiaste otra cosa: en la página del problema, Ctrl+A, Ctrl+C. `--forzar` si es correcto |
| `no tengo el enunciado` | Copia el enunciado (Ctrl+A, Ctrl+C) y repite el comando |
| `motor A falló … límite de uso` | Sigue solo con el motor B. Si no hay respaldo, espera el reinicio de tu cupo |
| `no hay respaldo: falta la clave del motor B` | Configúralo (PRIVADO.md) para tener respaldo |
| `no encuentro el motor A` / `sin sesión iniciada` | Ver PRIVADO.md |
| `clave del motor B inválida` | Revisa `tools/claves.env` (sin espacios ni comillas de más) |
| `no salió: los tests siguen fallando` | Lee `entrega/<slug>/w/log.md`; prueba `--nueva-sesion`, `--effort xhigh` o `--intentos 6` |
| El hilo se confunde | `--nueva-sesion` |
| VS Code subraya `plantillas` en rojo | Ctrl+Shift+P → "Java: Clean Java Language Server Workspace" → Restart |
| La tarea automática no arranca | Ctrl+Shift+P → "Tasks: Manage Automatic Tasks" → Allow, o usa `.\eda` en una terminal |

Notas: el tiempo que muestra `eda test` incluye el arranque de la JVM (~100 ms). La comparación es por
tokens (ignora espacios y saltos de línea extra, tolera 1e-6 en reales y avisa si solo difieren
mayúsculas). Problemas con varias respuestas válidas o interactivos no se pueden verificar con igualdad.

Para practicar sin navegador y validar el flujo completo, sigue **[PRUEBA_VSCODE.md](PRUEBA_VSCODE.md)**.
