
// GENERADO desde src/problemas/cf4A/JSolution.java — no edites este archivo, edita W.
// Plantillas incluidas: FastScanner
import java.io.*;
import java.util.*;

import plantillas.PersistentStack;

/*
 * A. Watermelon
 * https://codeforces.com/problemset/problem/4/A
 * Límites: 1000 ms, 64 MB
 *
 * Para usar una plantilla escribe su nombre (ej. PersistentStack) y deja que el IDE agregue
 * "import plantillas.PersistentStack;". Si borras el import, desaparece de entrega/cf4A/Main.java.
 */
public class Main {
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
        // int w = in.nextInt();
        // out.println(w % 2 == 0 && w > 2 ? "YES" : "NO");

        PersistentStack<Integer> stp = new PersistentStack<>();
    }

}

// ============ plantilla: FastScanner ============
/**
 * Lectura rápida de stdin (tu plantilla original + helpers para arrays).
 * Uso: FastScanner in = new FastScanner(); int n = in.nextInt(); long[] a =
 * in.nextLongArray(n);
 */
class FastScanner {
    BufferedReader br = new BufferedReader(new InputStreamReader(System.in), 1 << 16);
    StringTokenizer st = new StringTokenizer("");

    public String next() {
        while (!st.hasMoreTokens()) {
            try {
                String line = br.readLine();
                if (line == null)
                    return null;
                st = new StringTokenizer(line);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        return st.nextToken();
    }

    public int nextInt() {
        return Integer.parseInt(next());
    }

    public long nextLong() {
        return Long.parseLong(next());
    }

    public double nextDouble() {
        return Double.parseDouble(next());
    }

    /**
     * Resto de la línea actual (o la siguiente línea completa si no quedan tokens).
     */
    public String nextLine() {
        try {
            if (st.hasMoreTokens()) {
                StringBuilder sb = new StringBuilder(st.nextToken());
                while (st.hasMoreTokens())
                    sb.append(' ').append(st.nextToken());
                return sb.toString();
            }
            return br.readLine();
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }

    public int[] nextIntArray(int n) {
        int[] a = new int[n];
        for (int i = 0; i < n; i++)
            a[i] = nextInt();
        return a;
    }

    public long[] nextLongArray(int n) {
        long[] a = new long[n];
        for (int i = 0; i < n; i++)
            a[i] = nextLong();
        return a;
    }

    /**
     * Array 1-indexado: a[1..n], a[0] = 0 (útil para segment trees sobre [1, n]).
     */
    public long[] nextLongArray1(int n) {
        long[] a = new long[n + 1];
        for (int i = 1; i <= n; i++)
            a[i] = nextLong();
        return a;
    }
}
