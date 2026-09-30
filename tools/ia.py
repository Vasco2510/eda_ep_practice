r"""
eda ia — un LLM resuelve el problema actual usando las plantillas de src/plantillas.

  .\eda ia                     resuelve el problema actual (proveedor por defecto: groq, gratis)
  .\eda ia --clip              toma el enunciado del portapapeles (Ctrl+A, Ctrl+C en la página del problema)
  .\eda ia --usar PersistentLeftistHeap[,Otra]   obliga a usar esas plantillas
  .\eda ia --proveedor groq|claude-code|anthropic|ollama --modelo <id> --effort <nivel> --intentos 4 --copy
  .\eda ia --clip --solve      al terminar muestra y copia SOLO lo que va en tu W (imports + solve() y auxiliares)
  .\eda ia --ping              prueba la API key con una solicitud mínima (no necesita problema)
  .\eda ia --desde <carpeta>   (pruebas) respuestas desde archivos respuesta1.md, respuesta2.md…, sin gastar tokens

Enunciado, en este orden: --clip · enunciado.md/.txt/.pdf (o cualquier .pdf) en src/problemas/<slug>/ · la URL del problema.
Salida: entrega/<slug>/Main_ia.java (lo que envías), entrega/<slug>/ia/JSolution.java (el W de la IA) y ia/log.md.
"""
import base64
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

import eda as E
from eda import c

DEFAULTS = {
    "ia_proveedor": "groq",
    "ia_modelo": None,      # None = el de MODELOS según proveedor
    "ia_effort": None,      # None = el de EFFORT según proveedor
    "ia_intentos": 4,
    "groq_tpm": 8000,       # tokens por minuto del plan gratis de Groq para el modelo (ver console.groq.com)
    "ollama_url": "http://localhost:11434",
}
MODELOS = {
    "groq": "openai/gpt-oss-120b",
    "anthropic": "claude-opus-5-5",
    "claude-code": "",          # vacío = el modelo por defecto de tu plan
    "ollama": "qwen2.5-coder:14b",
    "archivo": "",
}
EFFORT = {"groq": "medium", "anthropic": "high", "claude-code": "high"}  # groq: reasoning_effort de gpt-oss (low|medium|high)
PDF_NATIVO = {"anthropic", "claude-code"}           # los demás reciben el PDF convertido a texto
CONTEXTO_COMPLETO = {"anthropic", "claude-code"}    # los demás reciben la API compacta de las plantillas


def cfg():
    d = dict(DEFAULTS)
    d.update({k: v for k, v in E.config().items() if k in DEFAULTS})
    return d


def est_tokens(text: str) -> int:
    return int(len(text) / 3.2) + 1


# ---------------------------------------------------------------------------
# Enunciado
# ---------------------------------------------------------------------------

def read_clipboard() -> str:
    if os.name == "nt":
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-Clipboard -Raw"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        return r.stdout
    for tool in (["pbpaste"], ["xclip", "-o", "-selection", "clipboard"], ["wl-paste"]):
        if shutil.which(tool[0]):
            return subprocess.run(tool, capture_output=True, text=True).stdout
    return ""


def fetch_statement(url: str):
    """Intenta bajar el enunciado de Codeforces (funciona en problemas públicos; en grupos pide login)."""
    if "codeforces" not in url:
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        page = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", "replace")
    except Exception:
        return None
    m = re.search(r'<div class="problem-statement">(.*?)</div>\s*</div>\s*<script', page, re.S) or \
        re.search(r'<div class="problem-statement">(.*)', page, re.S)
    if not m:
        return None
    text = re.sub(r"<(br|/p|/div|/li|/pre)[^>]*>", "\n", m.group(1))
    text = html.unescape(re.sub(r"<[^>]+>", "", text)).replace("$$$", "$")
    return re.sub(r"\n{3,}", "\n\n", text).strip()[:20000] or None


