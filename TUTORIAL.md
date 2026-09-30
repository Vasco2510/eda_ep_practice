# Asistente EDA — Tutorial (VS Code)

Tú trabajas en **W** (`JSolution.java`, un archivo Java normal con autocompletado). El sistema genera **F**
(`entrega/<slug>/Main.java`): tu lógica **más** el código de las plantillas que importaste, en un solo
archivo. **F es lo que se envía a Codeforces**; nunca se edita a mano.

Hay dos formas de llegar a la solución, y se pueden combinar:

| | Modo manual | Modo `work` (con IA) |
|---|---|---|
| Quién escribe `solve()` | Tú | La IA (Claude Sonnet 5.5; respaldo Groq) |
| Comando clave | `.\eda test` | `.\eda go` (todo) o `.\eda work` (tú pegas) |
| Qué se envía | `entrega/<slug>/Main.java` | `entrega/<slug>/Main.java` |

---

## 1. Flujo completo: del problema a Codeforces

### Paso 0 — Preparar (al abrir VS Code)
Abre la carpeta `Competitiva`. El listener de Competitive Companion **arranca solo** (VS Code puede
preguntar si permites tareas automáticas: di **Allow**). Si no arrancó, escribe `.\eda` en una
terminal y déjala abierta. Verás: `eda escuchando Competitive Companion en el puerto 27121`.
Para los demás comandos abre **otra** terminal (el `+` del panel).

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

#### Modo `work` (la IA escribe la solución)
1. En la **misma página del problema: Ctrl+A, Ctrl+C.** Copia el enunciado al portapapeles.
2. Elige cuánto quieres automatizar:

   | Comando | Qué hace | Después tú |
   |---|---|---|
   | **`.\eda go`** | La IA resuelve → aplica la solución a tu W → prueba tu W → copia `Main.java` | Pegas en Codeforces. **Terminaste** |
   | **`.\eda work`** | La IA resuelve y deja en el portapapeles solo lo que va en tu W (imports + `solve()`) | Pegas en `JSolution.java`, `.\eda test`, `.\eda copy` |
   | `.\eda work --completo` | La IA resuelve y deja `Main_ia.java` completo (sin pasar por tu W) | Pegas en Codeforces |

   Tarda entre 20 s y un par de minutos. Verás la explicación de la IA y cada intento con sus tests.
   **Solo entrega algo si pasa los tests de ejemplo** (hasta 4 intentos, corrigiéndose con el error).
3. Con `go` el flujo termina así:
   ```
   ✓ IA resolvió cf710567D en 1 intento(s), 22 s
   ✓ solución aplicada a tu W: src\problemas\cf710567D\JSolution.java
   ── probando tu W con los ejemplos ──
   ✓ OK  sample1 …          3/3 tests OK
   ✓ LISTO: entrega/cf710567D/Main.java está en el portapapeles → pégalo en Codeforces (Java 21)
   ```
   Si tu W ya tenía código, la IA lo guarda antes en `JSolution.HHMMSS.antes.txt` (junto a tu W).
4. Con `work` (modo "tú pegas"), el portapapeles trae tres cosas: el `import plantillas.…` (va arriba,
   con los otros imports), `solve()` con sus funciones auxiliares (reemplaza tu `solve()` vacío) y, si lo
   avisa, hay que descomentar `t = in.nextInt();` en `main()`.

**Obligar a usar una plantilla** (por ejemplo, en un simulacro donde se pide usar la persistencia):
`.\eda go --usar PersistentLeftistHeap`. Si la IA resuelve sin ella, el intento se rechaza.

### Paso 3 — Enviar
1. Si no lo hiciste ya: **`.\eda copy`** copia `entrega/<slug>/Main.java`.
   (Sin pasar por W, la solución de la IA está en `.\eda copy --work`.)
2. En Codeforces → **Submit Code** → Lenguaje **Java 21** → pega → Submit. Es un solo archivo con
   `public class Main`, sin `package` ni `import plantillas`.

### Resumen de una línea
```
Companion (clic)  →  [manual: escribe solve() → .\eda test]  o  [work: Ctrl+A, Ctrl+C → .\eda go]  →  .\eda copy  →  pegar en Codeforces
```

---

## 2. Comandos

