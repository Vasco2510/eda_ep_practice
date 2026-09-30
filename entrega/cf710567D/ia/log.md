# IA — cf710567D
proveedor: claude-code · modelo: (modelo de tu plan) · enunciado: enunciado.pdf

## intento 1

## Idea

Cuando aparece un héroe, puedo decidir que la bonificación que usa sea **cualquiera** de las que ya salieron y que todavía no se usaron. La razón: si descarto todas las bonificaciones que llegaron después de esa, la que quiero queda encima del mazo.

Por eso sale una estrategia voraz:
- Cada bonificación que aparece se guarda en un **max-heap**.
- Cuando llega un héroe (carta con valor 0), si el heap no está vacío, saco el máximo y lo sumo a la respuesta.

**Por qué es correcta (argumento de intercambio):**
- Los héroes se procesan en orden. El héroe *j* solo puede usar bonificaciones que aparecieron antes que él.
- Supongamos que una solución óptima le da al héroe actual una bonificación *b* menor que el máximo disponible *M*.
  - Si *M* se usa después en otro héroe *h*, intercambiamos *b* y *M* entre los dos. Sigue siendo válido, porque ambas cartas aparecieron antes que los dos héroes, y la suma no cambia.
  - Si *M* no se usa, cambiar *b* por *M* no empeora la suma.
- Falta ver que el orden de uso se puede lograr con el mazo (pila). Para cada héroe se apilan solo las bonificaciones que se van a usar. Como cada héroe consume la carta de encima, esa carta es exactamente la que le toca: con emparejamientos anidados entre bonificaciones y héroes siempre se puede lograr, y cualquier conjunto de emparejamientos válido se puede reordenar para que quede anidado sin cambiar la suma.

**Uso de la plantilla:** `PersistentLeftistHeap` es un min-heap, así que para tener un max-heap inserto `-s`. Guardo solo la versión actual `v`. Cada `insert` o `extractMin` devuelve una versión nueva. Al empezar cada caso de prueba vuelvo a la versión 0 (heap vacío), sin reconstruir nada.

**Complejidad:** O(n log n) por caso, con suma de n ≤ 2·10⁵. Cada operación copia O(log n) nodos, así que la memoria es de unos pocos millones de nodos y cabe en 256 MB. La recursión de `meld` tiene profundidad O(log n) (camino derecho del leftist heap), así que no hay riesgo de desbordar la pila. La respuesta puede llegar a unos 2·10¹⁴, por eso se usa `long`.

```java
package problemas.cf710567D;

import plantillas.FastScanner;
import plantillas.PersistentLeftistHeap;

import java.io.*;
import java.util.*;

/*
 * D. Ejercito supremo
 * https://codeforces.com/group/apQ6meuqNq/contest/710567/problem/D
 * Límites: 2000 ms, 256 MB
 *
 * Para usar una plantilla escribe su nombre (ej. PersistentStack) y deja que el IDE agregue
 * "import plantillas.PersistentStack;". Si borras el import, desaparece de entrega/cf710567D/Main.java.
 */
public class JSolution {
    static FastScanner in = new FastScanner();
    static PrintWriter out = new PrintWriter(new BufferedOutputStream(System.out));
    static PersistentLeftistHeap heap = new PersistentLeftistHeap();

    public static void main(String[] args) {
        int t = 1;
        t = in.nextInt();
        while (t-- > 0) solve();
        out.flush();
    }

    static void solve() {
        int n = in.nextInt();
        int v = 0; // versión 0 = heap vacío
        long ans = 0;
        for (int i = 0; i < n; i++) {
            long s = in.nextLong();
            if (s > 0) {
                v = heap.insert(v, -s); // max-heap con claves negadas
            } else if (!heap.isEmpty(v)) {
                ans += -heap.minKey(v);
                v = heap.extractMin(v);
            }
        }
        out.println(ans);
    }
}
```

Con los ejemplos da 6, 6, 8, 9 y 4; los revisé a mano y aún no he corrido `.\eda test`. Pruébalo para confirmar.

### resultado del intento 1

```
✓ OK  sample1 (70 ms)
✓ OK  grande2 (187 ms)
✓ OK  stress1 (74 ms)
3/3 tests OK  → entrega\cf710567D\Main_ia.java
```

