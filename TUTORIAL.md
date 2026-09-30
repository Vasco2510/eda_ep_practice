# Asistente EDA — Tutorial

Tú programas en **W** (`JSolution.java`, un archivo Java normal que tu IDE compila y autocompleta).
El sistema genera **F** (`Main.java`, un solo archivo con tu lógica + el código de las plantillas que
importaste). **F es lo que envías a Codeforces.** Nunca editas F.

```
Competitiva/
├── src/plantillas/          plantillas (paquete `plantillas`). Se incrustan en F solo si W las importa
│   ├── FastScanner.java
│   ├── PersistentSegmentTree.java        suma + update puntual + k-ésimo
│   ├── PersistentLazySegmentTree.java    suma en rango + update en rango
│   ├── PersistentArray.java              arreglo persistente genérico (segment tree por debajo)
│   ├── PersistentTrie.java               trie de strings (count, countPrefix)
│   ├── PersistentBinaryTrie.java         trie de bits (max/min XOR, k-ésimo en rango)
│   ├── PersistentStack.java
│   ├── PersistentQueue.java
│   ├── PersistentTreap.java              BST balanceado (insert, erase, rank, kth, floor, ceiling)
│   ├── PersistentFibonacciHeap.java      min-heap perezoso (sin decreaseKey)
│   └── PersistentLeftistHeap.java        min-heap, O(log n) garantizado
├── src/problemas/<slug>/    uno por problema
│   ├── JSolution.java       ← W: aquí trabajas
│   ├── tests/               *.in / *.out (muestras de Competitive Companion + los tuyos)
│   └── problem.json         nombre, URL y límites del problema
├── entrega/<slug>/Main.java ← F: se genera solo. Esto se envía
├── tools/eda.py             el asistente (render, listener, tests)
├── tools/JSolution.template plantilla de W para cada problema nuevo (edítala a tu gusto)
├── tests/PlantillasTest.java verificación de las plantillas contra fuerza bruta
├── borradores/              tus archivos anteriores (no compilaban; los saqué de src/)
└── eda.cmd                  atajo: `.\eda test` en lugar de `python tools/eda.py test`
```

## Comandos

| Comando | Qué hace |
|---|---|
| `.\eda` | Deja corriendo el listener de Competitive Companion + re-render en vivo de W → F |
| `.\eda test` | Genera F, lo compila y lo corre con cada `tests/*.in`. Muestra OK / WA / RE / TLE con diff |
| `.\eda test --copy` | Igual, y si todo pasa copia F al portapapeles |
| `.\eda copy` | Copia F al portapapeles |
| `.\eda render` | Genera F una vez (el listener ya lo hace solo) |
| `.\eda new <slug>` | Crea un problema a mano (sin Competitive Companion) |
| `.\eda use <slug>` / `.\eda list` | Cambia / lista el problema actual |
| `.\eda selftest` | Verifica todas las plantillas (~420 mil comprobaciones contra fuerza bruta) |
| `.\eda demo` | Crea o reinicia el problema de práctica `demo_pila` |

Sin `<slug>`, los comandos usan el **problema actual**: el último que llegó por Competitive Companion
o el que elegiste con `eda use`. En la terminal de VS Code o IntelliJ (PowerShell) se escribe `.\eda`.
(No lo llamé `cp` porque en PowerShell `cp` es `Copy-Item`.)

---

## 1. Preparación (una sola vez, antes del examen)

1. **Competitive Companion**: instala la extensión en tu navegador. No hay que configurar nada: por
   defecto envía los problemas al puerto **27121**, que es donde escucha `eda`.
   (Si algún día instalas la extensión CPH de VS Code, usa ese mismo puerto: cambia `"port"` en
   `tools/config.json` y agrégalo en Competitive Companion → *Custom ports*.)