Escríbelos en PowerShell dentro de `Competitiva` con el prefijo `.\eda`. Sin `[slug]` se usa el problema actual.

| Comando (atajo) | Qué hace |
|---|---|
| `.\eda` | Listener de Competitive Companion + re-render de F en vivo. Déjalo abierto |
| `.\eda go` | **Todo en uno con IA**: resuelve → aplica a tu W → prueba → copia `Main.java` |
| `.\eda work` (`w`) | La IA resuelve y deja en el portapapeles lo que va en tu W |
| `.\eda test` (`t`) | Genera F, lo compila y lo corre contra `tests/*.in`. Muestra OK / WA / RE / TLE con la diferencia |
| `.\eda test --copy` | Igual, y si todo pasa copia F al portapapeles |
| `.\eda copy` (`c`) | Copia `Main.java` al portapapeles |
| `.\eda render` (`r`) | Genera F una vez (el listener ya lo hace solo) |
| `.\eda new <slug>` | Crea un problema a mano (sin Competitive Companion) |
| `.\eda use <slug>` / `.\eda list` (`l`) | Cambia / lista los problemas |
| `.\eda uso` (`u`) | Tokens que gastó `work` en esta máquina + cuánto llevas usado de tu plan de Claude (§5) |
| `.\eda selftest` | Verifica todas las plantillas (~420 mil comprobaciones contra fuerza bruta) |
| `.\eda demo` | Crea o reinicia el problema de práctica `demo_pila` |

Opciones de `work` y `go`:

| Opción | Efecto |
|---|---|
| `--usar A,B` | Obliga a usar esas plantillas |
| `--aplicar` | (`work`) escribe la solución en tu W en vez de copiarla (es lo que hace `go`) |
| `--completo` | (`work`) copia `Main_ia.java` completo |
| `--clip` / `--forzar` | Exige el portapapeles como enunciado (ver §5); `--forzar` salta la verificación |
| `--nueva-sesion` | Abre una conversación nueva con Claude (por defecto continúa la anterior) |
| `--proveedor X`, `--modelo Y`, `--effort Z`, `--intentos N` | Elige proveedor (`claude-code`, `groq`, `anthropic`, `ollama`), modelo, esfuerzo y nº de intentos |
| `--ping` | Prueba la conexión con la IA con una solicitud mínima |
| `--uso` | Al terminar, muestra cuánto bajó tu plan por esta resolución (consulta `/usage` antes y después) |

(`--solve` y `--copy` siguen funcionando: son el modo por defecto de `work` y `--completo`.)

