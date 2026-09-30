# cf712749I
motor: A · enunciado: portapapeles, verificado: contiene «D-Query» (guardado en enunciado.md)

## intento 1

Es el mismo problema D-Query, y el W que pegas ya tiene mi solución. La reviso de nuevo y no encuentro nada que cambiar, así que la dejo igual.

**Idea:** recorro `r` de 1 a `n` y construyo `root[r]`, un segment tree persistente donde vale 1 solo en la última aparición de cada valor dentro de `a[1..r]`.

- Al procesar `r`, si `a[r]` ya apareció en la posición `last`, hago `add(last, -1)`. Después hago `add(r, +1)`.
- La respuesta a la consulta `(i, j)` es `query(root[j], i, j)`. Cuenta los valores cuya última aparición en el prefijo `j` cae en `[i, j]`. Eso es exactamente una vez por valor distinto de `a[i..j]`.

**Complejidad:** O((n + q) log n). Son unos 2·30000·16 ≈ 1M nodos, que caben en la capacidad inicial de 1.2M. Las 200000 consultas son O(log n) cada una, con lectura y escritura rápidas.

```java
package problemas.cf712749I;

import plantillas.FastScanner;
import plantillas.PersistentSegmentTree;

import java.io.*;
import java.util.*;

/*
 * I. D-Query
 * https://codeforces.com/group/apQ6meuqNq/contest/712749/problem/I
 * Límites: 1000 ms, 256 MB
 */
public class JSolution {
    static FastScanner in = new FastScanner();
    static PrintWriter out = new PrintWriter(new BufferedOutputStream(System.out));

    public static void main(String[] args) {
        int t = 1;
        while (t-- > 0) solve();
        out.flush();
    }

    static void solve() {
        int n = in.nextInt();
        int[] a = new int[n + 1];
        for (int i = 1; i <= n; i++) a[i] = in.nextInt();

        PersistentSegmentTree tree = new PersistentSegmentTree(1, n, 1200000);
        int[] root = new int[n + 1];
        int[] last = new int[1000001];
        root[0] = 0;
        for (int r = 1; r <= n; r++) {
            int cur = root[r - 1];
            if (last[a[r]] != 0) {
                cur = tree.add(cur, last[a[r]], -1);
            }
            cur = tree.add(cur, r, 1);
            last[a[r]] = r;
            root[r] = cur;
        }

        int q = in.nextInt();
        for (int k = 0; k < q; k++) {
            int i = in.nextInt();
            int j = in.nextInt();
            out.println(tree.query(root[j], i, j));
        }
    }
}
```

_unidades: entrada 3393 (+23710 de caché), salida 955_

### resultado del intento 1

```
✓ OK  sample1 (92 ms)
1/1 tests OK  → entrega\cf712749I\Main_w.java
```

