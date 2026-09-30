Idea (equivocada a propósito): cada héroe toma la última bonificación vista.
```java
package problemas.cf710567D;

import plantillas.FastScanner;
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
        int n = in.nextInt(); long last = 0, ans = 0;
        for (int i = 0; i < n; i++) { long s = in.nextLong(); if (s > 0) last = s; else { ans += last; last = 0; } }
        out.println(ans);
    }
}
```
