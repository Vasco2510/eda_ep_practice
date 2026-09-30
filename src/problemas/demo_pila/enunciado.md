# Demo — Pila con historia

Al inicio existe la **versión 0**: una pila vacía. Se procesan `q` operaciones; la operación `i`
(1-indexada) crea la **versión i** a partir de una versión anterior `t` (`0 ≤ t < i`):

- `1 t x` → versión i = versión t con `x` apilado. No imprime nada.
- `2 t`   → versión i = versión t sin su tope. Imprime el elemento quitado, o `-1` si la pila estaba vacía.
- `3 t`   → versión i = copia de la versión t. Imprime el tope y el tamaño de la versión t (`-1 0` si está vacía).

**Entrada:** `q` (1 ≤ q ≤ 2·10^5), luego q líneas con operaciones. |x| ≤ 10^9.
**Salida:** una línea por cada operación de tipo 2 o 3.

## Ejemplo
Entrada:
```
6
1 0 5
1 1 7
2 2
3 2
2 0
3 3
```
Salida:
```
7
7 2
-1
5 1
```
