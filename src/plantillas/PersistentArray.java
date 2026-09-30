package plantillas;

import java.util.*;

/**
 * Arreglo persistente de cualquier tipo, implementado como segment tree con path copying
 * (solo las hojas guardan valores). get / set: O(log n). Cada set devuelve el id de una versión nueva.
 * La versión 0 es el arreglo inicial.
 *
 *   PersistentArray<Integer> pa = new PersistentArray<>(n, 0);      // n posiciones [0, n-1] con valor 0
 *   PersistentArray<Long> pb = new PersistentArray<>(arr);           // desde un arreglo T[] (índices 0..n-1)
 *   int v1 = pa.set(0, 3, 42);   // versión 1: a[3] = 42
 *   pa.get(v1, 3) -> 42 ; pa.get(0, 3) -> 0
 *
 * Ejemplo de uso típico: DSU persistente (parent[] y rank[] como PersistentArray).
 */
public class PersistentArray<T> {
    public final int n;
    int[] L, R;
    Object[] val;
    int cnt = 0;
    private int[] roots = new int[16];
    private int vers = 0;

    public PersistentArray(int n, T init) {
        this.n = n;
        alloc(4 * n + 16);
        addVersion(build(0, n - 1, null, init));
    }

    public PersistentArray(T[] arr) {
        this.n = arr.length;
        alloc(4 * n + 16);
        addVersion(build(0, n - 1, arr, null));
    }

    private void alloc(int cap) {
        L = new int[cap];
        R = new int[cap];
        val = new Object[cap];
    }

    private int newNode() {
        if (++cnt == L.length) {
            int cap = L.length * 2;
            L = Arrays.copyOf(L, cap);
            R = Arrays.copyOf(R, cap);
            val = Arrays.copyOf(val, cap);
        }
        return cnt;
    }

    private int build(int l, int r, T[] arr, T init) {
        int id = newNode();
        if (l == r) { val[id] = arr == null ? init : arr[l]; return id; }
        int m = (l + r) >> 1;
        int a = build(l, m, arr, init), b = build(m + 1, r, arr, init);
        L[id] = a; R[id] = b;
        return id;
    }

    /** Valor a[pos] en la versión ver. */
    @SuppressWarnings("unchecked")
    public T get(int ver, int pos) {
        int node = roots[ver], l = 0, r = n - 1;
        while (l < r) {
            int m = (l + r) >> 1;
            if (pos <= m) { node = L[node]; r = m; } else { node = R[node]; l = m + 1; }
        }
        return (T) val[node];
    }

    /** Nueva versión = versión ver con a[pos] = x. Devuelve su id. */
    public int set(int ver, int pos, T x) { return addVersion(set(roots[ver], 0, n - 1, pos, x)); }

    private int set(int prev, int l, int r, int pos, T x) {
        int id = newNode();
        if (l == r) { val[id] = x; return id; }
        int m = (l + r) >> 1;
        if (pos <= m) { int c = set(L[prev], l, m, pos, x); L[id] = c; R[id] = R[prev]; }
        else { int c = set(R[prev], m + 1, r, pos, x); L[id] = L[prev]; R[id] = c; }
        return id;
    }

    /** Copia exacta de una versión (O(1)). */
    public int copy(int ver) { return addVersion(roots[ver]); }

    public int versions() { return vers; }

    private int addVersion(int root) {
        if (vers == roots.length) roots = Arrays.copyOf(roots, vers * 2);
        roots[vers] = root;
        return vers++;
    }
}
