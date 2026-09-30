A. Efecto cascada (Grupo 1)
time limit per test5 seconds
memory limit per test512 megabytes
Hasta el momento hemos visto que es posible realizar consultas sobre cajas en d
 dimensiones usando O(nlogd−1n)
 de memoria, O(nlogd−1n)
 de preprocesamiento para d≥2
 y O(logdn)
 por consulta.

A pesar de ello, al final de la clase de laboratorio 2 de la semana 4, fue mencionado que es posible reducir un factor O(logn)
 a la complejidad de consulta. Una técnica que permite ello se llama cross linking o fractional cascading, la cual usa un poco más de memoria (sin afectar la complejidad, solo multiplica por un factor constante) pero nos reduce a O(logd−1n)
 por consulta para d≥2
.

Ya que no deseo el odio de mis estudiantes, solicitaré que implementes un Range tree en 2 dimensiones pero con un tiempo de consulta de O(logn)
.

Nota: Este proyecto tiene fecha límite el día 24 de abril a las 8:00 p.m. Además, se debe presentar un reporte de 1-2 páginas explicando el diseño de implementación, la correctitud algorítmica y el análisis de complejidad de la estructura.

Input
La primera linea contiene dos enteros n
 y q
 (1≤n≤1000
) — La cantidad de puntos y la cantidad de consultas.

Las siguientes n
 líneas de entrada contienen dos enteros xi
 y yi
 (|xi|,|yi|≤109
) — La i
-ésima línea describe las coordenadas del i
-ésimo punto.

Las siguientes q
 líneas contienen cuatro enteros l1
, r1
, l2
 y r2
 (|l1|,|l2|,|r1|,|r2|≤109
, l1≤r1
, l2≤r2
) — La i
-ésima línea describe los dos intervalos de la caja de la i
-ésima consulta.

Output
Para cada consulta, imprime la cantidad de puntos dentro de la caja brindada.

Example
InputCopy
6 5
4 -4
-2 -5
3 0
-1 2
4 2
3 -3
2 6 -2 2
2 6 -4 -2
-2 2 -2 2
1 3 0 4
-1 -1 -2 3
OutputCopy
2
2
1
1
1