### Atajos en VS Code
**Ctrl+Shift+P → "Tasks: Run Task"** lista: *iniciar*, *go*, *work*, *test*, *test + copiar* y *copiar*.
*Tasks: Run Test Task* corre `EDA: test`. Para atajos de teclado, agrega esto a `keybindings.json`
(Ctrl+Shift+P → "Preferences: Open Keyboard Shortcuts (JSON)"):
```json
{ "key": "ctrl+alt+g", "command": "workbench.action.tasks.runTask", "args": "EDA: go (IA resuelve → aplica a tu W → prueba → copia Main.java)" },
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
│   ├── Main_ia.java         la solución de la IA renderizada (sin pasar por tu W)
│   └── ia/                  JSolution.java de la IA, solve.java.txt y log.md (explicación + intentos)
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
línea encima de cada método público. De ahí sale el manual que lee la IA (§5).

---

## 5. La IA (`work` / `go`) en detalle

### Qué proveedor usa
- **Principal:** Claude Sonnet 5.5 a través de **Claude Code**, con tu plan de Claude (sin API key ni costo aparte).
- **Respaldo automático: Groq (gratis).** Solo entra si Claude Code falla: no instalado, sin sesión, límite de
  uso alcanzado o cualquier error. Si pasas `--proveedor X` a mano, no hay respaldo.

### Cómo sabe qué plantillas hay y cómo usarlas
Se le envía un **manual** generado automáticamente desde `src/plantillas/` (~4 600 tokens; los archivos
completos serían ~13 600): para cada plantilla, qué es, cuándo usarla, un ejemplo y cada método público
con lo que hace, recibe y devuelve. **Nunca se le manda el código fuente.** Si agregas o modificas una
plantilla, el manual se actualiza solo en la siguiente ejecución.

### Sesión continua (como un chat)
Con Claude Code, cada problema **continúa la misma conversación** que el anterior: el manual queda en
caché (en la prueba: 465 tokens nuevos frente a 9 214 leídos de caché en el segundo problema) y la IA ya
conoce tus reglas. Los reintentos de un problema ven sus propios errores. Se abre sesión nueva sola si
cambian las plantillas o el modelo, cada 8 problemas, o con `--nueva-sesion` (úsalo si un problema
anterior confundió a la IA). Se guarda en `.eda_ia_session.json` (no se sube a git).

### El enunciado
Competitive Companion **no envía el enunciado**, solo los tests. `work`/`go` lo toman así:
1. **Del portapapeles, automáticamente,** solo si parece el enunciado **de este problema**: es texto largo
   con "Input/Output" (o Entrada/Salida), no es código, y **menciona el título** que envió Companion
   (p. ej. «Ejercito supremo»). Si no cumple, lo ignora y avisa (así no resuelve otro problema por error).
   `--clip` fuerza este modo y falla con un mensaje claro si no coincide; `--forzar` lo salta.
2. Si el portapapeles no sirve: `src/problemas/<slug>/enunciado.md` / `.txt` (donde se guardó la última
   vez) o un `.pdf` en esa carpeta. El PDF lo lee bien Claude; con Groq se extrae el texto y **se pierden
   fórmulas y variables** de PDFs impresos.
3. La URL del problema: solo funciona en el problemset público; en grupos privados Codeforces pide login.

### ¿Cuánto consumí y cuánto me queda?
Con Claude Code (tu plan) el límite no es en dinero ni en tokens exactos: Anthropic solo informa el
**porcentaje usado** de dos ventanas, la **sesión de 5 horas** y la **semana**, y cuándo se reinician.

| Qué quieres saber | Cómo |
|---|---|
| Tokens de **esa respuesta** | Cada llamada imprime `tokens: entrada N (+M de caché), salida K`. Al terminar, `work`/`go` suma la resolución: `consumo de esta resolución: …`. También queda en `entrega/<slug>/ia/log.md` |
| Cuánto **te queda del plan** | **`.\eda uso`** → `Sesión de 5 h: 44% usado → te queda ≈ 56% (se reinicia …)` y lo mismo para la semana |
| Cuánto **bajó el plan por una resolución** | `.\eda go --uso` (o `work --uso`): consulta `/usage` antes y después y muestra la diferencia en puntos |
| Directo con Claude, desde la terminal | `claude -p "/usage"` en **PowerShell** (en Git Bash la `/` se convierte en ruta y no funciona). Interactivo: `claude` y luego `/usage` (`d`/`w` cambian entre 24 h y 7 días; `--completo` en `eda uso` imprime todo el texto) |

Cómo leerlo:
- El porcentaje es de **toda tu cuenta** (claude.ai, Claude Code, otras conversaciones), no solo de `eda`.
  Una resolución típica pesa poco (la sesión con el manual en caché lee ~9 mil tokens de caché y escribe
  cientos); lo que más consume son las **conversaciones largas**, porque cada mensaje reenvía todo el
  historial. `/usage` marca ese efecto ("% de tu uso fue con >150k de contexto"): para tareas nuevas, abre
  una conversación nueva.
- El `≈ $` que imprime `work` es lo que costaría la misma llamada en la API de pago; con tu plan **no se
  cobra**, solo gasta de tus límites. Con Groq no se consume tu plan (tiene su propio límite diario).
- `--uso` tiene resolución de 1 punto y mide todo lo que pase en tu cuenta durante la resolución: úsalo
  sin otras conversaciones activas para que la diferencia sea fiel.
- Cuando se agota la sesión de 5 h, `work` sigue solo con Groq (respaldo). Los datos de consumo por
  llamada se guardan en `.eda_uso.jsonl` (no se sube a git).

### Configurar
**Claude Code (una vez):**
1. Instalar: `irm https://claude.ai/install.ps1 | iex` (PowerShell). Requiere plan Pro/Max/Team/Enterprise.
2. Abre una terminal nueva y comprueba: `claude --version`. Si no se reconoce, agrega
   `C:\Users\<tu usuario>\.local\bin` (la **carpeta**, no `claude.exe`) al PATH de usuario y reabre VS Code.
