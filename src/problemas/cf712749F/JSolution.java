package problemas.cf712749F;

import plantillas.FastScanner;
import plantillas.PersistentSegmentTree;

import java.io.*;
import java.util.*;

/*
 * F. Rollback
 * https://codeforces.com/group/apQ6meuqNq/contest/712749/problem/F
 * Límites: 3000 ms, 256 MB
 *
 * Para usar una plantilla escribe su nombre (ej. PersistentStack) y deja que el IDE agregue
 * "import plantillas.PersistentStack;". Si borras el import, desaparece de entrega/cf712749F/Main.java.
 */
public class JSolution {
    static FastScanner in = new FastScanner();
    static PrintWriter out = new PrintWriter(new BufferedOutputStream(System.out));

    public static void main(String[] args) {
        int t = 1;
        // t = in.nextInt(); // descomenta si el problema trae varios casos de prueba
        while (t-- > 0)
            solve();
        out.flush();
    }

    static void solve() {
        int n = in.nextInt();
        int m = in.nextInt();
        int[] a = new int[n + 2];
        for (int i = 1; i <= n; i++)
            a[i] = in.nextInt();

        PersistentSegmentTree t = new PersistentSegmentTree(1, n, 4000000);
        int[] root = new int[n + 2];
        int[] next = new int[m + 2];
        root[n + 1] = 0;
        for (int l = n; l >= 1; l--) {
            int r = root[l + 1];
            if (next[a[l]] != 0) {
                r = t.add(r, next[a[l]], -1);
            }
            r = t.add(r, l, 1);
            next[a[l]] = l;
            root[l] = r;
        }

        int q = in.nextInt();
        long p = 0;
        for (int i = 0; i < q; i++) {
            long x = in.nextLong();
            long y = in.nextLong();
            int l = (int) ((x + p) % n) + 1;
            int k = (int) ((y + p) % m) + 1;
            int ans;
            if (k > n) {
                ans = 0;
            } else {
                ans = t.kth(0, root[l], k);
                if (ans < 0)
                    ans = 0;
            }
            out.println(ans);
            p = ans;
        }
    }

}