2. **Verifica las plantillas**: `.\eda selftest` → debe terminar en `OK: todas las plantillas pasaron`.
3. **IDE** (elige uno):
   - **IntelliJ**: abre la carpeta `Competitiva`. Arriba, en el selector de ejecución, aparecen
     `EDA iniciar`, `EDA test`, `EDA test y copiar` y `EDA copiar` (vienen de `.run/`; usan el plugin
     *Shell Script*, que ya trae IntelliJ). Elige `EDA test` y ejecútalo con **Shift+F10**.
   - **VS Code**: abre la carpeta `Competitiva`. La tarea `EDA: iniciar` arranca sola al abrir la
     carpeta (la primera vez VS Code pregunta si permites tareas automáticas: di que sí).
     **Ctrl+Shift+P → "Tasks: Run Test Task"** corre `EDA: test`. Si quieres atajos, agrega esto a tu
     `keybindings.json` (Ctrl+Shift+P → "Preferences: Open Keyboard Shortcuts (JSON)"):
     ```json
     { "key": "ctrl+alt+t", "command": "workbench.action.tasks.runTask", "args": "EDA: test" },
     { "key": "ctrl+alt+c", "command": "workbench.action.tasks.runTask", "args": "EDA: test + copiar si pasa" }
     ```

## 2. Flujo en el examen

1. Abre el IDE y deja corriendo **`.\eda`** (IntelliJ: `EDA iniciar`; en VS Code arranca solo).
2. En Codeforces, clic en el botón de **Competitive Companion**. En la terminal verás
   `▶ A. Nombre del problema`, y se crea `src/problemas/cf<concurso><letra>/JSolution.java` con los tests.
   Si el problema ya existía, **tu código no se toca**: solo se actualizan los tests.
3. Abre ese `JSolution.java` y escribe la lógica en `solve()`. La lectura ya está lista:
   `in.nextInt()`, `in.nextLong()`, `in.nextIntArray(n)`, `in.nextLongArray1(n)` (1-indexado),
   `in.nextLine()`; escribe con `out.println(...)`. Si hay varios casos, descomenta `t = in.nextInt()`.
4. ¿Necesitas una estructura persistente? Escribe su nombre (`PersistentSegmentTree`…) y acepta el
   auto-import del IDE (IntelliJ: **Alt+Enter**; VS Code: **Ctrl+.**), o escribe
   `import plantillas.PersistentSegmentTree;`. **Borra el import y la estructura desaparece de F.**
5. **`.\eda test`**. Cuando todo esté en verde: **`.\eda copy`** (o `test --copy`) y pega en Codeforces.
   Si subes archivo en vez de pegar, sube `entrega/<slug>/Main.java`.

Tus propios casos de prueba: crea `tests/mio1.in` y `tests/mio1.out` en la carpeta del problema.
Si creas solo el `.in`, `eda test` te muestra la salida sin comparar.

Para depurar W en el IDE: ejecútalo directamente (tiene su propio `main`). En IntelliJ, en la
configuración de ejecución marca *Redirect input from* → `tests/sample1.in`.

## 3. Uso rápido de las plantillas

Todas usan **versiones con id entero**: cada operación que modifica devuelve el id de la versión
nueva y las anteriores no cambian. La versión 0 es la estructura vacía (o `build(...)` para los segment trees).

