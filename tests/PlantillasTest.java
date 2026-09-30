import plantillas.*;

import java.util.*;

/**
 * Verificación de las plantillas persistentes: operaciones aleatorias sobre versiones aleatorias,
 * comparadas contra una fuerza bruta que guarda una copia completa por versión.
 * Ejecutar:  python tools/eda.py selftest   (o compilar src/plantillas + este archivo a mano)
 */
public class PlantillasTest {
    static Random rnd = new Random(12345);
    static int checks = 0;

    static void check(boolean ok, String msg) {
        checks++;
        if (!ok) throw new AssertionError(msg);
    }

    public static void main(String[] args) {
        for (int round = 0; round < 30; round++) {
            segTree();
            lazySegTree();
            stack();
            queue();
            fibHeap();
            leftistHeap();
            persistentArray();
            trie();
            binaryTrie();
            treap();
        }
        kthSmallest();
        bigStress();
        System.out.println("OK: todas las plantillas pasaron (" + checks + " comprobaciones)");
    }

    static void segTree() {
        int n = 1 + rnd.nextInt(30);
        long[] a = new long[n + 1];
        for (int i = 1; i <= n; i++) a[i] = rnd.nextInt(100) - 50;
        PersistentSegmentTree t = new PersistentSegmentTree(1, n, 4);
        List<long[]> brute = new ArrayList<>();
        List<Integer> roots = new ArrayList<>();
        brute.add(a.clone());
        roots.add(t.build(a));
        for (int op = 0; op < 300; op++) {
            int v = rnd.nextInt(roots.size());
            long[] b = brute.get(v).clone();
            int p = 1 + rnd.nextInt(n);
            long x = rnd.nextInt(100) - 50;
            int nr;
            if (rnd.nextBoolean()) { b[p] = x; nr = t.set(roots.get(v), p, x); }
            else { b[p] += x; nr = t.add(roots.get(v), p, x); }
            brute.add(b);
            roots.add(nr);
            int q = rnd.nextInt(roots.size());
            int l = 1 + rnd.nextInt(n), r = l + rnd.nextInt(n - l + 1);
            long s = 0;
            for (int i = l; i <= r; i++) s += brute.get(q)[i];
            check(s == t.query(roots.get(q), l, r), "segTree query");
            check(brute.get(q)[l] == t.get(roots.get(q), l), "segTree get");
        }
    }

    static void lazySegTree() {
        int n = 1 + rnd.nextInt(30);
        long[] a = new long[n + 1];
        for (int i = 1; i <= n; i++) a[i] = rnd.nextInt(100);
        PersistentLazySegmentTree t = new PersistentLazySegmentTree(1, n, 4);
        List<long[]> brute = new ArrayList<>();
        List<Integer> roots = new ArrayList<>();
        brute.add(a.clone());
        roots.add(rnd.nextBoolean() ? t.build(a) : 0);
        if (roots.get(0) == 0) brute.set(0, new long[n + 1]);
        for (int op = 0; op < 300; op++) {
            int v = rnd.nextInt(roots.size());
            long[] b = brute.get(v).clone();
            int l = 1 + rnd.nextInt(n), r = l + rnd.nextInt(n - l + 1);
            long x = rnd.nextInt(21) - 10;
            for (int i = l; i <= r; i++) b[i] += x;
            brute.add(b);
            roots.add(t.rangeAdd(roots.get(v), l, r, x));
            int q = rnd.nextInt(roots.size());
            l = 1 + rnd.nextInt(n); r = l + rnd.nextInt(n - l + 1);
            long s = 0;
            for (int i = l; i <= r; i++) s += brute.get(q)[i];
            check(s == t.query(roots.get(q), l, r), "lazySegTree query");
        }
    }

    static void stack() {
        PersistentStack<Integer> s = new PersistentStack<>();
        List<ArrayDeque<Integer>> brute = new ArrayList<>();
        brute.add(new ArrayDeque<>());
        for (int op = 0; op < 300; op++) {
            int v = rnd.nextInt(s.versions());
            ArrayDeque<Integer> b = new ArrayDeque<>(brute.get(v));
            int nv;
            if (rnd.nextInt(3) > 0) { int x = rnd.nextInt(1000); b.push(x); nv = s.push(v, x); }
            else { b.poll(); nv = s.pop(v); }
            brute.add(b);
            check(nv == brute.size() - 1, "stack version id");
            int q = rnd.nextInt(s.versions());
            check(Objects.equals(brute.get(q).peek(), s.peek(q)), "stack peek");
            check(brute.get(q).size() == s.size(q), "stack size");
            check(new ArrayList<>(brute.get(q)).equals(s.toList(q)), "stack toList");
        }
    }

