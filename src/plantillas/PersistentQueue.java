package plantillas;

import java.util.*;

/**
 * Cola persistente. Todas las versiones comparten un árbol de nodos: cada push cuelga un nodo nuevo
 * del "tail" de la versión; una versión es (tail, profundidad del front). El front se obtiene con
 * binary lifting (ancestro de tail a esa profundidad).
 *   push / pop / size: O(log n) (por construir la tabla de saltos) ; peek: O(log n).
 * La versión 0 es la cola vacía.
 *
 *   PersistentQueue<Long> q = new PersistentQueue<>();
 *   int v1 = q.push(0, 1L);   // [1]
 *   int v2 = q.push(v1, 2L);  // [1, 2]
 *   int v3 = q.pop(v2);       // [2]
 *   q.peek(v2) -> 1 ; q.peek(v3) -> 2 ; q.size(v3) -> 1
 */
public class PersistentQueue<T> {
    static final int LOG = 20; // soporta hasta 2^20 (~10^6) pushes; subir a 21-22 si hace falta

    // nodos del árbol (el nodo 0 es la raíz centinela, profundidad 0)
    private final ArrayList<T> val = new ArrayList<>();
    private int[] depth = new int[1 << 10];
    private int[][] up = new int[LOG][1 << 10];
    private int nodes = 1;

    // versiones
    private int[] vTail = new int[1 << 10];   // nodo del último elemento
    private int[] vFront = new int[1 << 10];  // profundidad del primer elemento
    private int vers = 1;

    public PersistentQueue() {
        val.add(null);
        vTail[0] = 0;
        vFront[0] = 1;
    }

    /** Nueva versión = versión ver con x al final. */
    public int push(int ver, T x) {
        int t = vTail[ver];
        int id = newNode(t, x);
        return newVersion(id, vFront[ver]);
    }

    /** Nueva versión = versión ver sin su primer elemento (si estaba vacía, sigue vacía). */
    public int pop(int ver) {
        if (isEmpty(ver)) return newVersion(vTail[ver], vFront[ver]);
        return newVersion(vTail[ver], vFront[ver] + 1);
    }

    /** Primer elemento de la versión, o null si está vacía. */
    public T peek(int ver) {
        if (isEmpty(ver)) return null;
        return val.get(ancestorAtDepth(vTail[ver], vFront[ver]));
    }

    /** Último elemento de la versión, o null si está vacía. */
    public T back(int ver) { return isEmpty(ver) ? null : val.get(vTail[ver]); }

    public int size(int ver) { return Math.max(0, depth[vTail[ver]] - vFront[ver] + 1); }

    public boolean isEmpty(int ver) { return size(ver) == 0; }

    public int copy(int ver) { return newVersion(vTail[ver], vFront[ver]); }

    public int versions() { return vers; }

    /** Elementos de la versión, del front al back. O(size). */
    public List<T> toList(int ver) {
        ArrayList<T> out = new ArrayList<>();
        int s = size(ver);
        for (int u = vTail[ver], i = 0; i < s; i++, u = up[0][u]) out.add(val.get(u));
        Collections.reverse(out);
        return out;
    }

    private int ancestorAtDepth(int u, int d) {
        int k = depth[u] - d;
        for (int j = 0; k > 0; j++, k >>= 1) if ((k & 1) != 0) u = up[j][u];
        return u;
    }

    private int newNode(int parent, T x) {
        if (nodes == depth.length) {
            int cap = nodes * 2;
            depth = Arrays.copyOf(depth, cap);
            for (int j = 0; j < LOG; j++) up[j] = Arrays.copyOf(up[j], cap);
        }
        int id = nodes++;
        val.add(x);
        depth[id] = depth[parent] + 1;
        up[0][id] = parent;
        for (int j = 1; j < LOG; j++) up[j][id] = up[j - 1][up[j - 1][id]];
        return id;
    }

    private int newVersion(int tail, int front) {
        if (vers == vTail.length) {
            vTail = Arrays.copyOf(vTail, vers * 2);
            vFront = Arrays.copyOf(vFront, vers * 2);
        }
        vTail[vers] = tail;
        vFront[vers] = front;
        return vers++;
    }
}
