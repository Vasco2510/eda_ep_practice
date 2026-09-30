package plantillas;

import java.util.*;

/**
 * Fibonacci Heap persistente (MIN-heap) en versión funcional: los nodos son inmutables y se comparten
 * entre versiones. Igual que el Fibonacci heap clásico: insert/merge son "perezosos" (solo agregan
 * a la lista de raíces) y extractMin consolida uniendo árboles del mismo grado.
 *
 *   insert O(1), min O(1), merge O(min(#raíces)), extractMin O(#raíces + log n)
 *   NO hay decreaseKey (requiere punteros al padre y cortes en cascada, incompatibles con compartir nodos).
 *   Ojo: las cotas amortizadas del Fibonacci heap no valen si repites extractMin sobre la MISMA versión
 *   vieja muchas veces; si eso pasa usa PersistentLeftistHeap (O(log n) garantizado).
 *
 * Versión 0 = heap vacío. Para max-heap inserta -key.
 *   PersistentFibonacciHeap h = new PersistentFibonacciHeap();
 *   int v1 = h.insert(0, 5, 0);   // (key, id)  id = dato extra opcional (índice, nodo del grafo, ...)
 *   int v2 = h.insert(v1, 3, 1);
 *   h.minKey(v2) -> 3 ; int v3 = h.extractMin(v2) ; h.minKey(v3) -> 5 ; h.minKey(v1) -> 5
 */
public class PersistentFibonacciHeap {
    static final class Tree {
        final long key;
        final int id, degree;
        final Cons children;
        Tree(long key, int id, int degree, Cons children) {
            this.key = key; this.id = id; this.degree = degree; this.children = children;
        }
    }

    static final class Cons {
        final Tree head;
        final Cons tail;
        Cons(Tree head, Cons tail) { this.head = head; this.tail = tail; }
    }

    static final class Version {
        final Cons roots;
        final Tree min;
        final int size, rootCount;
        Version(Cons roots, Tree min, int size, int rootCount) {
            this.roots = roots; this.min = min; this.size = size; this.rootCount = rootCount;
        }
    }

    private final ArrayList<Version> vs = new ArrayList<>();

    public PersistentFibonacciHeap() { vs.add(new Version(null, null, 0, 0)); }

    public int insert(int ver, long key) { return insert(ver, key, -1); }

    public int insert(int ver, long key, int id) {
        Version v = vs.get(ver);
        Tree t = new Tree(key, id, 0, null);
        Tree mn = (v.min == null || key < v.min.key) ? t : v.min;
        return add(new Version(new Cons(t, v.roots), mn, v.size + 1, v.rootCount + 1));
    }

    /** Nueva versión = unión de las versiones a y b (ambas siguen existiendo). */
    public int merge(int a, int b) {
        Version x = vs.get(a), y = vs.get(b);
        if (x.rootCount < y.rootCount) { Version t = x; x = y; y = t; }
        Cons roots = x.roots;
        for (Cons c = y.roots; c != null; c = c.tail) roots = new Cons(c.head, roots);
        Tree mn = x.min == null ? y.min : (y.min == null || x.min.key <= y.min.key ? x.min : y.min);
        return add(new Version(roots, mn, x.size + y.size, x.rootCount + y.rootCount));
    }

    /** Clave mínima (lanza excepción si está vacío: verifica isEmpty antes). */
    public long minKey(int ver) { return vs.get(ver).min.key; }

    /** id asociado al mínimo. */
    public int minId(int ver) { return vs.get(ver).min.id; }

    public int size(int ver) { return vs.get(ver).size; }

    public boolean isEmpty(int ver) { return vs.get(ver).size == 0; }

    /** Nueva versión sin el mínimo (si está vacío, devuelve una copia vacía). */
    public int extractMin(int ver) {
        Version v = vs.get(ver);
        if (v.size == 0) return add(v);
        // grados posibles <= log_phi(n) + 2
        Tree[] byDegree = new Tree[64];
        boolean skipped = false;
        for (Cons c = v.roots; c != null; c = c.tail) {
            if (!skipped && c.head == v.min) { skipped = true; continue; }
            byDegree = place(byDegree, c.head);
        }
        for (Cons c = v.min.children; c != null; c = c.tail) byDegree = place(byDegree, c.head);

        Cons roots = null;
        Tree mn = null;
        int rc = 0;
        for (Tree t : byDegree) {
            if (t == null) continue;
            roots = new Cons(t, roots);
            rc++;
            if (mn == null || t.key < mn.key) mn = t;
        }
        return add(new Version(roots, mn, v.size - 1, rc));
    }

    public int versions() { return vs.size(); }

    private static Tree[] place(Tree[] byDegree, Tree t) {
        while (true) {
            if (t.degree >= byDegree.length) byDegree = Arrays.copyOf(byDegree, t.degree * 2);
            Tree o = byDegree[t.degree];
            if (o == null) { byDegree[t.degree] = t; return byDegree; }
            byDegree[t.degree] = null;
            t = link(t, o);
        }
    }

    private static Tree link(Tree a, Tree b) {
        if (b.key < a.key) { Tree t = a; a = b; b = t; }
        return new Tree(a.key, a.id, a.degree + 1, new Cons(b, a.children));
    }

    private int add(Version v) {
        vs.add(v);
        return vs.size() - 1;
    }
}