3. Iniciar sesión: `claude auth login` (se abre el navegador; usa tu cuenta de claude.ai). Comprueba con
   `claude auth status --text`.
4. Prueba: `.\eda work --ping` → `✓ el proveedor respondió: OK`.

**Groq (respaldo, gratis):**
1. Crea la clave en https://console.groq.com → **API Keys** → **Create API Key** (empieza con `gsk_`).
2. `Copy-Item tools\claves.env.example tools\claves.env`, abre `tools\claves.env` y deja una línea:
   `GROQ_API_KEY=gsk_tu_clave`. El archivo está en `.gitignore` (no se sube al repo).
   (Alternativa: `setx GROQ_API_KEY "gsk_..."` y reabrir VS Code.)
3. Prueba: `.\eda work --ping --proveedor groq`.
**Cuida la clave:** no la pegues en chats, commits ni capturas. Si se filtra, bórrala en *API Keys* y crea otra.
Límites del plan gratis (`openai/gpt-oss-120b`): 8 000 tokens/min y 200 000/día; si dice "espera N s", `eda`
espera solo. Con Groq las plantillas van en versión compacta.

**Ajustes permanentes** (`tools/config.json`, todos opcionales):
```json
{ "ia_proveedor": "claude-code", "ia_respaldo": "groq", "ia_modelo": "claude-sonnet-5-5",
  "ia_effort": "high", "ia_intentos": 4, "ia_max_problemas_sesion": 8 }
```
`ia_respaldo: null` desactiva el respaldo. `ia_effort`: `medium` es más rápido y gasta menos; `xhigh`/`max`
para problemas muy difíciles. Otros proveedores: `anthropic` (API de pago) y `ollama` (local, más débil).

**Ojo:** "pasa los tests" significa que pasa los **ejemplos** (y los tests que agregues en `tests/`). Puede
pasarlos y aun así ser incorrecta o lenta en Codeforces: lee la explicación en `entrega/<slug>/ia/log.md`.

---

## 6. Problemas comunes

| Síntoma | Qué hacer |
|---|---|
| `.\eda` no se reconoce | La terminal debe estar en `…\Competitiva` |
| "el puerto 27121 está ocupado" | Ya hay otra instancia de `eda` abierta (cierra la terminal vieja) o la extensión CPH |
| Companion no envía nada | Abre un problema **individual** (no la lista del concurso), recarga la página y revisa que el listener siga corriendo |
| `el portapapeles no parece el enunciado de este problema` | Estás en otra página o copiaste otra cosa: en la página del problema, Ctrl+A, Ctrl+C. `--forzar` si es correcto |
| `no tengo el enunciado` | Copia el enunciado (Ctrl+A, Ctrl+C) y repite el comando |
| `Claude Code falló … límite de uso` | Sigue solo con Groq. Si no hay respaldo, espera el reinicio de tu límite |
| `no hay respaldo: falta GROQ_API_KEY` | Configura Groq (§5) para tener respaldo |
| `no encuentro Claude Code` / `no has iniciado sesión` | §5: instalar y `claude auth login` |
| `GROQ_API_KEY inválida` | Revisa `tools/claves.env` (sin espacios ni comillas de más) |
| `la IA no logró pasar los tests` | Lee `entrega/<slug>/ia/log.md`; prueba `--nueva-sesion`, `--effort xhigh` o `--intentos 6` |
| La IA "olvida" reglas o se confunde | `--nueva-sesion` |
| VS Code subraya `plantillas` en rojo | Ctrl+Shift+P → "Java: Clean Java Language Server Workspace" → Restart |
| La tarea automática no arranca | Ctrl+Shift+P → "Tasks: Manage Automatic Tasks" → Allow, o usa `.\eda` en una terminal |

Notas: el tiempo que muestra `eda test` incluye el arranque de la JVM (~100 ms). La comparación es por
tokens (ignora espacios y saltos de línea extra, tolera 1e-6 en reales y avisa si solo difieren
mayúsculas). Problemas con varias respuestas válidas o interactivos no se pueden verificar con igualdad.

Para practicar sin navegador y validar el flujo completo, sigue **[PRUEBA_VSCODE.md](PRUEBA_VSCODE.md)**.
