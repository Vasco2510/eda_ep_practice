package plantillas;

import java.util.*;

/**
 * Segment Tree persistente con actualización en RANGO (suma a [l, r]) y consulta de suma en rango.
 * Técnica: lazy "permanente" (mark permanence) — el tag de un nodo nunca se empuja a los hijos,
 * así cada update solo copia O(log n) nodos y las versiones viejas no se tocan.
 *
 *   PersistentLazySegmentTree t = new PersistentLazySegmentTree(1, n);
 *   int v0 = t.build(a);                // o v0 = 0 (todo ceros)
 *   int v1 = t.rangeAdd(v0, l, r, x);   // nueva versión
 *   long s = t.query(v1, l, r);
 */
public class PersistentLazySegmentTree {
    public final int lo, hi;
    long[] sum, tag;
    int[] L, R;
    int cnt = 0; // el nodo 0 es el nulo

    public PersistentLazySegmentTree(int lo, int hi) { this(lo, hi, 1 << 20); }

    public PersistentLazySegmentTree(int lo, int hi, int initialCapacity) {
        this.lo = lo;
        this.hi = hi;
        sum = new long[initialCapacity];
        tag = new long[initialCapacity];
        L = new int[initialCapacity];
        R = new int[initialCapacity];
    }

    private int newNode(int copyFrom) {
        if (++cnt == sum.length) {
            int cap = sum.length * 2;
            sum = Arrays.copyOf(sum, cap);
            tag = Arrays.copyOf(tag, cap);
            L = Arrays.copyOf(L, cap);
            R = Arrays.copyOf(R, cap);
        }
        sum[cnt] = sum[copyFrom];
        tag[cnt] = tag[copyFrom];
        L[cnt] = L[copyFrom];
        R[cnt] = R[copyFrom];
        return cnt;
    }

    public int build(long[] arr) { return build(arr, lo, hi); }

    private int build(long[] arr, int l, int r) {
        int id = newNode(0);
        if (l == r) { sum[id] = arr[l]; return id; }
        int m = (l + r) >> 1;
        int a = build(arr, l, m), b = build(arr, m + 1, r);
        L[id] = a; R[id] = b;
        sum[id] = sum[a] + sum[b];
        return id;
    }

    /** Nueva versión con a[i] += v para todo i en [ql, qr]. */
    public int rangeAdd(int root, int ql, int qr, long v) { return rangeAdd(root, lo, hi, ql, qr, v); }

    private int rangeAdd(int prev, int l, int r, int ql, int qr, long v) {
        int id = newNode(prev);
        sum[id] += v * (Math.min(r, qr) - Math.max(l, ql) + 1);
        if (ql <= l && r <= qr) { tag[id] += v; return id; }
        int m = (l + r) >> 1;
        if (ql <= m) { int c = rangeAdd(L[prev], l, m, ql, qr, v); L[id] = c; }
        if (qr > m)  { int c = rangeAdd(R[prev], m + 1, r, ql, qr, v); R[id] = c; }
        return id;
    }

    /** Suma de [ql, qr] en la versión root. */
    public long query(int root, int ql, int qr) { return query(root, lo, hi, ql, qr, 0); }

    private long query(int node, int l, int r, int ql, int qr, long acc) {
        if (qr < l || r < ql) return 0;
        if (ql <= l && r <= qr) return sum[node] + acc * (r - l + 1);
        int m = (l + r) >> 1;
        long a = acc + tag[node];
        return query(L[node], l, m, ql, qr, a) + query(R[node], m + 1, r, ql, qr, a);
    }
}
