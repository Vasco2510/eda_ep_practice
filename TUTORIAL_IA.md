# IA — `.\eda ia`

Un solo comando: la IA lee el enunciado y los tests, escribe su propio `JSolution.java` usando tus
plantillas, lo renderiza, lo prueba y, si falla, recibe el error y lo corrige (hasta 4 intentos).

```
.\eda ia --clip      (VS Code: Ctrl+Shift+P → Tasks: Run Task → "EDA: IA resuelve (enunciado del portapapeles)")
```

| Archivo | Qué es |
|---|---|
| `entrega/<slug>/Main_ia.java` | **Lo que envías** (F de la IA, con las plantillas incrustadas) |
| `entrega/<slug>/ia/JSolution.java` | El W que escribió la IA (léelo para entender la solución) |
| `entrega/<slug>/ia/log.md` | Bitácora: explicación de la IA en español + resultado de cada intento |

Tu `src/problemas/<slug>/JSolution.java` **no se toca**: tu trabajo y el de la IA van separados.

**Resumen rápido** (una vez: clave de Groq, sección 1):
```
.\eda ia --ping              ¿funciona la clave?
.\eda ia --clip --solve      (tras Ctrl+A, Ctrl+C en el problema) → solo lo de solve() al portapapeles
.\eda ia --clip --copy       → Main_ia.java completo al portapapeles
```

---

## 1. Elegir el modelo (una sola vez)

| Proveedor | Costo | Calidad en competitiva | Qué necesitas |
|---|---|---|---|
| **`groq`** (por defecto) | Gratis (con límites) | Buena (`openai/gpt-oss-120b`) | Una API key gratis de Groq |
| **`claude-code`** | Usa tu plan de Claude (Pro/Max) | Muy buena | Instalar Claude Code e iniciar sesión |
| `anthropic` | Pago por uso (~$0.10–1 por problema) | Muy buena | API key de console.anthropic.com con saldo |
| `ollama` | Gratis, offline | Débil | Ollama + un modelo descargado |

### Groq (por defecto, gratis): obtener la clave
1. Abre https://console.groq.com y entra con **Google, GitHub o tu correo**. No pide tarjeta.
2. En el menú de la izquierda: **API Keys** → botón **Create API Key**.
3. Ponle un nombre (por ejemplo `eda-examen`) → **Submit**.
4. **Copia la clave en ese momento** (empieza con `gsk_`). Groq la muestra una sola vez; si la pierdes,
   borra esa y crea otra.
5. Guárdala en Windows. En una terminal de PowerShell (reemplaza por tu clave, con comillas):
   ```
   setx GROQ_API_KEY "gsk_tu_clave_aqui"
   ```
   Debe decir `CORRECTO: se guardó el valor especificado.`
6. **Cierra VS Code por completo y vuelve a abrirlo.** `setx` solo afecta a las terminales nuevas.
7. Verifica en la terminal de VS Code:
   ```
   .\eda ia --ping
   ```
   ✅ Esperado: `✓ el proveedor respondió: OK` (gasta unos 30 tokens del cupo gratis).

No pongas la clave en ningún archivo del proyecto: se subiría al repo. Si se filtra, bórrala en
**API Keys** y crea otra.

Límites del plan gratis para `openai/gpt-oss-120b` (según console.groq.com hoy): **8 000 tokens por
minuto**, 1 000 solicitudes y 200 000 tokens por día (unos 30–50 problemas diarios). Por eso con Groq:
- las plantillas van en **modo compacto** (firmas de los métodos; el ejemplo de uso completo solo de
  las que pides con `--usar` o las que la IA ya importó), unos 3 000 tokens por intento;
- en cada reintento se reenvía solo el enunciado, su último código y el error;
- si Groq dice "espera N s", `eda` espera y sigue solo.

Otros modelos de Groq: `--modelo openai/gpt-oss-20b` (más rápido y más débil) o
`--modelo qwen/qwen3.8-27b`. Lista actual: https://console.groq.com/docs/models.
`--effort low|medium|high` controla cuánto "piensa" gpt-oss (por defecto `medium`; `high` puede
chocar con el límite de 8 000 tokens por minuto).

