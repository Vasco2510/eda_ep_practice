F. Rollback
time limit per test3 seconds
memory limit per test256 megabytes
Sergey has an array of integers a1,a2,…,an
, 1≤ai≤m
. He wants to answer the following questions: given l
, what is the minimal r
 such that there are at least k
 different values among al,al+1,…,ar
.

Input
The first line of input contains two integers: n
 and m
 (1≤n,m≤100000
). The second line contains n
 integers a1,a2,…,an
 (1≤ai≤m
).

The following line contains q
 — the number of queries to answer (1≤q≤100000
). To answer the queries online you must maintain an integer p
, initially p=0
. Each query is specified with two integers xi
 and yi
; use them to get the query parameters: li=((xi+p)modn)+1
, ki=((yi+p)modm)+1
 (1≤li,xi≤n
, 1≤ki,yi≤m
). Let the answer to the i
-th query be ri
. After answering the question, set p
 equal to ri
.

Output
For each query output the minimal value of ri
, or 0
 if there is no such ri
.

Example
InputCopy
7 3
1 2 1 3 1 2 1
4
7 3
7 1
7 1
2 2
OutputCopy
1
4
0
6
Note
The array is [1,2,1,3,1,2,1]
. The first query decodes to l=1,k=1
: [1,1]={1}
 already has 1
 distinct value, so r=1
. The second decodes (with p=1
) to l=2,k=3
: [2,4]={2,1,3}
 is the shortest prefix from 2
 with 3
 distinct values, so r=4
. The third decodes (with p=4
) to l=5,k=3
: only {1,2}
 (from positions 5,6,7
) are ever available from l=5
 onward — 2
 distinct values, never 3
 — so the answer is 0
. The fourth decodes (with p=0
) to l=3,k=3
: [3,6]={1,3,2}
 is the shortest range from 3
 with 3
 distinct values, so r=6
.