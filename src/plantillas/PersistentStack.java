package plantillas;

import java.util.*;

/**
 * Pila persistente (lista enlazada inmutable, nodos compartidos entre versiones).
 * Todas las operaciones son O(1). Cada operación que modifica crea una versión nueva y devuelve su id.
 * La versión 0 es la pila vacía.
 *
 *   PersistentStack<Long> s = new PersistentStack<>();
 *   int v1 = s.push(0, 5L);      // versión 1: [5]
 *   int v2 = s.push(v1, 7L);     // versión 2: [5, 7]
 *   int v3 = s.pop(v2);          // versión 3: [5]
 *   s.peek(v2) -> 7 ; s.size(v3) -> 1 ; s.peek(0) -> null
 *
 * Patrón típico de examen: "la operación i se aplica sobre la versión t_i":
 *   int[] ver = new int[q + 1];  ver[i] = s.push(ver[t], x);
 */
public class PersistentStack<T> {
    static final class Node<T> {
        final T val;
        final Node<T> next;
        final int size;
        Node(T val, Node<T> next) {
            this.val = val;
            this.next = next;
            this.size = next == null ? 1 : next.size + 1;
        }
    }

    private final ArrayList<Node<T>> heads = new ArrayList<>();

    public PersistentStack() { heads.add(null); } // versión 0 = vacía

    /** Nueva versión = versión ver + x en el tope. */
    public int push(int ver, T x) { return newVersion(new Node<>(x, heads.get(ver))); }

    /** Nueva versión = versión ver sin su tope (si estaba vacía, sigue vacía). */
    public int pop(int ver) {
        Node<T> h = heads.get(ver);
        return newVersion(h == null ? null : h.next);
    }

    /** Tope de la versión ver, o null si está vacía. */
    public T peek(int ver) {
        Node<T> h = heads.get(ver);
        return h == null ? null : h.val;
    }

    public int size(int ver) {
        Node<T> h = heads.get(ver);
        return h == null ? 0 : h.size;
    }

    public boolean isEmpty(int ver) { return heads.get(ver) == null; }

    /** Copia exacta de una versión (útil si el problema pide "volver a la versión k" como nueva versión). */
    public int copy(int ver) { return newVersion(heads.get(ver)); }

    /** Cantidad de versiones creadas (incluye la 0). La última es versions() - 1. */
    public int versions() { return heads.size(); }

    /** Elementos de la versión, del tope al fondo. O(size). */
    public List<T> toList(int ver) {
        ArrayList<T> out = new ArrayList<>();
        for (Node<T> h = heads.get(ver); h != null; h = h.next) out.add(h.val);
        return out;
    }

    private int newVersion(Node<T> head) {
        heads.add(head);
        return heads.size() - 1;
    }
}
