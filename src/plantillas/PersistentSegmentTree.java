package plantillas;

import java.util.*;

/**
 * Segment Tree persistente (path copying) con pool de nodos en arrays.
 * Suma en rango + actualización puntual. Cada update devuelve la raíz de una NUEVA versión,
 * la versión anterior queda intacta.
 *
 * Nodo 0 = nodo nulo (suma 0): la raíz 0 representa un árbol lleno de ceros sin haber llamado build.
 *
 *   PersistentSegmentTree t = new PersistentSegmentTree(1, n);
 *   int[] root = new int[q + 1];
 *   root[0] = t.build(a);               // a indexado en [lo, hi]  (o root[0] = 0 si todo empieza en 0)
 *   root[1] = t.set(root[0], pos, val); // versión 1
 *   long s  = t.query(root[1], l, r);   // suma en [l, r] de la versión 1
 *
 * k-ésimo menor en subarreglo a[l..r] (clásico): comprimir valores a [1..m], raíces por prefijo
 *   pre[i] = t.add(pre[i-1], comp(a[i]), 1);  ans = t.kth(pre[l-1], pre[r], k)  -> índice comprimido.
 *
 * Memoria: O(n + q log n) nodos; los arrays crecen solos.
 */
public class PersistentSegmentTree {
    public final int lo, hi;
    long[] sum;
    int[] L, R;
    int cnt = 0; // nodos usados (el 0 es el nulo)

    public PersistentSegmentTree(int lo, int hi) { this(lo, hi, 1 << 20); }

    public PersistentSegmentTree(int lo, int hi, int initialCapacity) {
        this.lo = lo;
        this.hi = hi;
        sum = new long[initialCapacity];
        L = new int[initialCapacity];
        R = new int[initialCapacity];
    }

    private int newNode(int copyFrom) {
        if (++cnt == sum.length) {
            int cap = sum.length * 2;
            sum = Arrays.copyOf(sum, cap);
            L = Arrays.copyOf(L, cap);
            R = Arrays.copyOf(R, cap);
        }
        sum[cnt] = sum[copyFrom];
        L[cnt] = L[copyFrom];
        R[cnt] = R[copyFrom];
        return cnt;
    }

    /** Versión inicial a partir de arr (se usan las posiciones arr[lo..hi]). */
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

    /** Nueva versión con a[pos] = val. */
    public int set(int root, int pos, long val) { return update(root, lo, hi, pos, val, false); }

    /** Nueva versión con a[pos] += delta. */
    public int add(int root, int pos, long delta) { return update(root, lo, hi, pos, delta, true); }

    private int update(int prev, int l, int r, int pos, long v, boolean additive) {
        int id = newNode(prev);
        if (l == r) {
            sum[id] = additive ? sum[id] + v : v;
            return id;
        }
        int m = (l + r) >> 1;
        if (pos <= m) { int c = update(L[prev], l, m, pos, v, additive); L[id] = c; }
        else          { int c = update(R[prev], m + 1, r, pos, v, additive); R[id] = c; }
        sum[id] = sum[L[id]] + sum[R[id]];
        return id;
    }

    /** Suma de [ql, qr] en la versión root. */
    public long query(int root, int ql, int qr) { return query(root, lo, hi, ql, qr); }

    private long query(int node, int l, int r, int ql, int qr) {
        if (node == 0 || qr < l || r < ql) return 0;
        if (ql <= l && r <= qr) return sum[node];
        int m = (l + r) >> 1;
        return query(L[node], l, m, ql, qr) + query(R[node], m + 1, r, ql, qr);
    }

    /** Valor en la posición pos de la versión root (sirve como "array persistente"). */
    public long get(int root, int pos) { return query(root, pos, pos); }

    /**
     * k-ésima posición (1-indexado) con peso acumulado, usando la diferencia de versiones
     * (rootR - rootL). Con árboles de frecuencias por prefijo da el k-ésimo menor de a[l..r].
     * Devuelve -1 si hay menos de k elementos.
     */
    public int kth(int rootL, int rootR, long k) {
        if (sum[rootR] - sum[rootL] < k) return -1;
        int l = lo, r = hi;
        while (l < r) {
            int m = (l + r) >> 1;
            long leftCount = sum[L[rootR]] - sum[L[rootL]];
            if (k <= leftCount) { rootL = L[rootL]; rootR = L[rootR]; r = m; }
            else { k -= leftCount; rootL = R[rootL]; rootR = R[rootR]; l = m + 1; }
        }
        return l;
    }

    /** Cantidad de elementos con valor comprimido en [vl, vr] entre las versiones rootL y rootR. */
    public long countBetween(int rootL, int rootR, int vl, int vr) {
        return query(rootR, vl, vr) - query(rootL, vl, vr);
    }
}
