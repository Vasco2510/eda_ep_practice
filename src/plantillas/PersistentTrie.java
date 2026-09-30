package plantillas;

import java.util.*;

/**
 * Trie persistente de strings (alfabeto 'a'..'z'; cambia ALPHA y la función idx para otro alfabeto).
 * Cada insert/erase copia solo el camino de la palabra: O(|s|). La versión 0 es el trie vacío.
 * Es multiconjunto: insertar dos veces la misma palabra la cuenta dos veces.
 *
 *   PersistentTrie t = new PersistentTrie();
 *   int v1 = t.insert(0, "abc");
 *   int v2 = t.insert(v1, "abd");
 *   t.count(v2, "abc") -> 1 ; t.countPrefix(v2, "ab") -> 2 ; t.countPrefix(v1, "ab") -> 1
 *   int v3 = t.erase(v2, "abc");  // si la palabra no está, v3 es copia de v2
 *
 * Para XOR máximo en rango usa PersistentBinaryTrie.
 */
public class PersistentTrie {
    static final int ALPHA = 26;

    static int idx(char ch) { return ch - 'a'; }

    int[][] next = new int[ALPHA][1 << 16];
    int[] end = new int[1 << 16];   // palabras que terminan en el nodo
    int[] pass = new int[1 << 16];  // palabras que pasan por el nodo (tamaño del subárbol)
    int cnt = 0;                    // el nodo 0 es el nulo
    private int[] roots = new int[16];
    private int vers = 0;

    public PersistentTrie() { addVersion(0); }

    private int clone(int from) {
        if (++cnt == end.length) {
            int cap = end.length * 2;
            for (int c = 0; c < ALPHA; c++) next[c] = Arrays.copyOf(next[c], cap);
            end = Arrays.copyOf(end, cap);
            pass = Arrays.copyOf(pass, cap);
        }
        for (int c = 0; c < ALPHA; c++) next[c][cnt] = next[c][from];
        end[cnt] = end[from];
        pass[cnt] = pass[from];
        return cnt;
    }

    public int insert(int ver, String s) { return addVersion(change(roots[ver], s, +1)); }

    /** Borra UNA ocurrencia de s (si no existe, devuelve una copia de la versión). */
    public int erase(int ver, String s) {
        if (count(ver, s) == 0) return copy(ver);
        return addVersion(change(roots[ver], s, -1));
    }

    private int change(int root, String s, int d) {
        int newRoot = clone(root), cur = newRoot;
        pass[cur] += d;
        for (int i = 0; i < s.length(); i++) {
            int c = idx(s.charAt(i));
            int child = clone(next[c][cur]);
            next[c][cur] = child;
            cur = child;
            pass[cur] += d;
        }
        end[cur] += d;
        return newRoot;
    }

    /** Veces que s fue insertada (y no borrada) en la versión ver. */
    public int count(int ver, String s) {
        int node = walk(roots[ver], s);
        return node == 0 ? 0 : end[node];
    }

    /** Cantidad de palabras de la versión ver que tienen a p como prefijo. */
    public int countPrefix(int ver, String p) {
        int node = walk(roots[ver], p);
        return node == 0 ? 0 : pass[node];
    }

    public int size(int ver) { return pass[roots[ver]]; }

    public int copy(int ver) { return addVersion(roots[ver]); }

    public int versions() { return vers; }

    private int walk(int node, String s) {
        for (int i = 0; i < s.length() && node != 0; i++) node = next[idx(s.charAt(i))][node];
        return node;
    }

    private int addVersion(int root) {
        if (vers == roots.length) roots = Arrays.copyOf(roots, vers * 2);
        roots[vers] = root;
        return vers++;
    }
}
