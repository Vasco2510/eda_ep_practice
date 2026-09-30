package problemas.cf710567D;

import plantillas.FastScanner;
import plantillas.PersistentLeftistHeap;

import java.io.*;
import java.util.*;

/*
 * D. Ejercito supremo
 * https://codeforces.com/group/apQ6meuqNq/contest/710567/problem/D
 * Límites: 2000 ms, 256 MB
 *
 * Para usar una plantilla escribe su nombre (ej. PersistentStack) y deja que el IDE agregue
 * "import plantillas.PersistentStack;". Si borras el import, desaparece de entrega/cf710567D/Main.java.
 */
public class JSolution {
    static FastScanner in = new FastScanner();
    static PrintWriter out = new PrintWriter(new BufferedOutputStream(System.out));
    static PersistentLeftistHeap heap = new PersistentLeftistHeap();

    public static void main(String[] args) {
        int t = 1;
        t = in.nextInt();
        while (t-- > 0) solve();
        out.flush();
    }

    static void solve() {
        int n = in.nextInt();
        int v = 0; // versión 0 = heap vacío
        long ans = 0;
        for (int i = 0; i < n; i++) {
            long s = in.nextLong();
            if (s > 0) {
                v = heap.insert(v, -s); // max-heap con claves negadas
            } else if (!heap.isEmpty(v)) {
                ans += -heap.minKey(v);
                v = heap.extractMin(v);
            }
        }
        out.println(ans);
    }
}