### Claude Code (usa tu plan de Claude, sin API key)
Requiere plan Pro, Max, Team o Enterprise (el plan gratis de claude.ai no incluye Claude Code).
1. Instálalo en PowerShell (instalador oficial, no necesita administrador):
   ```
   irm https://claude.ai/install.ps1 | iex
   ```
2. **Abre una terminal nueva** y verifica: `claude --version`
   (si dice que no se reconoce, cierra y reabre VS Code).
3. Inicia sesión: corre `claude`, elige iniciar sesión con tu **cuenta de claude.ai (suscripción)**,
   acepta en el navegador y sal con `/exit`. Si alguna vez entraste con una cuenta de Console
   (API), usa `/login` dentro de `claude` para cambiar a tu suscripción.
   Comprueba con `claude auth status`.
4. Prueba la conexión:
   ```
   .\eda ia --ping --proveedor claude-code
   ```
5. Úsalo con `--proveedor claude-code`, o déjalo por defecto creando `tools/config.json` con
   `{ "ia_proveedor": "claude-code" }`.

Consume de los límites de uso de tu plan (los mismos que usas en claude.ai). Recibe las plantillas
completas y puede leer el PDF del enunciado. Solo tiene permiso para **leer** archivos: no edita
nada ni ejecuta comandos; `eda` se encarga de guardar, compilar y probar.

**Modo interactivo:** en la terminal de VS Code, dentro de `Competitiva`, escribe `claude` y pídele
cosas como *"resuelve el problema actual usando PersistentLeftistHeap y pruébalo"* o *"explícame por
qué falla mi solve()"*. El archivo `CLAUDE.md` del proyecto le explica tu flujo (`eda test`,
plantillas, dónde va W). En ese modo sí edita tu W y corre comandos, pero te pide permiso antes.

### API de Claude (pago por uso): obtener la clave
Ojo: la suscripción de claude.ai (Pro/Max) **no incluye créditos de API**. Son cuentas y saldos
separados. Si quieres usar tu plan, usa **Claude Code** (arriba), no esta opción.
1. Abre https://console.anthropic.com e inicia sesión (o crea una cuenta).
2. **Billing** (o *Plans & Billing*) → compra créditos (hay un mínimo, del orden de US$5).
3. **API Keys** → **Create Key** → ponle un nombre → copia la clave (empieza con `sk-ant-`, se
   muestra una sola vez).
4. En PowerShell: `setx ANTHROPIC_API_KEY "sk-ant-tu_clave_aqui"` → cierra y reabre VS Code.
5. Verifica: `.\eda ia --ping --proveedor anthropic`.
6. Úsala con `--proveedor anthropic`, o déjala por defecto con `{ "ia_proveedor": "anthropic" }` en
   `tools/config.json` (el SDK ya está instalado).

### Ajustes permanentes (en `tools/config.json`, todos opcionales)
```json
{ "ia_proveedor": "groq", "ia_modelo": "openai/gpt-oss-120b", "ia_effort": "medium", "ia_intentos": 4 }
```

---

## 2. El enunciado

Competitive Companion **no envía el enunciado**, solo los tests. `eda ia` lo busca en este orden:

1. `--clip`: el portapapeles. En la página del problema: **Ctrl+A, Ctrl+C**, luego `.\eda ia --clip`.
   Se guarda en `enunciado.md`. **Es la mejor opción.**
2. `src/problemas/<slug>/enunciado.md` / `.txt` / cualquier `.pdf` en esa carpeta.
   Ojo con el PDF: para Groq se extrae su texto, y en PDFs impresos desde Codeforces **se pierden las
   variables y fórmulas** (por ejemplo "un mazo de  cartas" sin la `n`). Claude Code sí lee el PDF bien.
3. La URL del problema. Funciona en el problemset público; **en grupos privados (como el del curso)
   Codeforces pide login y falla**, así que en el simulacro usa `--clip`.

## 3. Flujo del simulacro

