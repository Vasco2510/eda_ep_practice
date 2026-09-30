// Plantillas incluidas: FastScanner, PersistentSegmentTree
import java.io.*;
import java.util.*;

/*
 * A. Efecto cascada (Grupo 1)
 * https://codeforces.com/group/apQ6meuqNq/contest/715162/problem/A
 * Límites: 5000 ms, 512 MB
 */
public class Main {
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

// ============ plantilla: FastScanner ============
/**
 * Lectura rápida de stdin (tu plantilla original + helpers para arrays).
 * Uso:  FastScanner in = new FastScanner();  int n = in.nextInt();  long[] a = in.nextLongArray(n);
 */
class FastScanner {
    BufferedReader br = new BufferedReader(new InputStreamReader(System.in), 1 << 16);
    StringTokenizer st = new StringTokenizer("");

    public String next() {
        while (!st.hasMoreTokens()) {
            try {
                String line = br.readLine();
                if (line == null) return null;
                st = new StringTokenizer(line);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        return st.nextToken();
    }

    public int nextInt() { return Integer.parseInt(next()); }
    public long nextLong() { return Long.parseLong(next()); }
    public double nextDouble() { return Double.parseDouble(next()); }

    /** Resto de la línea actual (o la siguiente línea completa si no quedan tokens). */
    public String nextLine() {
        try {
            if (st.hasMoreTokens()) {
                StringBuilder sb = new StringBuilder(st.nextToken());
                while (st.hasMoreTokens()) sb.append(' ').append(st.nextToken());
                return sb.toString();
            }
            return br.readLine();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public int[] nextIntArray(int n) {
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = nextInt();
        return a;
    }

    public long[] nextLongArray(int n) {
        long[] a = new long[n];
        for (int i = 0; i < n; i++) a[i] = nextLong();
        return a;
    }

    /** Array 1-indexado: a[1..n], a[0] = 0 (útil para segment trees sobre [1, n]). */
    public long[] nextLongArray1(int n) {
        long[] a = new long[n + 1];
        for (int i = 1; i <= n; i++) a[i] = nextLong();
        return a;
    }
}

// ============ plantilla: PersistentSegmentTree ============
/**
 * Segment Tree persistente (path copying) con pool de nodos en arrays.
 * Suma en rango + actualización puntual. Cada update devuelve la raíz de una
 * NUEVA versión,
 * la versión anterior queda intacta.
 *
 * Nodo 0 = nodo nulo (suma 0): la raíz 0 representa un árbol lleno de ceros sin
 * haber llamado build.
 *
 * PersistentSegmentTree t = new PersistentSegmentTree(1, n);
 * int[] root = new int[q + 1];
 * root[0] = t.build(a); // a indexado en [lo, hi] (o root[0] = 0 si todo
 * empieza en 0)
 * root[1] = t.set(root[0], pos, val); // versión 1
 * long s = t.query(root[1], l, r); // suma en [l, r] de la versión 1
 *
 * k-ésimo menor en subarreglo a[l..r] (clásico): comprimir valores a [1..m],
 * raíces por prefijo
 * pre[i] = t.add(pre[i-1], comp(a[i]), 1); ans = t.kth(pre[l-1], pre[r], k) ->
 * índice comprimido.
 *
 * Memoria: O(n + q log n) nodos; los arrays crecen solos.
 */
class PersistentSegmentTree {
    public final int lo, hi;
    long[] sum;
    int[] L, R;
    int cnt = 0; // nodos usados (el 0 es el nulo)

    public PersistentSegmentTree(int lo, int hi) {
        this(lo, hi, 1 << 20);
    }

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
    public int build(long[] arr) {
        return build(arr, lo, hi);
    }

    private int build(long[] arr, int l, int r) {
        int id = newNode(0);
        if (l == r) {
            sum[id] = arr[l];
            return id;
        }
        int m = (l + r) >> 1;
        int a = build(arr, l, m), b = build(arr, m + 1, r);
        L[id] = a;
        R[id] = b;
        sum[id] = sum[a] + sum[b];
        return id;
    }

    /** Nueva versión con a[pos] = val. */
    public int set(int root, int pos, long val) {
        return update(root, lo, hi, pos, val, false);
    }

    /** Nueva versión con a[pos] += delta. */
    public int add(int root, int pos, long delta) {
        return update(root, lo, hi, pos, delta, true);
    }

    private int update(int prev, int l, int r, int pos, long v, boolean additive) {
        int id = newNode(prev);
        if (l == r) {
            sum[id] = additive ? sum[id] + v : v;
            return id;
        }
        int m = (l + r) >> 1;
        if (pos <= m) {
            int c = update(L[prev], l, m, pos, v, additive);
            L[id] = c;
        } else {
            int c = update(R[prev], m + 1, r, pos, v, additive);
            R[id] = c;
        }
        sum[id] = sum[L[id]] + sum[R[id]];
        return id;
    }

    /** Suma de [ql, qr] en la versión root. */
    public long query(int root, int ql, int qr) {
        return query(root, lo, hi, ql, qr);
    }

    private long query(int node, int l, int r, int ql, int qr) {
        if (node == 0 || qr < l || r < ql)
            return 0;
        if (ql <= l && r <= qr)
            return sum[node];
        int m = (l + r) >> 1;
        return query(L[node], l, m, ql, qr) + query(R[node], m + 1, r, ql, qr);
    }

    /**
     * Valor en la posición pos de la versión root (sirve como "array persistente").
     */
    public long get(int root, int pos) {
        return query(root, pos, pos);
    }

    /**
     * k-ésima posición (1-indexado) con peso acumulado, usando la diferencia de
     * versiones
     * (rootR - rootL). Con árboles de frecuencias por prefijo da el k-ésimo menor
     * de a[l..r].
     * Devuelve -1 si hay menos de k elementos.
     */
    public int kth(int rootL, int rootR, long k) {
        if (sum[rootR] - sum[rootL] < k)
            return -1;
        int l = lo, r = hi;
        while (l < r) {
            int m = (l + r) >> 1;
            long leftCount = sum[L[rootR]] - sum[L[rootL]];
            if (k <= leftCount) {
                rootL = L[rootL];
                rootR = L[rootR];
                r = m;
            } else {
                k -= leftCount;
                rootL = R[rootL];
                rootR = R[rootR];
                l = m + 1;
            }
        }
        return l;
    }

    /**
     * Cantidad de elementos con valor comprimido en [vl, vr] entre las versiones
     * rootL y rootR.
     */
    public long countBetween(int rootL, int rootR, int vl, int vr) {
        return query(rootR, vl, vr) - query(rootL, vl, vr);
    }

}
