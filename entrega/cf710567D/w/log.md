# cf710567D
motor: sim · enunciado: enunciado.pdf

## intento 1

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


### resultado del intento 1

```
✗ WA  sample1 (87 ms): token #1: se esperaba '6', salió '3'
  entrada:
    5
    5
    3 3 3 0 0
    6
    0 3 3 0 0 3
    7
    1 2 3 0 4 5 0
    7
    1 2 5 0 4 3 0
    5
    3 1 0 0 4
  esperado:
    6
    6
    8
    9
    4
  obtenido:
    3
    3
    8
    8
    1
✗ WA  grande2 (151 ms): token #1: se esperaba '49809245550727', salió '24960782455694'
  entrada:
    1
    200000
    799006728 473115223 0 490943926 0 356529166 0 0 0 0 4846644 0 173758261 0 463144762 131139583 0 0 939437312 697235262 0 0 0 0 0 0 0 0 0 525791235 845699882 504326982 0 0 763032895 889920601 0 825385285 0 460063173 138745944 609560824 0 0 764168068 434828815 391628116 985075910 536547909 0 0 888930652 912132320 0 0 0 0 743479128 0 155387241 0 180082464 812403511 971322227 0 46720154 696519426 583868091 639202023 0 11876674 0 0 194896922 77388061 180982165 673283365 0 488096512 0 964028253 648128283 0 0 0 303057005 159601822 368245513 0 0 202033714 0 0 920760085 0 0 0 0 0 0 0 184383259 0 479597866 759498780 0 0 0 485548737 246723615 119816077 0 286074794 0 0 982106641 0 61065074 0 0 0 33019496 517788102 0 0 0 843981620 155090722 208172241 406633944 0 0 0 94649410 561189724 0 630387948 0 597331862 831482386 0 0 768271940 227367749 0 0 0 0 0 993456180 275135339 922513272 0 955665201 487787533 707784811 0 629721539 161378991 0 0 994109138 285381297 0 0 219112379 505072823 0 59060624 144030525 0 861699085 0 0 0 366844119 0 916731002 226552185 0 0 946884228 31380691 149501891 371198887 0 0 0 0 522289730 406608472 0 567397703 25978473 795103270 0 655382047 106656405 122534012 0 0 
    … (recortado)
  esperado:
    49809245550727
  obtenido:
    24960782455694
✗ WA  stress1 (90 ms): token #2: se esperaba '13', salió '6'
  entrada:
    400
    3
    0 0 0
    11
    0 0 0 7 1 0 4 0 0 1 0
    7
    0 1 0 8 0 4 0
    5
    0 9 0 0 6
    12
    0 9 0 5 8 7 0 4 0 0 9 0
    8
    0 3 0 8 0 0 7 0
    9
    0 4 0 7 6 0 5 9 0
    12
    0 9 0 0 6 0 0 0 0 1 9 0
    10
    0 3 0 0 1 0 0 0 0 2
    3
    0 0 0
    9
    3 5 0 0 0 0 0 0 0
    5
    0 0 0 0 1
    3
    8 9 7
    4
    0 4 0 6
    11
    0 0 0 0 0 5 0 0 1 1 4
    8
    3 0 0 0 4 7 0 2
    7
    5 0 6 0 0 0 0
    7
    0 0 0 0 0 2 0
    3
    0 0 0
    10
    0 0 0 0 0 0 0 0 0 0
    2
    0 0
    10
    0 0 0 0 0 0 0 0 0 4
    7
    0 0 0 0 7 5 5
    8
    0 4 0 0 5 0 0 0
    2
    6 0
    5
    4 9 8 0 3
    4
    0 0 0 0
    2
    0 0
    1
    0
    6
    0 0 9 0 0 0
    2
    5 2
    2
    1 0
    6
    0 0 0 2 0 0
    6
    0 9 0 0 9 0
    10
    9 0 0 0 1 0 2 0 0 0
    9
    0 0 0 0 7 0 6 3 0
    5
    0 0 0 0 3
    6
    9 8 0 0 0 0
    9
    5 0 2 0 0 0 5 0 8
    2
    2 9
    7
    0 0 4 0 7 0 0
    9
    1 0 0 0 0 0 0 0 0
    10
    0 0 0 2 0 0 0 4 8 0
    11
    0 0 0 0 0 5 0 0 0 0 0
    5
    0 2 1 5 0
    9
    6 0 9 6 0 0 0 5 0
    12
    0 0 4 0 0 8 0 5 0 0 6 1
    7
    0 6 0 4 5 0 3
    7
    0 2 0 5 7 0 0
    5
    0 8 0 0 0
    6
    2 0 3 3 0 5
    5
    4 0 0 0 9
    6
    8 9 0 5 0 6
    12
    0 0 0 5 6 0 4 1 0 0 0 2
    12
    3 8 3 0 0 0 0 0 0 4 0 0
    7
    0 0 0 0 0 9 0
    11
    0 0 0 0 0 0 0 8 0 8 0
    8
    0 0 0 0 7 0 0 0
    1
    0
    11
    0 0 0 8 0 1 1 0 0 0 0
    8
    3 5 4 0 6 0 0 1
    10
    0 7 9 0 6 7 4 0 2 5
    10
    0 0 0 0 0 2 8 0 0 3
    1
    8
    3
    7 0 0
    2
    0 0
    1
    0
    12
    0 0 0 0 0 9 0 6 7 0 3 8
    9
    9 0 0 0 0 0 0 0 5
    9
    0 0 0 6 9 1 0 6 0
    10
    0 0 0 0 0 1 8 0 0 0
    5
    8 6 0 0 5
    4
    0 0 0 9
    5
    0 0 9 0 4
    3
    0 1 0
    12
    0 4 0 0 6 0 0 0 
    … (recortado)
  esperado:
    0
    13
    13
    9
    38
    18
    20
    24
    4
    0
    8
    0
    0
    4
    5
    10
    11
    2
    0
    0
    0
    0
    0
    9
    6
    9
    0
    0
    0
    9
    0
    1
    2
    18
    12
    13
    0
    17
    12
    0
    11
    1
    10
    5
    5
    26
    17
    11
    14
    8
    5
    4
    17
    16
    18
    9
    16
    7
    0
    10
    15
    16
    10
    0
    7
    0
    0
    16
    9
    15
    9
    14
    0
    9
    1
    11
    23
    10
    6
    0
    7
    11
    4
    17
    9
    15
    8
    20
    9
    0
    3
    0
    17
    1
    10
    25
    0
    16
    0
    3
    10
    16
    18
    10
    11
    19
    9
    2
    0
    0
    5
    2
    0
    0
    3
    22
    8
    10
    10
    0
    29
    0
    2
    12
    0
    12
    0
    0
    17
    9
    7
    14
    0
    0
    7
    0
    0
    8
    12
    26
    12
    10
    2
    11
    0
    0
    15
    9
    0
    16
    9
    7
    4
    13
    0
    0
    0
    11
    2
    3
    18
    6
    5
    18
    0
    4
    3
    6
    0
    3
    14
    0
    8
    0
    0
    4
    0
    3
    14
    10
    13
    0
    0
    8
    0
    13
    0
    17
    6
    7
    12
    9
    8
    20
    5
    0
    23
    0
    19
    6
    2
    18
    0
    9
    10
    16
    15
    21
    10
    5
    3
    18
    9
    7
    4
    0
    7
    8
    6
    6
    10
    0
    18
    4
    0
    8
    0
    1
    0
    6
    0
    9
    0
    0
    0
    0
    9
    0
    8
    7
    17
    22
    0
    28
    8
    8
    0
    7
    14
    0
    16
    0
    0
    8
    0
    23
    13
    15
    8
    13
    26
    15
    0
    21
    2
    23
    7
    14
    0
    7
    0
    8
    5
    0
    5
    12
    13
    7
    10
    8
    0
    9
    17
    5
    24
    7
    0
    0
    7
    0
    0
    7
    0
    15
    19
    0
    6
    3
    6
    0
    0
    0
    0
    3
    21
    21
    5
    10
    15
    18
    21
    0
    13
    15
    15
    15
    0
    8
    0
    9
    9
    11
    4
    0
    19
    0
    0
    15
    0
    0
    0
    18
    14
    0
    27
    12
    15
    0
    10
    0
    0
    32
    15
    0
    15
    12
    0
    15
    0
    0
    1
    7
    0
    19
    17
    19
    4
    0
    0
    0
    5
    9
    1
    0
    0
    6
    5
    7
    20
    6
    0
    0
    13
    4
    0
    0
    6
    30
    2
    14
    0
    14
    14
    1
    16
    11
    0
    16
    8
    8
    4
    0
    6
    13
    0
    5
    17
    7
    1
    18
  obtenido:
    0
    6
    13
    9
    29
    18
    19
    24
    4
    0
    5
    0
    0
    4
    5
    10
    11
    2
    0
    0
    0
    0
    0
    9
    6
    8
    0
    0
    0
    9
    0
    1
    2
    18
    12
    10
    0
    8
    12
    0
    11
    1
    10
    5
    5
    17
    17
    11
    9
    8
    5
    4
    14
    7
    7
    9
    16
    7
    0
    9
    10
    13
    8
    0
    7
    0
    0
    16
    9
    7
    8
    6
    0
    9
    1
    11
    16
    10
    6
    0
    7
    11
    4
    17
    9
    15
    1
    11
    3
    0
    3
    0
    13
    1
    5
    6
    0
    15
    0
    3
    10
    8
    18
    3
    11
    13
    9
    2
    0
    0
    5
    2
    0
    0
    3
    9
    8
    10
    6
    0
    22
    0
    2
    8
    0
    12
    0
    0
    17
    9
    7
    14
    0
    0
    4
    0
    0
    8
    7
    22
    12
    10
    2
    10
    0
    0
    13
    9
    0
    10
    9
    7
    4
    13
    0
    0
    0
    11
    2
    3
    6
    6
    5
    17
    0
    4
    3
    6
    0
    3
    5
    0
    8
    0
    0
    4
    0
    3
    14
    10
    4
    0
    0
    8
    0
    13
    0
    13
    6
    7
    12
    9
    8
    20
    5
    0
    14
    0
    11
    1
    2
    15
    0
    8
    8
    9
    7
    13
    8
    1
    3
    15
    9
    7
    4
    0
    7
    8
    6
    1
    10
    0
    16
    4
    0
    8
    0
    1
    0
    2
    0
    9
    0
    0
    0
    0
    9
    0
    8
    7
    17
    17
    0
    2
    8
    8
    0
    7
    14
    0
    16
    0
    0
    8
    0
    23
    13
    15
    8
    13
    12
    10
    0
    11
    2
    23
    7
    11
    0
    4
    0
    8
    5
    0
    5
    6
    13
    7
    10
    8
    0
    9
    4
    5
    16
    7
    0
    0
    1
    0
    0
    7
    0
    15
    17
    0
    4
    3
    6
    0
    0
    0
    0
    3
    21
    14
    3
    10
    11
    18
    13
    0
    13
    11
    3
    6
    0
    8
    0
    9
    9
    7
    4
    0
    11
    0
    0
    15
    0
    0
    0
    18
    9
    0
    18
    7
    8
    0
    10
    0
    0
    23
    15
    0
    10
    6
    0
    11
    0
    0
    1
    7
    0
    19
    17
    12
    4
    0
    0
    0
    5
    9
    1
    0
    0
    6
    5
    7
    13
    6
    0
    0
    10
    4
    0
    0
    6
    9
    2
    13
    0
    14
    14
    1
    5
    11
    0
    16
    8
    8
    4
    0
    2
    13
    0
    5
    10
    7
    1
    16
0/3 tests OK  → entrega\cf710567D\Main_w.java
```

## intento 2

Idea: max-heap con PriorityQueue.
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
        int n = in.nextInt(); long ans = 0; PriorityQueue<Long> pq = new PriorityQueue<>(Comparator.reverseOrder());
        for (int i = 0; i < n; i++) { long s = in.nextLong(); if (s > 0) pq.add(s); else if (!pq.isEmpty()) ans += pq.poll(); }
        out.println(ans);
    }
}
```


### resultado del intento 2

```
No usaste las plantillas obligatorias: PersistentLeftistHeap
```

## intento 3

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


### resultado del intento 3

```
✓ OK  sample1 (71 ms)
✓ OK  grande2 (189 ms)
✓ OK  stress1 (89 ms)
3/3 tests OK  → entrega\cf710567D\Main_w.java
```

