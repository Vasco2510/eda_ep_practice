# cf712749F
motor: A

## intento 1

**Idea:** proceso `l` de `n` a 1 y mantengo un segment tree persistente por versión. En la versión `l`, la posición `r` vale 1 si `r` es la primera aparición de `a[r]` en el sufijo que empieza en `l`, y 0 en otro caso. Entonces la suma de la versión `l` sobre `[l, r]` es la cantidad de valores distintos en `a[l..r]`.

**Construcción:** parto de `root[l+1]`. Si el valor `a[l]` aparecía antes en `next[a[l]] = j`, pongo 0 en `j` con `add(-1)`. Luego pongo 1 en `l` con `add(+1)`. Cada paso copia O(log n) nodos.

**Consulta:** el mínimo `r` con al menos `k` distintos es la k-ésima posición con peso 1, y eso es `kth(0, root[l], k)`. Uso la raíz 0, que es el árbol vacío, como límite izquierdo. Esas posiciones son todas ≥ l, porque la versión `l` solo tiene unos en posiciones ≥ l. Si hay menos de `k` unos, `kth` devuelve -1 y la respuesta es 0. También pongo 0 directamente si `k > n`. Después `p = r`.

**Complejidad:** O((n + q) log n) en tiempo y unos 2n·17 ≈ 3.4M nodos en memoria, que caben en 256 MB.

```java
package problemas.cf712749F;

import plantillas.FastScanner;
import plantillas.PersistentSegmentTree;

import java.io.*;
import java.util.*;

/*
 * F. Rollback
 * https://codeforces.com/group/apQ6meuqNq/contest/712749/problem/F
 * Límites: 3000 ms, 256 MB
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
        int m = in.nextInt();
        int[] a = new int[n + 2];
        for (int i = 1; i <= n; i++) a[i] = in.nextInt();

        PersistentSegmentTree t = new PersistentSegmentTree(1, n, 4000000);
        int[] root = new int[n + 2];
        int[] next = new int[m + 2];
        root[n + 1] = 0;
        for (int l = n; l >= 1; l--) {
            int r = root[l + 1];
            if (next[a[l]] != 0) {
                r = t.add(r, next[a[l]], -1);
            }
            r = t.add(r, l, 1);
            next[a[l]] = l;
            root[l] = r;
        }

        int q = in.nextInt();
        long p = 0;
        for (int i = 0; i < q; i++) {
            long x = in.nextLong();
            long y = in.nextLong();
            int l = (int) ((x + p) % n) + 1;
            int k = (int) ((y + p) % m) + 1;
            int ans;
            if (k > n) {
                ans = 0;
            } else {
                ans = t.kth(0, root[l], k);
                if (ans < 0) ans = 0;
            }
            out.println(ans);
            p = ans;
        }
    }
}
```

### resultado del intento 1

```
✓ OK  sample1 (92 ms)
1/1 tests OK  → entrega\cf712749F\Main_ia.java
```

