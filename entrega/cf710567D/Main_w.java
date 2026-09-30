// Plantillas incluidas: FastScanner, PersistentLeftistHeap
import java.io.*;
import java.util.*;

public class Main {
    static FastScanner in = new FastScanner();
    static PrintWriter out = new PrintWriter(new BufferedOutputStream(System.out));
    public static void main(String[] args) {
        int t = in.nextInt();
        while (t-- > 0) solve();
        out.flush();
    }
    static void solve() {
        int n = in.nextInt(); long ans = 0; PersistentLeftistHeap h = new PersistentLeftistHeap(); int v = 0;
        for (int i = 0; i < n; i++) { long s = in.nextLong(); if (s > 0) v = h.insert(v, -s); else if (!h.isEmpty(v)) { ans -= h.minKey(v); v = h.extractMin(v); } }
        out.println(ans);
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

// ============ plantilla: PersistentLeftistHeap ============
/**
 * Leftist heap persistente (MIN-heap): el heap persistente "de manual" para competitiva.
 * insert / merge / extractMin: O(log n) GARANTIZADO en cualquier versión (copia solo el camino derecho).
 *
 * Versión 0 = heap vacío. Para max-heap inserta -key.
 *   PersistentLeftistHeap h = new PersistentLeftistHeap();
 *   int v1 = h.insert(0, 5, 0);  int v2 = h.insert(v1, 3, 1);
 *   h.minKey(v2) -> 3 ; int v3 = h.extractMin(v2); int v4 = h.merge(v1, v3);
 */
class PersistentLeftistHeap {
    static final class Node {
        final long key;
        final int id, rank;
        final Node left, right;
        Node(long key, int id, Node left, Node right) {
            int rl = left == null ? 0 : left.rank, rr = right == null ? 0 : right.rank;
            if (rl < rr) { Node t = left; left = right; right = t; }
            this.key = key; this.id = id; this.left = left; this.right = right;
            this.rank = Math.min(rl, rr) + 1;
        }
    }

    private final ArrayList<Node> roots = new ArrayList<>();
    private final ArrayList<Integer> sizes = new ArrayList<>();

    public PersistentLeftistHeap() { roots.add(null); sizes.add(0); }

    public int insert(int ver, long key) { return insert(ver, key, -1); }

    public int insert(int ver, long key, int id) {
        return add(meld(roots.get(ver), new Node(key, id, null, null)), sizes.get(ver) + 1);
    }

    public int merge(int a, int b) { return add(meld(roots.get(a), roots.get(b)), sizes.get(a) + sizes.get(b)); }

    public long minKey(int ver) { return roots.get(ver).key; }

    public int minId(int ver) { return roots.get(ver).id; }

    public int size(int ver) { return sizes.get(ver); }

    public boolean isEmpty(int ver) { return roots.get(ver) == null; }

    public int extractMin(int ver) {
        Node r = roots.get(ver);
        if (r == null) return add(null, 0);
        return add(meld(r.left, r.right), sizes.get(ver) - 1);
    }

    public int versions() { return roots.size(); }

    private static Node meld(Node a, Node b) {
        if (a == null) return b;
        if (b == null) return a;
        if (b.key < a.key) { Node t = a; a = b; b = t; }
        return new Node(a.key, a.id, a.left, meld(a.right, b));
    }

    private int add(Node root, int size) {
        roots.add(root);
        sizes.add(size);
        return roots.size() - 1;
    }
}
