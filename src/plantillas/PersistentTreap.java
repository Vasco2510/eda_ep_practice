package plantillas;

import java.util.*;

/**
 * BST persistente balanceado (treap con path copying). Multiconjunto ordenado de long con versiones.
 * insert / erase / contains / rank / kth / floor / ceiling: O(log n) esperado. La versión 0 es vacía.
 *
 *   PersistentTreap t = new PersistentTreap();
 *   int v1 = t.insert(0, 5);  int v2 = t.insert(v1, 2);  int v3 = t.erase(v2, 5);
 *   t.contains(v2, 5) -> true ; t.contains(v3, 5) -> false
 *   t.kth(v2, 1) -> 2 (1-indexado) ; t.rank(v2, 5) -> 1 (cuántos < 5) ; t.size(v2) -> 2
 *   t.floor(v2, 4) -> 2 ; t.ceiling(v2, 3) -> 5 (Long.MIN_VALUE / Long.MAX_VALUE si no hay)
 */
public class PersistentTreap {
    static final class Node {
        final long key;
        final int pri, size;
        final Node left, right;
        Node(long key, int pri, Node left, Node right) {
            this.key = key; this.pri = pri; this.left = left; this.right = right;
            this.size = 1 + sz(left) + sz(right);
        }
    }

    static int sz(Node t) { return t == null ? 0 : t.size; }

    private final SplittableRandom rnd = new SplittableRandom(20260930);
    private final ArrayList<Node> roots = new ArrayList<>();

    public PersistentTreap() { roots.add(null); }

    // split en (< key, >= key), copiando solo el camino recorrido
    private static Node[] split(Node t, long key) {
        if (t == null) return new Node[]{null, null};
        if (t.key < key) {
            Node[] p = split(t.right, key);
            return new Node[]{new Node(t.key, t.pri, t.left, p[0]), p[1]};
        }
        Node[] p = split(t.left, key);
        return new Node[]{p[0], new Node(t.key, t.pri, p[1], t.right)};
    }

    private static Node merge(Node a, Node b) {
        if (a == null) return b;
        if (b == null) return a;
        if (a.pri > b.pri) return new Node(a.key, a.pri, a.left, merge(a.right, b));
        return new Node(b.key, b.pri, merge(a, b.left), b.right);
    }

    /** Nueva versión con key agregado (se permiten repetidos). */
    public int insert(int ver, long key) {
        Node[] p = split(roots.get(ver), key);
        return add(merge(merge(p[0], new Node(key, rnd.nextInt(), null, null)), p[1]));
    }

    /** Nueva versión sin UNA ocurrencia de key (si no está, copia de la versión). */
    public int erase(int ver, long key) { return add(erase(roots.get(ver), key)); }

    private static Node erase(Node t, long key) {
        if (t == null) return null;
        if (t.key == key) return merge(t.left, t.right);
        if (key < t.key) {
            Node l = erase(t.left, key);
            return l == t.left ? t : new Node(t.key, t.pri, l, t.right);
        }
        Node r = erase(t.right, key);
        return r == t.right ? t : new Node(t.key, t.pri, t.left, r);
    }

    public boolean contains(int ver, long key) {
        for (Node t = roots.get(ver); t != null; t = key < t.key ? t.left : t.right)
            if (t.key == key) return true;
        return false;
    }

    public int size(int ver) { return sz(roots.get(ver)); }

    /** Cantidad de elementos < key. */
    public int rank(int ver, long key) {
        int r = 0;
        for (Node t = roots.get(ver); t != null; ) {
            if (t.key < key) { r += sz(t.left) + 1; t = t.right; } else t = t.left;
        }
        return r;
    }

    /** Cantidad de elementos == key. */
    public int count(int ver, long key) {
        return key == Long.MAX_VALUE ? size(ver) - rank(ver, key) : rank(ver, key + 1) - rank(ver, key);
    }

    /** k-ésimo menor, 1-indexado. Lanza excepción si k está fuera de [1, size]. */
    public long kth(int ver, int k) {
        Node t = roots.get(ver);
        if (k < 1 || k > sz(t)) throw new IndexOutOfBoundsException("kth: k=" + k + " size=" + sz(t));
        while (true) {
            int ls = sz(t.left);
            if (k <= ls) t = t.left;
            else if (k == ls + 1) return t.key;
            else { k -= ls + 1; t = t.right; }
        }
    }

    /** Mayor elemento <= key, o Long.MIN_VALUE si no hay. */
    public long floor(int ver, long key) {
        long best = Long.MIN_VALUE;
        for (Node t = roots.get(ver); t != null; ) {
            if (t.key <= key) { best = t.key; t = t.right; } else t = t.left;
        }
        return best;
    }

    /** Menor elemento >= key, o Long.MAX_VALUE si no hay. */
    public long ceiling(int ver, long key) {
        long best = Long.MAX_VALUE;
        for (Node t = roots.get(ver); t != null; ) {
            if (t.key >= key) { best = t.key; t = t.left; } else t = t.right;
        }
        return best;
    }

    public int copy(int ver) { return add(roots.get(ver)); }

    public int versions() { return roots.size(); }

    /** Elementos en orden. O(n). */
    public List<Long> toList(int ver) {
        ArrayList<Long> out = new ArrayList<>();
        ArrayDeque<Node> st = new ArrayDeque<>();
        Node t = roots.get(ver);
        while (t != null || !st.isEmpty()) {
            while (t != null) { st.push(t); t = t.left; }
            t = st.pop();
            out.add(t.key);
            t = t.right;
        }
        return out;
    }

    private int add(Node root) {
        roots.add(root);
        return roots.size() - 1;
    }
}