    static void queue() {
        PersistentQueue<Integer> s = new PersistentQueue<>();
        List<ArrayDeque<Integer>> brute = new ArrayList<>();
        brute.add(new ArrayDeque<>());
        for (int op = 0; op < 300; op++) {
            int v = rnd.nextInt(s.versions());
            ArrayDeque<Integer> b = new ArrayDeque<>(brute.get(v));
            int nv;
            if (rnd.nextInt(3) > 0) { int x = rnd.nextInt(1000); b.addLast(x); nv = s.push(v, x); }
            else { b.pollFirst(); nv = s.pop(v); }
            brute.add(b);
            check(nv == brute.size() - 1, "queue version id");
            int q = rnd.nextInt(s.versions());
            check(Objects.equals(brute.get(q).peekFirst(), s.peek(q)), "queue peek");
            check(Objects.equals(brute.get(q).peekLast(), s.back(q)), "queue back");
            check(brute.get(q).size() == s.size(q), "queue size");
            check(new ArrayList<>(brute.get(q)).equals(s.toList(q)), "queue toList");
        }
    }

    interface HeapOps {
        int insert(int v, long k, int id);
        int merge(int a, int b);
        int extractMin(int v);
        long minKey(int v);
        int size(int v);
        boolean isEmpty(int v);
    }

    static void heapCheck(HeapOps h, String name) {
        List<PriorityQueue<Long>> brute = new ArrayList<>();
        brute.add(new PriorityQueue<>());
        for (int op = 0; op < 300; op++) {
            int kind = rnd.nextInt(5), v = rnd.nextInt(brute.size());
            PriorityQueue<Long> b = new PriorityQueue<>(brute.get(v));
            int nv;
            if (kind <= 1) { long k = rnd.nextInt(200) - 100; b.add(k); nv = h.insert(v, k, op); }
            else if (kind <= 3) { b.poll(); nv = h.extractMin(v); }
            else { int w = rnd.nextInt(brute.size()); b.addAll(brute.get(w)); nv = h.merge(v, w); }
            brute.add(b);
            check(nv == brute.size() - 1, name + " version id");
            int q = rnd.nextInt(brute.size());
            check(brute.get(q).size() == h.size(q), name + " size");
            check(brute.get(q).isEmpty() == h.isEmpty(q), name + " isEmpty");
            if (!brute.get(q).isEmpty()) check(brute.get(q).peek() == h.minKey(q), name + " minKey");
        }
        // vaciar completamente una versión grande y comprobar el orden
        int best = 0;
        for (int i = 0; i < brute.size(); i++) if (brute.get(i).size() > brute.get(best).size()) best = i;
        PriorityQueue<Long> b = new PriorityQueue<>(brute.get(best));
        int v = best;
        while (!b.isEmpty()) {
            check(b.poll() == h.minKey(v), name + " drain order");
            v = h.extractMin(v);
        }
        check(h.isEmpty(v), name + " drained");
    }

    static void fibHeap() {
        PersistentFibonacciHeap h = new PersistentFibonacciHeap();
        heapCheck(new HeapOps() {
            public int insert(int v, long k, int id) { return h.insert(v, k, id); }
            public int merge(int a, int b) { return h.merge(a, b); }
            public int extractMin(int v) { return h.extractMin(v); }
            public long minKey(int v) { return h.minKey(v); }
            public int size(int v) { return h.size(v); }
            public boolean isEmpty(int v) { return h.isEmpty(v); }
        }, "fibHeap");
    }

    static void leftistHeap() {
        PersistentLeftistHeap h = new PersistentLeftistHeap();
        heapCheck(new HeapOps() {
            public int insert(int v, long k, int id) { return h.insert(v, k, id); }
            public int merge(int a, int b) { return h.merge(a, b); }
            public int extractMin(int v) { return h.extractMin(v); }
            public long minKey(int v) { return h.minKey(v); }
            public int size(int v) { return h.size(v); }
            public boolean isEmpty(int v) { return h.isEmpty(v); }
        }, "leftistHeap");
    }

    static void persistentArray() {
        int n = 1 + rnd.nextInt(20);
        Integer[] init = new Integer[n];
        for (int i = 0; i < n; i++) init[i] = rnd.nextInt(50);
        PersistentArray<Integer> pa = rnd.nextBoolean() ? new PersistentArray<>(init) : null;
        if (pa == null) { Arrays.fill(init, 7); pa = new PersistentArray<>(n, 7); }
        List<Integer[]> brute = new ArrayList<>();
        brute.add(init.clone());
        for (int op = 0; op < 300; op++) {
            int v = rnd.nextInt(brute.size());
            Integer[] b = brute.get(v).clone();
            int nv;
            if (rnd.nextInt(5) == 0) nv = pa.copy(v);
            else { int p = rnd.nextInt(n), x = rnd.nextInt(50); b[p] = x; nv = pa.set(v, p, x); }
            brute.add(b);
            check(nv == brute.size() - 1, "array version id");
            int q = rnd.nextInt(brute.size()), p = rnd.nextInt(n);
            check(brute.get(q)[p].equals(pa.get(q, p)), "array get");
        }
    }