1. `.\eda` corriendo → clic en Competitive Companion en el problema.
2. En la página del problema: **Ctrl+A, Ctrl+C**.
3. Elige qué quieres recibir:
   - `.\eda ia --clip --copy` → deja en el portapapeles **`Main_ia.java` completo**, listo para pegar
     en Codeforces. (Para copiarlo después: `.\eda copy --ia`.)
   - `.\eda ia --clip --solve` → muestra y copia **solo lo que va en tu W**: el `import` de la
     plantilla, `solve()` y sus funciones auxiliares, y un aviso si hay que descomentar
     `t = in.nextInt()`. Pégalo en tu `JSolution.java` y termina con tu flujo normal (`.\eda test`).
     Se guarda también en `entrega/<slug>/ia/solve.java.txt`.
4. Espera: de segundos a un par de minutos. Verás la respuesta de la IA en gris y cada intento con
   sus tests. Solo se entrega algo si pasa los tests.

Opciones útiles:
- `--usar PersistentLeftistHeap` (o varias separadas por coma): **obliga** a usar esas plantillas.
  Si la IA resuelve sin ellas, el intento se rechaza y se le pide que las use.
- `--proveedor claude-code`, `--modelo <id>`, `--effort <nivel>`, `--intentos 6`: por ejecución.
- `.\eda ia cf710567D`: otro problema que no es el actual.

**Ojo:** "pasa los tests" significa que pasa los **ejemplos** (y los tests que tú agregues). Una
solución puede pasarlos y aun así ser incorrecta o lenta en Codeforces. Revisa la explicación en
`ia/log.md`. Si agregas tests propios (`tests/mio1.in` / `.out`), la IA también tiene que pasarlos.

---

## 4. Prueba sin gastar tokens (valida el ciclo ahora mismo)

Hay respuestas simuladas para el problema D (`tools/demo/ia_simulada_D/`): la 1 está mal, la 2 es
correcta pero no usa la plantilla y la 3 es correcta con `PersistentLeftistHeap`.
```
.\eda ia cf710567D --desde tools\demo\ia_simulada_D --como groq --usar PersistentLeftistHeap
```
✅ Esperado:
- intento 1 → `✗ WA` (y le envía el diff del sample1 a la "IA")
- intento 2 → `3/3 tests OK` pero `✗ No usaste las plantillas obligatorias: PersistentLeftistHeap`
- intento 3 → `3/3 tests OK` y `✓ IA resolvió cf710567D en 3 intento(s)`
- `entrega/cf710567D/Main_ia.java` dice `Plantillas incluidas: FastScanner, PersistentLeftistHeap`

En `tools/demo/ia_simulada_D/prompt1.md` queda exactamente lo que se le enviaría a Groq, con su
tamaño estimado en tokens (`--como claude-code` muestra el formato completo).

## 5. Prueba real
Con Groq configurado (o `--proveedor claude-code`), en la página del problema D: Ctrl+A, Ctrl+C, y:
```
.\eda ia cf710567D --clip --usar PersistentLeftistHeap
```

## Si algo falla

| Mensaje | Qué hacer |
|---|---|
| `falta GROQ_API_KEY` / `GROQ_API_KEY inválida` | Sección 1 (y reabre VS Code después de `setx`) |
| `… límite por minuto de Groq, espero N s` | Normal en el plan gratis: espera solo |
| `Groq: límite diario alcanzado` | Usaste el cupo del día: `--proveedor claude-code` o espera |
| `el modelo … no existe o fue retirado` | Groq cambió sus modelos: elige otro en console.groq.com/docs/models |
| `el prompt … no entra en el límite` | Enunciado muy largo: recorta `enunciado.md` a lo esencial |
| `no encuentro Claude Code` | Instálalo (sección 1) y abre una terminal nueva |
| `Claude Code está instalado pero no has iniciado sesión` | Corre `claude` y entra con tu cuenta de claude.ai |
| `no tengo el enunciado` | Usa `--clip` |
| `la IA no logró pasar los tests` | Lee `ia/log.md`; prueba `--effort high`, `--intentos 6` o `--proveedor claude-code` |
