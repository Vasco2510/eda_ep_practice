I. D-Query
time limit per test1 second
memory limit per test256 megabytes
Given a sequence of n
 numbers a1,a2,…,an
 and a number of d
-queries. A d
-query is a pair (i,j)
 (1≤i≤j≤n
). For each d
-query (i,j)
, you have to return the number of distinct elements in the subsequence ai,ai+1,…,aj
.

Input
Line 1: n
 (1≤n≤30000
).

Line 2: n
 numbers a1,a2,…,an
 (1≤ai≤106
).

Line 3: q
 (1≤q≤200000
), the number of d
-queries.

In the next q
 lines, each line contains two numbers i,j
 representing a d
-query (1≤i≤j≤n
).

Output
For each d
-query (i,j)
, print the number of distinct elements in the subsequence ai,ai+1,…,aj
 on its own line.

Example
InputCopy
5
1 1 2 1 3
3
1 5
2 4
3 5
OutputCopy
3
2
3
Note
The array is [1,1,2,1,3]
. Query (1,5)
: subsequence [1,1,2,1,3]
 has 3
 distinct values (1,2,3
). Query (2,4)
: subsequence [1,2,1]
 has 2
 distinct values (1,2
). Query (3,5)
: subsequence [2,1,3]
 has 3
 distinct values.