    static String randWord() {
        int len = 1 + rnd.nextInt(4);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < len; i++) sb.append((char) ('a' + rnd.nextInt(3)));
        return sb.toString();
    }

    static void trie() {
        PersistentTrie t = new PersistentTrie();
        List<List<String>> brute = new ArrayList<>();
        brute.add(new ArrayList<>());
        for (int op = 0; op < 300; op++) {
            int v = rnd.nextInt(brute.size());
            List<String> b = new ArrayList<>(brute.get(v));
            String w = randWord();
            int nv;
            if (rnd.nextInt(3) > 0) { b.add(w); nv = t.insert(v, w); }
            else { b.remove(w); nv = t.erase(v, w); }
            brute.add(b);
            check(nv == brute.size() - 1, "trie version id");
            int q = rnd.nextInt(brute.size());
            String s = randWord();
            check(Collections.frequency(brute.get(q), s) == t.count(q, s), "trie count");
            String pre = s.substring(0, 1 + rnd.nextInt(s.length()));
            check(brute.get(q).stream().filter(x -> x.startsWith(pre)).count() == t.countPrefix(q, pre), "trie prefix");
            check(brute.get(q).size() == t.size(q), "trie size");
        }
    }

    static void binaryTrie() {
        int n = 1 + rnd.nextInt(40);
        int[] a = new int[n + 1];
        for (int i = 1; i <= n; i++) a[i] = rnd.nextInt(1 << 10);
        PersistentBinaryTrie t = new PersistentBinaryTrie();
        int[] pre = new int[n + 1];
        for (int i = 1; i <= n; i++) pre[i] = t.insert(pre[i - 1], a[i]);
        for (int q = 0; q < 60; q++) {
            int l = 1 + rnd.nextInt(n), r = l + rnd.nextInt(n - l + 1), x = rnd.nextInt(1 << 10);
            long mx = -1, mn = Long.MAX_VALUE;
            int[] sub = Arrays.copyOfRange(a, l, r + 1);
            for (int y : sub) { mx = Math.max(mx, x ^ y); mn = Math.min(mn, x ^ y); }
            Arrays.sort(sub);
            int k = 1 + rnd.nextInt(sub.length);
            check(mx == t.maxXor(pre[l - 1], pre[r], x), "binTrie maxXor");
            check(mn == t.minXor(pre[l - 1], pre[r], x), "binTrie minXor");
            check(sub[k - 1] == t.kth(pre[l - 1], pre[r], k), "binTrie kth");
            int y = a[l];
            check(Arrays.stream(a, 1, r + 1).filter(z -> z == y).count() == t.count(pre[r], y), "binTrie count");
        }
        int v = pre[n], y = a[1];
        int before = t.count(v, y);
        int v2 = t.erase(v, y);
        check(t.count(v2, y) == before - 1 && t.size(v2) == n - 1 && t.count(v, y) == before, "binTrie erase");
    }

    static void treap() {
        PersistentTreap t = new PersistentTreap();
        List<List<Long>> brute = new ArrayList<>();
        brute.add(new ArrayList<>());
        for (int op = 0; op < 300; op++) {
            int v = rnd.nextInt(brute.size());
            List<Long> b = new ArrayList<>(brute.get(v));
            long k = rnd.nextInt(40) - 20;
            int nv;
            if (rnd.nextInt(3) > 0) { b.add(k); nv = t.insert(v, k); }
            else { b.remove((Long) k); nv = t.erase(v, k); }
            Collections.sort(b);
            brute.add(b);
            check(nv == brute.size() - 1, "treap version id");
            int q = rnd.nextInt(brute.size());
            List<Long> s = brute.get(q);
            long key = rnd.nextInt(44) - 22;
            check(s.equals(t.toList(q)), "treap toList");
            check(s.size() == t.size(q), "treap size");
            check(s.contains(key) == t.contains(q, key), "treap contains");
            check(s.stream().filter(x -> x < key).count() == t.rank(q, key), "treap rank");
            check(Collections.frequency(s, key) == t.count(q, key), "treap count");
            check(s.stream().filter(x -> x <= key).max(Long::compare).orElse(Long.MIN_VALUE) == t.floor(q, key), "treap floor");
            check(s.stream().filter(x -> x >= key).min(Long::compare).orElse(Long.MAX_VALUE) == t.ceiling(q, key), "treap ceiling");
            if (!s.isEmpty()) { int k2 = 1 + rnd.nextInt(s.size()); check(s.get(k2 - 1) == t.kth(q, k2), "treap kth"); }
        }
    }

    /** k-ésimo menor en a[l..r] con raíces por prefijo (uso clásico del segment tree persistente). */
    static void kthSmallest() {
        for (int round = 0; round < 50; round++) {
            int n = 1 + rnd.nextInt(40);
            int[] a = new int[n + 1];
            for (int i = 1; i <= n; i++) a[i] = rnd.nextInt(20);
            int[] vals = Arrays.stream(a, 1, n + 1).distinct().sorted().toArray();
            PersistentSegmentTree t = new PersistentSegmentTree(1, vals.length, 4);
            int[] pre = new int[n + 1];
            for (int i = 1; i <= n; i++) pre[i] = t.add(pre[i - 1], Arrays.binarySearch(vals, a[i]) + 1, 1);
            for (int q = 0; q < 50; q++) {
                int l = 1 + rnd.nextInt(n), r = l + rnd.nextInt(n - l + 1);
                int[] sub = Arrays.copyOfRange(a, l, r + 1);
                Arrays.sort(sub);
                int k = 1 + rnd.nextInt(sub.length);
                check(vals[t.kth(pre[l - 1], pre[r], k) - 1] == sub[k - 1], "kth");
            }
        }
    }

    /** Tamaños de competencia: que no explote en tiempo/memoria/stack. */
    static void bigStress() {
        int n = 200_000, q = 200_000;
        long t0 = System.currentTimeMillis();
        PersistentSegmentTree t = new PersistentSegmentTree(1, n);
        int root = t.build(new long[n + 1]);
        for (int i = 0; i < q; i++) root = t.add(root, 1 + rnd.nextInt(n), 1);
        check(t.query(root, 1, n) == q, "big segTree");
        PersistentLazySegmentTree lt = new PersistentLazySegmentTree(1, n);
        int lr = 0;
        for (int i = 0; i < q; i++) lr = lt.rangeAdd(lr, 1, n, 1);
        check(lt.query(lr, 1, n) == (long) q * n, "big lazy");
        PersistentStack<Integer> s = new PersistentStack<>();
        int sv = 0;
        for (int i = 0; i < q; i++) sv = s.push(sv, i);
        check(s.size(sv) == q, "big stack");
        PersistentQueue<Integer> pq = new PersistentQueue<>();
        int qv = 0;
        for (int i = 0; i < q; i++) qv = pq.push(qv, i);
        for (int i = 0; i < q / 2; i++) qv = pq.pop(qv);
        check(pq.peek(qv) == q / 2, "big queue");
        PersistentFibonacciHeap fh = new PersistentFibonacciHeap();
        PersistentLeftistHeap lh = new PersistentLeftistHeap();
        int fv = 0, lv = 0;
        for (int i = 0; i < q; i++) { long k = rnd.nextInt(); fv = fh.insert(fv, k); lv = lh.insert(lv, k); }
        for (int i = 0; i < q / 2; i++) {
            check(fh.minKey(fv) == lh.minKey(lv), "big heaps");
            fv = fh.extractMin(fv);
            lv = lh.extractMin(lv);
        }
        PersistentArray<Integer> pa = new PersistentArray<>(n, 0);
        int av = 0;
        for (int i = 0; i < q; i++) av = pa.set(av, rnd.nextInt(n), i);
        check(pa.versions() == q + 1, "big array");
        PersistentBinaryTrie bt = new PersistentBinaryTrie();
        int bv = 0;
        for (int i = 0; i < q; i++) bv = bt.insert(bv, rnd.nextInt(1 << 30));
        check(bt.size(bv) == q, "big binTrie");
        PersistentTrie tr = new PersistentTrie();
        int tv = 0;
        for (int i = 0; i < q; i++) tv = tr.insert(tv, "palabra" + (char) ('a' + i % 26) + (char) ('a' + i / 26 % 26));
        check(tr.countPrefix(tv, "palabra") == q, "big trie");
        PersistentTreap tp = new PersistentTreap();
        int pv = 0;
        for (int i = 0; i < q; i++) pv = tp.insert(pv, i);   // claves ordenadas: peor caso para un BST sin balancear
        check(tp.kth(pv, q / 2) == q / 2 - 1, "big treap");
        System.out.println("  estrés n=q=2e5 en " + (System.currentTimeMillis() - t0) + " ms");
    }
}
