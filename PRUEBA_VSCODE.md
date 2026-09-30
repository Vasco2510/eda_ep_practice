# Prueba del flujo en VS Code — Watermelon (Codeforces 4A)

Objetivo: comprobar el flujo completo de principio a fin con un problema fácil.
Clic en Competitive Companion → W en VS Code → `eda test` → copiar F → enviar.

## 0. Qué necesitas instalar

| Dónde | Qué | ¿Ya lo tienes? |
|---|---|---|
| Navegador | Extensión **Competitive Companion** (Chrome, Edge o Firefox) | Instálala |
| VS Code | **Extension Pack for Java** (`vscjava.vscode-java-pack`) | ✅ ya está instalada |
| PC | Python 3 y JDK (java/javac) | ✅ Python 3.14 y Java 21 |

En VS Code no hace falta nada más. Las tareas que corren `eda` vienen en `.vscode/tasks.json`.
Nada más necesitas la extensión del navegador.

> Si usas **Opera GX**, primero instala el complemento "Install Chrome Extensions" y luego
> Competitive Companion desde la Chrome Web Store. Es más simple probar con Chrome o Edge.

## 1. Abrir el proyecto

1. VS Code → *File → Open Folder…* → elige **`Z:\C26-2\EDA\ExamenEDA\Competitiva`**
   (esa carpeta exacta, no `ExamenEDA`).
2. Espera a que la extensión de Java termine de cargar (abajo a la izquierda: "Java: Ready").
3. Abre la terminal con **Ctrl+ñ** (o *Terminal → New Terminal*).
4. Verifica las plantillas:
   ```
   .\eda selftest
   ```
   ✅ Esperado: `OK: todas las plantillas pasaron (418812 comprobaciones)`

## 2. Arrancar el listener

VS Code puede preguntar *"This folder has tasks that run automatically… Allow?"*: di **Allow**.
Si no pregunta nada, arráncalo a mano: **Ctrl+Shift+P → "Tasks: Run Task" → "EDA: iniciar…"**
(o escribe `.\eda` en una terminal y déjala abierta).

✅ Esperado en esa terminal:
```
eda escuchando Competitive Companion en el puerto 27121
re-render en vivo: src/problemas/*/JSolution.java → entrega/*/Main.java
```
Deja esa terminal abierta. Para los demás comandos abre **otra** terminal (el `+` del panel).

## 3. Recibir el problema

1. En el navegador abre https://codeforces.com/problemset/problem/4/A
2. Clic en el ícono verde (+) de **Competitive Companion**.

✅ Esperado en la terminal del listener:
```
▶ A. Watermelon  (nuevo)
  W: src\problemas\cf4A\JSolution.java
  F: entrega\cf4A\Main.java
  1 tests de muestra
```
Además deben existir `src/problemas/cf4A/tests/sample1.in` (`8`) y `sample1.out` (`YES`).

❌ Si no aparece nada: revisa que el listener siga corriendo y que no tengas otra extensión
usando el puerto 27121 (por ejemplo CPH). Mira la sección 7.

## 4. Resolver en W

Abre `src/problemas/cf4A/JSolution.java` (Ctrl+P → `cf4A JSolution`). Escribe la lógica en `solve()`.
El enunciado: dado `w`, imprime YES si se puede partir en dos partes pares positivas.

<details><summary>Solución (ábrela solo si quieres ir directo a probar el flujo)</summary>

```java
    static void solve() {
        int w = in.nextInt();
        out.println(w % 2 == 0 && w > 2 ? "YES" : "NO");
    }
```
</details>

Guarda con **Ctrl+S**. ✅ En la terminal del listener aparece `✓ hh:mm:ss entrega\cf4A\Main.java [FastScanner]`.

## 5. Probar

En la segunda terminal:
```
.\eda test
```
(o **Ctrl+Shift+P → "Tasks: Run Test Task"**)

✅ Esperado:
```
✓ OK  sample1 (… ms)
1/1 tests OK  → entrega\cf4A\Main.java
```

Para ver cómo se ve un error, cambia `"YES"` por `"SI"`, guarda y corre `.\eda test` otra vez.
Debe salir `✗ WA` con entrada, esperado y obtenido. Después vuelve a poner `"YES"`.

Agrega un caso tuyo: crea `src/problemas/cf4A/tests/mio1.in` con `2` y `mio1.out` con `NO`.
Corre `.\eda test` → ✅ `2/2 tests OK`.

## 6. Enviar

1. `.\eda test --copy` → si todo pasa, `Main.java` queda en el portapapeles.
2. Abre `entrega/cf4A/Main.java` y míralo: tiene tu `solve()`, la clase `FastScanner` al final y
   ninguna línea `package` ni `import plantillas…`.
3. En Codeforces → **Submit Code** → Problem: 4A → Language: **Java 21** → pega → Submit.
   ✅ Esperado: **Accepted**.

## 7. Prueba extra: importar una plantilla (sin enviar)

1. En W, dentro de `solve()`, escribe `PersistentStack<Integer> ps = new PersistentStack<>();`
2. Pon el cursor sobre `PersistentStack` → **Ctrl+.** → *Import 'PersistentStack' (plantillas)*.
3. Guarda → abre `entrega/cf4A/Main.java`: la línea 2 dice
   `Plantillas incluidas: FastScanner, PersistentStack` y la clase está al final.
4. Borra esa línea y el import, guarda → la pila desaparece de `Main.java`.

## Si algo falla

| Síntoma | Qué hacer |
|---|---|
| `.\eda` no se reconoce | Estás en otra carpeta: la terminal debe estar en `…\Competitiva` |
| "el puerto 27121 está ocupado" | Ya tienes otra instancia de `eda` abierta (cierra la terminal vieja) o la extensión CPH instalada |
| Competitive Companion no envía nada | Abre un problema **individual** (no la lista del concurso) y recarga la página |
| VS Code subraya `plantillas` en rojo | Ctrl+Shift+P → "Java: Clean Java Language Server Workspace" → Restart |
| La tarea automática no arranca | Ctrl+Shift+P → "Tasks: Manage Automatic Tasks" → Allow, o usa `.\eda` en una terminal |

Cuando termines, cuéntame qué pasos fallaron o te sobraron, y lo ajusto.
