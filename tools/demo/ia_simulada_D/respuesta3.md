Idea: max-heap con la plantilla persistente (claves negadas).
```java
package cualquiera.mal.puesto;

import plantillas.FastScanner;
import plantillas.PersistentLeftistHeap;
import java.io.*;
import java.util.*;

public class JSolution {
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
```
