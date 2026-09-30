# cf715162A
motor: A

## intento 1

Este es el mismo problema de antes, y el archivo que pegas ya tiene mi solución. La reviso de nuevo y no encuentro nada que cambiar. Repito la explicación y el archivo completo.

**Idea:** cuento los puntos de la caja `[l1,r1] × [l2,r2]` con un segment tree persistente. Cuesta O(log n) por consulta, igual que el range tree con fractional cascading que pide el enunciado.

1. Ordeno los puntos por `x` y comprimo las `y` a rangos `1..m`.
2. La versión `pre[i]` es el árbol de frecuencias sobre `y` con los primeros `i` puntos por `x`.
3. Para cada consulta, dos búsquedas binarias sobre `xs` dan `lo` (los puntos con `x < l1`) y `hi` (los puntos con `x ≤ r1`). Otras dos sobre las `y` comprimidas dan `vl` y `vr`.
4. La respuesta es `countBetween(pre[lo], pre[hi], vl, vr)`, o 0 si `lo ≥ hi` o `vl > vr`.

**Por qué es correcta:** `pre[hi] − pre[lo]` contiene exactamente los puntos con `x` en `[l1,r1]`. Los empates en `x` quedan bien, porque `lowerBound` y `upperBound` toman todos los puntos con esa `x`. Luego cuento los que tienen `y` en `[l2,r2]`. Las coordenadas caben en `int` (|v| ≤ 10^9).

**Complejidad:** O(n log n) de preprocesamiento y memoria, y O(log n) por consulta.

```java
package problemas.cf715162A;

import plantillas.FastScanner;
import plantillas.PersistentSegmentTree;

import java.io.*;
import java.util.*;

/*
 * A. Efecto cascada (Grupo 1)
 * https://codeforces.com/group/apQ6meuqNq/contest/715162/problem/A
 * Límites: 5000 ms, 512 MB
 */
public class JSolution {
    static FastScanner in = new FastScanner();
    static PrintWriter out = new PrintWriter(new BufferedOutputStream(System.out));

    public static void main(String[] args) {
        int t = 1;
        while (t-- > 0) solve();
        out.flush();
    }

    // cantidad de elementos < v en arr ordenado
    static int lowerBound(int[] arr, int v) {
        int lo = 0, hi = arr.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (arr[mid] < v) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }

    // cantidad de elementos <= v en arr ordenado
    static int upperBound(int[] arr, int v) {
        int lo = 0, hi = arr.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (arr[mid] <= v) lo = mid + 1;
            else hi = mid;
        }
        return lo;
    }

    static void solve() {
        int n = in.nextInt();
        int q = in.nextInt();
        int[] px = new int[n];
        int[] py = new int[n];
        for (int i = 0; i < n; i++) {
            px[i] = in.nextInt();
            py[i] = in.nextInt();
        }
        Integer[] idx = new Integer[n];
        for (int i = 0; i < n; i++) idx[i] = i;
        Arrays.sort(idx, (u, v) -> Integer.compare(px[u], px[v]));

        int[] xs = new int[n];
        for (int i = 0; i < n; i++) xs[i] = px[idx[i]];

        int[] sortedY = py.clone();
        Arrays.sort(sortedY);
        int m = 0;
        int[] ys = new int[n];
        for (int i = 0; i < n; i++) {
            if (i == 0 || sortedY[i] != sortedY[i - 1]) ys[m++] = sortedY[i];
        }
        ys = Arrays.copyOf(ys, m);

        PersistentSegmentTree tree = new PersistentSegmentTree(1, m);
        int[] pre = new int[n + 1];
        pre[0] = 0;
        for (int i = 1; i <= n; i++) {
            int rk = lowerBound(ys, py[idx[i - 1]]) + 1;
            pre[i] = tree.add(pre[i - 1], rk, 1);
        }

        for (int i = 0; i < q; i++) {
            int l1 = in.nextInt();
            int r1 = in.nextInt();
            int l2 = in.nextInt();
            int r2 = in.nextInt();
            int lo = lowerBound(xs, l1);
            int hi = upperBound(xs, r1);
            int vl = lowerBound(ys, l2) + 1;
            int vr = upperBound(ys, r2);
            long ans = 0;
            if (lo < hi && vl <= vr) {
                ans = tree.countBetween(pre[lo], pre[hi], vl, vr);
            }
            out.println(ans);
        }
    }
}
```

_tokens: entrada 7148 (+13480 de caché), salida 1946_

### resultado del intento 1

```
✓ OK  sample1 (71 ms)
1/1 tests OK  → entrega\cf715162A\Main_ia.java
```