```java
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

// Arreglo persistente de cualquier tipo, índices [0, n-1]
PersistentArray<Integer> arr = new PersistentArray<>(n, 0);      // o new PersistentArray<>(Integer[] a)
int a1v = arr.set(0, pos, x);  arr.get(a1v, pos);  arr.get(0, pos);

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

**Sobre el Fibonacci heap persistente**: un Fibonacci heap clásico necesita punteros al padre y
cortes en cascada para `decreaseKey`, y eso no se puede compartir entre versiones. La versión
persistente implementa insert/merge perezosos y consolidación por grado en `extractMin`, sin
`decreaseKey`. Si el problema repite `extractMin` sobre versiones viejas, usa `PersistentLeftistHeap`,
que da O(log n) garantizado. **Si tu profesor definió la estructura de otra forma, adapta esta plantilla.**
Si el problema **no** pide persistencia en el heap (el profesor acepta usar la "STL"), usa directamente
`java.util.PriorityQueue` (min-heap; para max-heap: `new PriorityQueue<>(Comparator.reverseOrder())`).

**Memoria del `PersistentTrie`**: guarda 26 hijos por nodo, así que 10^6 caracteres insertados en total
ocupan unos 110 MB. Si el problema tiene muchos caracteres, reduce `ALPHA` o usa el trie binario.

### Agregar o modificar plantillas
Crea `src/plantillas/Nombre.java` con `package plantillas;` y **una** clase `public class Nombre`
declarada en la columna 0 (como las existentes). El render le quita el `public` y la pega al final de F.
Si una plantilla usa otra, la incluye sola (dependencias transitivas). Después corre `.\eda selftest`.

---

## 4. Recorrido de prueba (para que valides el flujo)

Hazlo en orden y marca cada paso. Si algo no sale como dice "Esperado", anótalo y lo ajustamos.

**A. Plantillas**
- [ ] `.\eda selftest` → Esperado: `OK: todas las plantillas pasaron (418812 comprobaciones)`.

**B. Resolver la demo con una plantilla** (sin navegador)
- [ ] `.\eda demo` → crea `src/problemas/demo_pila/` (lee `enunciado.md` ahí mismo).
- [ ] `.\eda test` sin escribir nada → Esperado: `0/3 tests OK` (los tests existen y fallan).
- [ ] Resuelve el problema en `solve()` usando `PersistentStack` con el auto-import del IDE.
      (Si te trabas, la solución está en `tools/demo/solucion_referencia.java.txt`.)
- [ ] `.\eda test` → Esperado: `3/3 tests OK`; `grande3` (2·10⁵ operaciones) debería tardar menos de ~1 s.
- [ ] Abre `entrega/demo_pila/Main.java` → Esperado: la línea 2 dice
      `Plantillas incluidas: FastScanner, PersistentStack` y al final está el código de la pila.

**C. Render en vivo**
- [ ] Deja corriendo `.\eda` y abre `entrega/demo_pila/Main.java` en una pestaña al lado.
- [ ] En W agrega `import plantillas.PersistentQueue;` y guarda → en ~1 s aparece `PersistentQueue` en F.
- [ ] Borra ese import y guarda → desaparece de F.

**D. Competitive Companion real** (con `.\eda` corriendo)
- [ ] Abre https://codeforces.com/problemset/problem/1262/D2 y haz clic en la extensión.
      Esperado: en la terminal `▶ D2. Optimal Subsequences (Hard Version)` y aparece
      `src/problemas/cf1262D2/` con `tests/sample1.in`, `sample1.out`, etc.
      (Es un buen ejercicio de segment tree persistente: `kth` sobre versiones.)
- [ ] Haz clic otra vez en la extensión → Esperado: dice "ya existía: tu código se conserva".

**E. Envío**
- [ ] Resuelve la demo o el D2, `.\eda test --copy`, y pega en *Submit* de Codeforces (lenguaje Java 21).
      Esperado: compila en Codeforces sin tocar nada (una sola clase `public class Main`).

**F. Tus propios casos**
- [ ] Crea `tests/mio1.in` sin `.out` → `.\eda test` muestra `? --  mio1` con tu salida.

**Qué me puedes reportar para ajustar**: pasos que te sobran, nombres de comandos que prefieras,
métodos que le falten a las plantillas, cómo prefieres que se vean los errores, etc.

---

## 5. Problemas conocidos
- El tiempo que muestra `eda test` incluye el arranque de la JVM (~100 ms). Solo es una referencia.
- `eda test` compara por tokens: ignora espacios y saltos de línea extra, tolera 1e-6 en números
  reales y avisa (sin fallar) si solo difieren mayúsculas (YES/yes). Problemas con varias respuestas
  válidas o interactivos no se pueden verificar con igualdad: revisa la salida a mano.
- Si IntelliJ subraya en rojo `plantillas.*`: verifica que `src` esté marcado como *Sources Root*.
