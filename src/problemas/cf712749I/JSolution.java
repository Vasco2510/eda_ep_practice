package problemas.cf712749I;

import plantillas.FastScanner;
import plantillas.PersistentSegmentTree;

import java.io.*;
import java.util.*;

/*
 * I. D-Query
 * https://codeforces.com/group/apQ6meuqNq/contest/712749/problem/I
 * Límites: 1000 ms, 256 MB
 */
public class JSolution {
    static FastScanner in = new FastScanner();
    static PrintWriter out = new PrintWriter(new BufferedOutputStream(System.out));

    public static void main(String[] args) {
        int t = 1;
        while (t-- > 0) solve();
        out.flush();
    }

    static void solve() {
        int n = in.nextInt();
        int[] a = new int[n + 1];
        for (int i = 1; i <= n; i++) a[i] = in.nextInt();

        PersistentSegmentTree tree = new PersistentSegmentTree(1, n, 1200000);
        int[] root = new int[n + 1];
        int[] last = new int[1000001];
        root[0] = 0;
        for (int r = 1; r <= n; r++) {
            int cur = root[r - 1];
            if (last[a[r]] != 0) {
                cur = tree.add(cur, last[a[r]], -1);
            }
            cur = tree.add(cur, r, 1);
            last[a[r]] = r;
            root[r] = cur;
        }

        int q = in.nextInt();
        for (int k = 0; k < q; k++) {
            int i = in.nextInt();
            int j = in.nextInt();
            out.println(tree.query(root[j], i, j));
        }
    }
}