def pdf_text(pdf: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        raise SystemExit(c("✗ para leer el PDF con este proveedor: pip install pypdf  (o usa --clip)", "red"))
    text = "\n".join((p.extract_text() or "") for p in PdfReader(str(pdf)).pages)
    return re.sub(r"[ \t]+\n", "\n", text).strip()


def gather_statement(slug, use_clip):
    """Devuelve (texto | None, ruta_pdf | None, origen)."""
    d = E.PROBLEMAS / slug
    if use_clip:
        t = read_clipboard().strip()
        if len(t) < 40:
            raise SystemExit(c("✗ el portapapeles está vacío o es muy corto. En la página del problema: Ctrl+A, Ctrl+C", "red"))
        (d / "enunciado.md").write_text(t, encoding="utf-8")
        return t, None, "portapapeles (guardado en enunciado.md)"
    for name in ("enunciado.md", "enunciado.txt"):
        if (d / name).exists():
            return (d / name).read_text(encoding="utf-8"), None, name
    pdfs = sorted(d.glob("*.pdf"))
    if pdfs:
        return None, pdfs[0], pdfs[0].name
    url = E.problem_meta(slug).get("url", "")
    t = fetch_statement(url)
    if t:
        (d / "enunciado.md").write_text(t, encoding="utf-8")
        return t, None, f"{url} (guardado en enunciado.md)"
    raise SystemExit(c(
        "✗ no tengo el enunciado. Opciones:\n"
        "   · en la página del problema: Ctrl+A, Ctrl+C y corre  .\\eda ia --clip\n"
        f"   · o guarda el texto en {(d / 'enunciado.md').relative_to(E.ROOT)} (o un .pdf en esa carpeta)", "red"))


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

RULES = """Eres un experto en programación competitiva que resuelve problemas de Codeforces en Java 21 \
para un curso de Estructuras de Datos Avanzadas (persistencia).

Formato de respuesta, siempre:
1. Explicación breve en español: idea, por qué es correcta, complejidad frente a los límites.
2. UN solo bloque ```java con el archivo COMPLETO JSolution.java.

Reglas del archivo:
- `package problemas.<slug>;` y `public class JSolution` con `public static void main`.
- Lee con `static FastScanner in = new FastScanner();` (import plantillas.FastScanner; métodos nextInt, nextLong, \
nextDouble, next, nextLine, nextIntArray(n), nextLongArray(n)) y escribe con \
`static PrintWriter out = new PrintWriter(new BufferedOutputStream(System.out));` + `out.flush()` al final.
- Las plantillas se usan con `import plantillas.Nombre;` y SOLO a través de sus métodos/constructores public \
listados (los campos no son accesibles). NO copies su código: un script lo incrusta en el archivo final. \
No inventes métodos que no existen.
- Si una plantilla encaja con la estructura que necesita la solución (heap, pila, cola, BST, segment tree, \
trie, arreglo persistente), úsala en vez de java.util: el curso evalúa su uso.
- Usa long cuando las sumas puedan pasar 2^31. Evita recursión profunda (más de ~10^4 niveles).
- La solución debe ser correcta para TODOS los casos dentro de los límites, no solo para los ejemplos."""


def template_api(name, detailed):
    """Firma pública de una plantilla: descripción de 1 línea (o el comentario completo si detailed) + métodos."""
    src = (E.PLANTILLAS / f"{name}.java").read_text(encoding="utf-8")
    cls = re.search(r"^public\s+(?:final\s+)?class\s+(\w+(?:<[^>]*>)?)", src, re.M)
    doc = re.search(r"/\*\*(.*?)\*/\s*\npublic", src, re.S)
    lines = [f"class {cls.group(1) if cls else name}"]
    if doc:
        doc_lines = [re.sub(r"^\s*\* ?", "", l).rstrip() for l in doc.group(1).strip("\n").split("\n")]
        doc_lines = doc_lines if detailed else doc_lines[:1]
        lines += ["  // " + l if l else "  //" for l in doc_lines]
    lines += [f"  {m.group(1).strip()};"
              for m in re.finditer(r"^    (public\s+[^=;{]*\([^)]*\))\s*\{", src, re.M)]
    return "\n".join(lines)


def build_system(full: bool, detailed=()) -> str:
    if full:
        body = "\n\n".join(f"### plantillas/{n}.java\n```java\n"
                           f"{(E.PLANTILLAS / f'{n}.java').read_text(encoding='utf-8')}\n```"
                           for n in E.template_names())
    else:
        body = "```java\n" + "\n\n".join(template_api(n, n in detailed) for n in E.template_names()
                                          if n != "FastScanner") + "\n```"
    return RULES + "\n\nPlantillas disponibles (paquete `plantillas`):\n\n" + body


def build_first_message(slug, statement, stmt_source, forced, full):
    meta = E.problem_meta(slug)
    tests = []
    for tin in sorted((E.PROBLEMAS / slug / "tests").glob("sample*.in"))[:3 if full else 2]:
        tout = tin.with_suffix(".out")
        inp = tin.read_text(encoding="utf-8")
        if len(inp) > (3000 if full else 800):
            continue
        tests.append(f"Entrada:\n```\n{inp.rstrip()}\n```\nSalida esperada:\n```\n"
                     f"{tout.read_text(encoding='utf-8').rstrip() if tout.exists() else '(desconocida)'}\n```")
    if statement and not full and len(statement) > 9000:
        statement = statement[:9000] + "\n… (recortado)"
    parts = [
        f"Problema: {meta.get('name', slug)}  (slug: {slug})",
        f"Límites: {meta.get('timeLimit', '?')} ms, {meta.get('memoryLimit', '?')} MB",
        f"Enunciado (fuente: {stmt_source}):\n" + (statement if statement else "(adjunto en el PDF)"),
        "Ejemplos:\n" + ("\n\n".join(tests) if tests else "(no hay)"),
    ]
    if full:
        w = E.w_path(slug).read_text(encoding="utf-8")
        parts.append(f"Plantilla actual de W (src/problemas/{slug}/JSolution.java):\n```java\n{w}\n```")
    if forced:
        parts.append("OBLIGATORIO: la solución debe usar estas plantillas: " + ", ".join(forced) + ".")
    return "\n\n".join(parts)


def feedback_message(report, limit=6000):
    if len(report) > limit:  # los samples van primero: se conserva el inicio
        report = report[:limit] + "\n… (recortado)"
    return ("Tu solución falló al compilar o al correr los tests locales. Reporte:\n```\n" + report +
            "\n```\nEncuentra la causa (no solo el síntoma), revisa si la idea es correcta y responde con la "
            "explicación corregida y el archivo JSolution.java COMPLETO en un bloque ```java.")


def extract_java(reply: str):
    blocks = re.findall(r"```java\s*\n(.*?)```", reply, re.S)
    blocks = [b for b in blocks if re.search(r"\bclass\s+JSolution\b", b)]
    return blocks[-1] if blocks else None


def solve_snippet(code: str) -> str:
    """Solo lo que tú pegarías en tu W: imports extra + miembros de JSolution salvo `in`, `out` y `main`
    (solve() y sus funciones/clases auxiliares). Avisa si main() lee varios casos."""
    clean = E._TOKEN_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), code)  # mismo largo, sin literales
    m = re.search(r"\bclass\s+JSolution\b[^{]*\{", clean)
    if not m:
        return code
    members, depth, seg = [], 1, m.end()
    for i in range(m.end(), len(clean)):
        ch = clean[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
            if depth == 1:
                members.append(code[seg:i + 1]); seg = i + 1
        elif ch == ";" and depth == 1:
            members.append(code[seg:i + 1]); seg = i + 1
    keep, multi = [], False
    for mem in members:
        body = E.strip_comments_and_strings(mem)
        if re.search(r"\bFastScanner\s+in\b|\bPrintWriter\s+out\b", body):
            continue
        if re.search(r"\bvoid\s+main\s*\(", body):
            multi = bool(re.search(r"\bt\s*=\s*in\.next(Int|Long)\s*\(", body))
            continue
        keep.append(mem.strip("\n"))
    imports = [l.strip() for l in code.splitlines()
               if re.match(r"\s*import\s", l) and "plantillas.FastScanner" not in l
               and l.strip() not in ("import java.io.*;", "import java.util.*;")]
    head = [f"// imports (van arriba, junto a los tuyos):"] + imports if imports else []
    note = ["// en main(): descomenta  t = in.nextInt();  (varios casos de prueba)"] if multi else []
    return "\n".join(head + note + [""] + [k for k in keep if k.strip()]).strip("\n") + "\n"


def normalize(code, slug):
    code = re.sub(r"^\s*package\s+[\w.]+\s*;", f"package problemas.{slug};", code, count=1, flags=re.M)
    if not re.search(r"^\s*package\s", code, re.M):
        code = f"package problemas.{slug};\n\n" + code
    return code.rstrip() + "\n"


# ---------------------------------------------------------------------------
# Proveedores: send(system, texto, pdf=None) -> texto de la respuesta. Cada uno guarda su historial.
# ---------------------------------------------------------------------------

class GroqProvider:
    """Groq (plan gratis): API compatible con OpenAI. Credencial: GROQ_API_KEY.
    El plan gratis limita tokens por minuto, así que se reenvía solo lo necesario en cada intento."""
    URL = os.environ.get("EDA_GROQ_URL", "https://api.groq.com/openai/v1/chat/completions")  # override solo para pruebas

    def __init__(self, model, effort, tpm):
        self.key = os.environ.get("GROQ_API_KEY", "").strip()
        if not self.key:
            raise SystemExit(c("✗ falta GROQ_API_KEY (créala gratis en console.groq.com; ver TUTORIAL_IA.md)", "red"))
        self.model, self.effort, self.tpm = model, effort, tpm
        self.first = None
        self.last_code = None

    def send(self, system, text, pdf=None):
        if self.first is None:
            self.first = text
            msgs = [{"role": "user", "content": text}]
        else:  # historial recortado: enunciado + su último código + el error
            msgs = [{"role": "user", "content": self.first},
                    {"role": "assistant", "content": f"```java\n{self.last_code or '(sin código)'}\n```"},
                    {"role": "user", "content": text}]
        msgs.insert(0, {"role": "system", "content": system})
        prompt_tokens = sum(est_tokens(m["content"]) for m in msgs)
        max_out = self.tpm - prompt_tokens - 300
        if max_out < 1500:
            raise SystemExit(c(f"✗ el prompt (~{prompt_tokens} tokens) no entra en el límite de {self.tpm} tokens/min "
                               f"de Groq. Acorta enunciado.md o sube 'groq_tpm' si tu plan lo permite.", "red"))
        body = {"model": self.model, "messages": msgs, "max_completion_tokens": min(max_out, 32000)}
        if self.model.startswith("openai/gpt-oss") and self.effort:
            body["reasoning_effort"] = self.effort
        print(c(f"  [groq · {self.model} · prompt ~{prompt_tokens} tokens · salida máx {body['max_completion_tokens']}]",
                "gray"))
        data = self._post(body)
        choice = data["choices"][0]
        reply = choice["message"].get("content") or ""
        u = data.get("usage", {})
        print(c(reply, "gray"))
        print(c(f"  [tokens: entrada {u.get('prompt_tokens')}, salida {u.get('completion_tokens')}; "
                f"fin={choice.get('finish_reason')}]", "gray"))
        if choice.get("finish_reason") == "length":
            print(c("  ⚠ la respuesta se cortó por el límite de tokens (prueba --effort low)", "yellow"))
        code = extract_java(reply)
        if code:
            self.last_code = code
        return reply

    def _post(self, body):
        payload = json.dumps(body).encode()
        for intento in range(6):
            req = urllib.request.Request(self.URL, data=payload, headers={
                "Authorization": f"Bearer {self.key}", "Content-Type": "application/json",
                "User-Agent": "eda-cli/1.0"})
            try:
                return json.loads(urllib.request.urlopen(req, timeout=300).read())
            except urllib.error.HTTPError as e:
                err = e.read().decode("utf-8", "replace")
                if e.code == 429:
                    m = re.search(r"try again in (?:(\d+)m)?([\d.]+)s", err)
                    wait = float(e.headers.get("retry-after") or 0) or \
                        ((int(m.group(1) or 0) * 60 + float(m.group(2))) if m else 20)
                    if wait > 120:
                        raise SystemExit(c(f"✗ Groq: límite diario alcanzado (reintentar en {wait / 60:.0f} min).\n{err}", "red"))
                    print(c(f"  … límite por minuto de Groq, espero {wait:.0f} s", "yellow"))
                    time.sleep(wait + 1)
                    continue
                if e.code == 401:
                    raise SystemExit(c("✗ GROQ_API_KEY inválida", "red"))
                if e.code == 413 or "too large" in err.lower():
                    raise SystemExit(c(f"✗ Groq: solicitud demasiado grande para tu límite.\n{err}", "red"))
                if e.code == 404 or "model_not_found" in err or "decommissioned" in err:
                    raise SystemExit(c(f"✗ Groq: el modelo {self.model} no existe o fue retirado. "
                                       f"Mira console.groq.com/docs/models y usa --modelo <id>.\n{err}", "red"))
                raise SystemExit(c(f"✗ Groq respondió {e.code}:\n{err[-2000:]}", "red"))
            except urllib.error.URLError as e:
                raise SystemExit(c(f"✗ sin conexión con api.groq.com: {e.reason}", "red"))
        raise SystemExit(c("✗ Groq siguió limitando después de varios reintentos", "red"))


class AnthropicProvider:
    """API de Claude con el SDK oficial (pip install anthropic). Credencial: ANTHROPIC_API_KEY. De pago."""

    def __init__(self, model, effort):
        try:
            import anthropic
        except ImportError:
            raise SystemExit(c("✗ falta el SDK: pip install anthropic", "red"))
        self.anthropic = anthropic
        self.client = anthropic.Anthropic()
        self.model, self.effort = model, effort
        self.system = None
        self.messages = []

    def send(self, system, text, pdf=None):
        if self.system is None:  # fijo durante la conversación (va con caché)
            self.system = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
        content = []
        if pdf:
            content.append({"type": "document", "source": {
                "type": "base64", "media_type": "application/pdf",
                "data": base64.standard_b64encode(pdf.read_bytes()).decode()}})
        content.append({"type": "text", "text": text})
        self.messages.append({"role": "user", "content": content})
        A = self.anthropic
        try:
            with self.client.beta.messages.stream(
                model=self.model,
                max_tokens=64000,
                system=self.system,
                messages=self.messages,
                output_config={"effort": self.effort},
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            ) as stream:
                for chunk in stream.text_stream:
                    print(c(chunk, "gray"), end="", flush=True)
                msg = stream.get_final_message()
            print()
        except A.AuthenticationError:
            raise SystemExit(c("✗ API key inválida o ausente. Define ANTHROPIC_API_KEY (ver TUTORIAL_IA.md)", "red"))
        except A.PermissionDeniedError as e:
            raise SystemExit(c(f"✗ la API key no tiene permiso: {e.message}", "red"))
        except A.NotFoundError:
            raise SystemExit(c(f"✗ modelo no encontrado: {self.model}", "red"))
        except A.RateLimitError:
            raise SystemExit(c("✗ límite de uso alcanzado (rate limit / saldo). Espera o revisa tu cuenta.", "red"))
        except A.APIStatusError as e:
            raise SystemExit(c(f"✗ error de la API ({e.status_code}): {e.message}", "red"))
        except A.APIConnectionError:
            raise SystemExit(c("✗ sin conexión con api.anthropic.com", "red"))
        except TypeError as e:  # el SDK no encontró ninguna credencial
            if "authentication" not in str(e):
                raise
            raise SystemExit(c("✗ no hay credenciales de Claude: define ANTHROPIC_API_KEY (ver TUTORIAL_IA.md)", "red"))
        if msg.stop_reason == "refusal":
            raise SystemExit(c("✗ el modelo rechazó la solicitud", "red"))
        self.messages.append({"role": "assistant", "content": msg.content})
        u = msg.usage
        print(c(f"  [tokens: entrada {u.input_tokens} (+{u.cache_read_input_tokens or 0} de caché), "
                f"salida {u.output_tokens}; stop={msg.stop_reason}]", "gray"))
        return "".join(b.text for b in msg.content if b.type == "text")


def find_claude():
    exe = shutil.which("claude")
    if not exe:  # el instalador nativo lo deja aquí; puede no estar en el PATH de una terminal ya abierta
        p = Path.home() / ".local" / "bin" / ("claude.exe" if os.name == "nt" else "claude")
        exe = str(p) if p.exists() else None
    return exe


class ClaudeCodeProvider:
    """Claude Code en modo no interactivo (`claude -p`): usa tu cuenta/plan de Claude, sin API key.
    El primer intento abre una sesión y los reintentos la continúan (--resume)."""

    def __init__(self, model, effort):
        exe = find_claude()
        if not exe:
            raise SystemExit(c("✗ no encuentro Claude Code. Instálalo en PowerShell con:\n"
                               "    irm https://claude.ai/install.ps1 | iex\n"
                               "  y luego corre `claude` una vez para iniciar sesión (ver TUTORIAL_IA.md)", "red"))
        st = subprocess.run([exe, "auth", "status"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if st.returncode != 0:
            raise SystemExit(c("✗ Claude Code está instalado pero no has iniciado sesión: corre `claude` "
                               "(o `claude auth login`) y entra con tu cuenta de claude.ai", "red"))
        # --tools Read: solo puede leer archivos (el PDF); --max-turns evita que se quede dando vueltas.
        # --strict-mcp-config sin --mcp-config: no carga conectores MCP (sus definiciones gastan tokens).
        self.base = [exe, "-p", "--output-format", "json", "--tools", "Read", "--max-turns", "8",
                     "--strict-mcp-config"]
        if model:
            self.base += ["--model", model]
        if effort:
            self.base += ["--effort", effort]
        self.session = None
        self.sys_file = E.BUILD / "ia_system_prompt.md"

    def send(self, system, text, pdf=None):
        cmd = list(self.base)
        if self.session:
            cmd += ["--resume", self.session]
        else:
            # REEMPLAZA el prompt de sistema de Claude Code (agente de programación + herramientas, muy largo)
            # por el nuestro: gasta mucho menos del plan. Va en archivo porque no cabe en la línea de
            # comandos de Windows.
            self.sys_file.parent.mkdir(parents=True, exist_ok=True)
            self.sys_file.write_text(system + "\n\nSi el enunciado viene en un PDF, léelo con la herramienta Read.",
                                     encoding="utf-8")
            cmd += ["--system-prompt-file", str(self.sys_file)]
        if pdf:
            text = f"El enunciado está en el PDF {pdf} (léelo con la herramienta Read).\n\n" + text
        # el mensaje va por stdin; el argumento solo le indica que lo siga
        cmd += ["Sigue las instrucciones del mensaje recibido por la entrada estándar."]
        r = subprocess.run(cmd, input=text, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=E.ROOT)
        try:
            data = json.loads(r.stdout)
        except json.JSONDecodeError:
            raise SystemExit(c(f"✗ claude -p falló (¿iniciaste sesión con `claude`?):\n{(r.stderr or r.stdout)[-2000:]}", "red"))
        if data.get("is_error"):
            raise SystemExit(c(f"✗ Claude Code: {data.get('result') or data}", "red"))
        self.session = data.get("session_id") or self.session
        reply = data.get("result", "")
        print(c(reply, "gray"))
        cost = data.get("total_cost_usd")
        u = data.get("usage") or {}
        toks = (f"entrada {u.get('input_tokens', 0) + u.get('cache_creation_input_tokens', 0)}"
                f" (+{u.get('cache_read_input_tokens', 0)} de caché), salida {u.get('output_tokens', 0)}") if u else ""
        print(c(f"  [claude code · {data.get('num_turns', '?')} turnos · tokens: {toks}"
                + (f" · consumo de tu plan equivalente a ${cost:.3f} de API (no se cobra aparte)" if cost else "")
                + "]", "gray"))
        return reply


class OllamaProvider:
    """Modelo local con Ollama (https://ollama.com)."""

    def __init__(self, model, url):
        self.model, self.url = model, url.rstrip("/")
        self.messages = None

    def send(self, system, text, pdf=None):
        if self.messages is None:
            self.messages = [{"role": "system", "content": system}]
        self.messages.append({"role": "user", "content": text})
        body = json.dumps({"model": self.model, "messages": self.messages, "stream": False}).encode()
        req = urllib.request.Request(self.url + "/api/chat", data=body, headers={"Content-Type": "application/json"})
        try:
            data = json.loads(urllib.request.urlopen(req, timeout=1800).read())
        except Exception as e:
            raise SystemExit(c(f"✗ no pude hablar con Ollama en {self.url}: {e}", "red"))
        reply = data["message"]["content"]
        self.messages.append({"role": "assistant", "content": reply})
        print(c(reply, "gray"))
        return reply


class FileProvider:
    """Para probar el ciclo sin gastar tokens: responde con <carpeta>/respuesta1.md, respuesta2.md, …
    y guarda en prompt<N>.md lo que se habría enviado (system + mensaje)."""

    def __init__(self, folder):
        self.folder, self.n = Path(folder), 0

    def send(self, system, text, pdf=None):
        self.n += 1
        f = self.folder / f"respuesta{self.n}.md"
        if not f.exists():
            raise SystemExit(c(f"✗ no hay {f}", "red"))
        sent = f"=== SYSTEM (~{est_tokens(system)} tokens) ===\n{system}\n\n=== MENSAJE (~{est_tokens(text)} tokens) ===\n{text}"
        (self.folder / f"prompt{self.n}.md").write_text(sent, encoding="utf-8")
        return f.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Ciclo principal
# ---------------------------------------------------------------------------

def parse_args(argv):
    opts = {"slug": None, "clip": False, "usar": [], "copy": False, "solve": False, "ping": False}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--clip", "--copy", "--solve", "--ping"):
            opts[a[2:]] = True
        elif a in ("--usar", "--proveedor", "--modelo", "--intentos", "--desde", "--effort", "--como"):
            if i + 1 >= len(argv):
                raise SystemExit(f"falta el valor de {a}")
            opts[a[2:]] = argv[i + 1]
            i += 1
        elif not a.startswith("--"):
            opts["slug"] = a
        else:
            raise SystemExit(f"opción desconocida: {a}\n{__doc__}")
        i += 1
    if isinstance(opts["usar"], str):
        opts["usar"] = [u.strip() for u in opts["usar"].split(",") if u.strip()]
    return opts


def make_provider(name, o, conf):
    modelo = o.get("modelo") or conf["ia_modelo"] or MODELOS.get(name, "")
    effort = o.get("effort") or conf["ia_effort"] or EFFORT.get(name)
    if name == "groq":
        return GroqProvider(modelo, effort, int(conf["groq_tpm"])), modelo
    if name == "anthropic":
        return AnthropicProvider(modelo, effort), modelo
    if name == "claude-code":
        return ClaudeCodeProvider(modelo, effort), modelo or "(modelo de tu plan)"
    if name == "ollama":
        return OllamaProvider(modelo, conf["ollama_url"]), modelo
    if name == "archivo":
        return FileProvider(o["desde"]), o["desde"]
    raise SystemExit(f"proveedor desconocido: {name} (groq | claude-code | anthropic | ollama)")


def solve(argv):
    o = parse_args(argv)
    conf = cfg()
    if o["ping"]:  # prueba la clave/conexión con una solicitud mínima
        name = o.get("proveedor", conf["ia_proveedor"])
        prov, modelo = make_provider(name, o, conf)
        print(c(f"▶ ping a {name} · {modelo}", "bold"))
        reply = prov.send("Eres un asistente. Responde en una sola palabra.", "Responde exactamente: OK")
        print(c("✓ el proveedor respondió: " + reply.strip()[:80], "green"))
        return 0
    slug = E.current_slug(o["slug"])
    for u in o["usar"]:
        if u not in E.template_names():
            raise SystemExit(c(f"✗ --usar {u}: no existe src/plantillas/{u}.java", "red"))

    proveedor = "archivo" if o.get("desde") else o.get("proveedor", conf["ia_proveedor"])
    # "--como groq" junto con --desde: simula el formato de prompt de ese proveedor
    estilo = o.get("como", proveedor)
    full = estilo in CONTEXTO_COMPLETO
    prov, modelo = make_provider(proveedor, o, conf)

    statement, pdf, source = gather_statement(slug, o["clip"])
    if pdf and estilo not in PDF_NATIVO:
        statement, source = pdf_text(pdf), f"{pdf.name} (texto extraído)"
        pdf = None

    ia_dir = E.ENTREGA / slug / "ia"
    ia_dir.mkdir(parents=True, exist_ok=True)
    w_ia, f_ia, log = ia_dir / "JSolution.java", E.f_path(slug, ia=True), ia_dir / "log.md"
    log.write_text(f"# IA — {slug}\nproveedor: {proveedor} · modelo: {modelo} · enunciado: {source}\n\n", encoding="utf-8")
    intentos = int(o.get("intentos", conf["ia_intentos"]))

    print(c(f"▶ IA resolviendo {slug}", "bold") + f"  [{proveedor} · {modelo}]")
    print(f"  enunciado: {source}" + (f" · plantillas obligatorias: {', '.join(o['usar'])}" if o["usar"] else ""))

    detailed = set(o["usar"])  # plantillas cuyo ejemplo de uso completo va en el prompt (modo compacto)
    msg = build_first_message(slug, statement, source, o["usar"], full)
    t0 = time.time()
    for attempt in range(1, intentos + 1):
        print(c(f"\n── intento {attempt}/{intentos} ──", "blue"))
        reply = prov.send(build_system(full, detailed), msg, pdf if attempt == 1 else None)
        with log.open("a", encoding="utf-8") as f:
            f.write(f"## intento {attempt}\n\n{reply}\n\n")
        code = extract_java(reply)
        if not code:
            msg = "No encontré un bloque ```java con `class JSolution`. Responde con el archivo completo."
            print(c("✗ la respuesta no trae un bloque ```java con class JSolution", "red"))
            continue
        code = normalize(code, slug)
        w_ia.write_text(code, encoding="utf-8")
        try:
            out, templates = E.render_code(code, slug)
        except SystemExit as e:  # import de una plantilla inexistente
            msg = feedback_message(str(e), 6000 if full else 1500)
            print(e)
            continue
        detailed |= set(templates) - {"FastScanner"}
        if out.startswith("// GENERADO desde"):  # en Main_ia.java no va esa línea
            out = out.split("\n", 1)[1]
        f_ia.write_text(out, encoding="utf-8")
        missing = [u for u in o["usar"] if u not in templates]
        ok, report = E.run_tests(slug, ia=True)
        if ok and missing:
            ok, report = False, "No usaste las plantillas obligatorias: " + ", ".join(missing)
            print(c("✗ " + report, "red"))
        with log.open("a", encoding="utf-8") as f:
            f.write(f"### resultado del intento {attempt}\n\n```\n{report}\n```\n\n")
        if ok:
            print(c(f"\n✓ IA resolvió {slug} en {attempt} intento(s), {time.time() - t0:.0f} s", "green"))
            print(f"  enviar:   {f_ia.relative_to(E.ROOT)}   (plantillas: {', '.join(templates) or 'ninguna'})")
            snippet = solve_snippet(code)
            (ia_dir / "solve.java.txt").write_text(snippet, encoding="utf-8")
            print(f"  su W:     {w_ia.relative_to(E.ROOT)}\n  solo solve(): {(ia_dir / 'solve.java.txt').relative_to(E.ROOT)}"
                  f"\n  bitácora: {log.relative_to(E.ROOT)}")
            if o["solve"]:
                print(c("\n──── lo que va en tu W ────", "blue") + "\n" + snippet)
                E.copy_to_clipboard(ia_dir / "solve.java.txt")
            elif o["copy"]:
                E.copy_to_clipboard(f_ia)
            return 0
        msg = feedback_message(report, 6000 if full else 1500)
    print(c(f"\n✗ la IA no logró pasar los tests en {intentos} intentos. Revisa {log.relative_to(E.ROOT)}", "red"))
    return 1


if __name__ == "__main__":
    sys.exit(solve(sys.argv[1:]))
