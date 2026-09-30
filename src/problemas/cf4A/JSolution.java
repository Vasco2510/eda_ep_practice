package problemas.cf4A;

import plantillas.FastScanner;

import java.io.*;
import java.util.*;

/*
 * A. Watermelon
 * https://codeforces.com/problemset/problem/4/A
 * Límites: 1000 ms, 64 MB
 *
 * Para usar una plantilla escribe su nombre (ej. PersistentStack) y deja que el IDE agregue
 * "import plantillas.PersistentStack;". Si borras el import, desaparece de entrega/cf4A/Main.java.
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
        int w = in.nextInt();
        out.println(w % 2 == 0 && w > 2 ? "YES" : "NO");
    }

}
