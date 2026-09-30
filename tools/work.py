r"""
eda work — resuelve tu problema actual con las plantillas de src/plantillas.
(Motor A principal; motor B de respaldo automático. Detalle de motores: PRIVADO.md.)

  .\eda work                   resuelve el problema: enunciado = portapapeles (si es el de este problema);
                               al terminar deja en el portapapeles lo que va en tu W (imports + solve())
  .\eda work --aplicar         en vez de copiar, escribe la solución en tu W (respaldando lo que tenías)
  .\eda work --completo        deja en el portapapeles Main_w.java completo (sin pasar por tu W)
  .\eda go                     resuelve tu problema y entrégalo: work + aplicar a tu W + probar + copiar Main.java
  .\eda resp                  corrige tu solución con la respuesta del juez que copiaste (work --error + aplicar)
  .\eda work --usar PersistentLeftistHeap[,Otra]   obliga a usar esas plantillas
  .\eda work --clip [--forzar] exige el portapapeles (falla si no parece el enunciado de este problema)
  .\eda work --proveedor <motor> --modelo <versión> --effort <nivel> --intentos 4
  .\eda work --nueva-sesion    abre un hilo nuevo (por defecto continúa el anterior)
  .\eda work --ping            prueba la conexión con una solicitud mínima (no necesita problema)
  .\eda work --desde <carpeta> (pruebas) respuestas desde respuesta1.md, respuesta2.md…, sin gastar cupo
(--solve y --copy siguen funcionando: son lo mismo que el modo por defecto y --completo.)

Enunciado, en este orden: portapapeles · enunciado.md/.txt/.pdf en src/problemas/<slug>/ · la URL del problema.
Salida: entrega/<slug>/Main_w.java, entrega/<slug>/w/JSolution.java (el W del work), w/solve.java.txt y w/log.md.
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
    "w_motor": "claude-code",   # motor principal
    "w_respaldo": "groq",           # motor de respaldo si el principal falla (sin sesión, límite, error): None para desactivar
    "w_version": None,               # None = la de MODELOS según motor
    "w_esfuerzo": None,               # None = el de EFFORT según motor
    "w_intentos": 4,
    "w_max_problemas_hilo": 8,    # motor A: cada cuántos problemas se abre un hilo nuevo
    "respaldo_upm": 8000,       # unidades por minuto que admite el motor de respaldo (ver PRIVADO.md)
    "d_url": "http://localhost:11434",
}
MODELOS = {
    "groq": "openai/gpt-oss-120b",
    "anthropic": "claude-sonnet-5-5",
    "claude-code": "claude-sonnet-5-5",
    "ollama": "qwen2.5-coder:14b",
    "archivo": "",
}
EFFORT = {"groq": "medium", "anthropic": "high", "claude-code": "high"}  # motor B: nivel de esfuerzo (low|medium|high)
PDF_NATIVO = {"anthropic", "claude-code"}           # los demás reciben el PDF convertido a texto
CONTEXTO_COMPLETO = {"anthropic", "claude-code"}    # guía completa de plantillas; los demás, una compacta


LETRAS = {"A": "claude-code", "B": "groq", "C": "anthropic", "D": "ollama"}   # --proveedor A, w_motor "A", …


def cfg():
    d = dict(DEFAULTS)
    d.update({k: v for k, v in E.config().items() if k in DEFAULTS})
    for k in ("w_motor", "w_respaldo"):
        if d[k]:
            d[k] = LETRAS.get(str(d[k]).upper(), d[k])
    return d


def load_secret(name: str) -> str:
    """Clave desde la variable de entorno o, si no existe, desde tools/claves.env (ignorado por git)."""
    v = os.environ.get(name, "").strip()
    if v:
        return v
    f = E.ROOT / "tools" / "claves.env"
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, val = line.split("=", 1)
                if k.strip() == name:
                    return val.strip().strip('"').strip("'")
    return ""


def mot(n):
    """Nombre corto del motor para los mensajes."""
    return {"claude-code": "A", "groq": "B", "anthropic": "C", "ollama": "D", "archivo": "sim"}.get(n, n)


def est_unid(text: str) -> int:
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
        raise SystemExit(c("✗ para leer el PDF con este motor: pip install pypdf  (o usa --clip)", "red"))
    text = "\n".join((p.extract_text() or "") for p in PdfReader(str(pdf)).pages)
    return re.sub(r"[ \t]+\n", "\n", text).strip()


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def looks_like_statement(text: str) -> bool:
    """¿El portapapeles parece el enunciado de un problema (y no código, ni una URL, ni cualquier cosa)?"""
    if len(text) < 120:
        return False
    if re.search(r"\bclass\s+JSolution\b|\bstatic\s+void\s+solve\b|import\s+plantillas\.", text):
        return False  # es la solución que dejó `eda work` en el portapapeles
    return bool(re.search(r"(?i)\b(input|output|entrada|salida)\b", text))


def title_check(slug: str, text: str):
    """(ok, título). Comprueba que el texto mencione el título del problema que recibió Competitive Companion
    (p. ej. 'D. Ejercito supremo' → busca 'ejercito supremo'). Sin título conocido no se puede comprobar."""
    name = E.problem_meta(slug).get("name", "")
    title = re.sub(r"^\s*[A-Za-z0-9]{1,3}\s*[.:)]\s*", "", name).strip()
    if len(title) < 3:
        return True, ""
    return _norm(title) in _norm(text), title


def gather_statement(slug, clip="auto", forzar=False):
    """Devuelve (texto | None, ruta_pdf | None, origen).
    clip='auto': usa el portapapeles solo si parece el enunciado de ESTE problema; si no, busca en archivos.
    clip=True (--clip): exige el portapapeles y falla si no parece el enunciado correcto (salvo --forzar)."""
    d = E.PROBLEMAS / slug
    if clip:
        t = read_clipboard().strip()
        if clip is True:
            if len(t) < 40:
                raise SystemExit(c("✗ el portapapeles está vacío o es muy corto. En la página del problema: "
                                   "Ctrl+A, Ctrl+C", "red"))
            ok, title = title_check(slug, t)
            if not ok and not forzar:
                raise SystemExit(c(f"✗ el portapapeles no menciona «{title}». ¿Copiaste el enunciado de ESTE problema? "
                                   "(en su página: Ctrl+A, Ctrl+C). Si es correcto igual, agrega --forzar", "red"))
        else:
            ok, title = title_check(slug, t)
            if not (looks_like_statement(t) and ok):
                t = ""
                if len(read_clipboard().strip()) >= 120:
                    print(c("  (el portapapeles no parece el enunciado de este problema: lo ignoro)", "yellow"))
        if t:
            (d / "enunciado.md").write_text(t, encoding="utf-8")
            check = (f", verificado: contiene «{title}»" if ok else ", SIN verificar (--forzar)") if title else ""
            return t, None, f"portapapeles{check} (guardado en enunciado.md)"
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
        "✗ no tengo el enunciado. En la página del problema: Ctrl+A, Ctrl+C y vuelve a correr  .\\eda work\n"
        f"   (o guarda el texto en {(d / 'enunciado.md').relative_to(E.ROOT)}, o un .pdf en esa carpeta)", "red"))


# ---------------------------------------------------------------------------
# Encargo
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


def _doc_before(src_lines, i):
    """Comentario (/** */ o //) justo encima de la línea i, en una sola línea de texto."""
    j = i - 1
    while j >= 0 and src_lines[j].strip().startswith("@"):
        j -= 1
    if j < 0:
        return ""
    s = src_lines[j].strip()
    if s.endswith("*/"):
        k = j
        while k >= 0 and "/**" not in src_lines[k]:
            k -= 1
        text = " ".join(re.sub(r"^\s*(?:/\*\*|\*/|\*)\s?|\s*\*/\s*$", "", l).strip() for l in src_lines[max(k, 0):j + 1])
        return re.sub(r"\s+", " ", text).strip()
    return s[2:].strip() if s.startswith("//") else ""


def template_api(name, detailed):
    """Manual de una plantilla: qué es, ejemplo de uso y cada método público con su descripción.
    detailed=False deja solo la primera línea de la descripción y las firmas (para límites de unidades ajustados)."""
    src = (E.PLANTILLAS / f"{name}.java").read_text(encoding="utf-8")
    cls = re.search(r"^public\s+(?:final\s+)?class\s+(\w+(?:<[^>]*>)?)", src, re.M)
    doc = re.search(r"/\*\*(.*?)\*/\s*\npublic", src, re.S)
    lines = [f"class {cls.group(1) if cls else name}"]
    if doc:
        doc_lines = [re.sub(r"^\s*\* ?", "", l).rstrip() for l in doc.group(1).strip("\n").split("\n")]
        doc_lines = doc_lines if detailed else doc_lines[:1]
        lines += ["  // " + l if l else "  //" for l in doc_lines]
    src_lines = src.split("\n")
    for i, line in enumerate(src_lines):
        m = re.match(r"^    (public\s+[^=;{]*\([^)]*\))\s*\{", line)
        if m:
            note = _doc_before(src_lines, i) if detailed else ""
            lines.append(f"  {m.group(1).strip()};" + (f"   // {note}" if note else ""))
    return "\n".join(lines)


def build_system(full: bool, detailed=()) -> str:
    """full=True: guía completa de todas las plantillas. Nunca se envía el código fuente."""
    body = "```java\n" + "\n\n".join(template_api(n, full or n in detailed) for n in E.template_names()
                                      if n != "FastScanner") + "\n```"
    return RULES + "\n\nPlantillas disponibles (paquete `plantillas`). Manual: qué hace cada una, cuándo usarla, " \
                   "y cada método con lo que recibe y devuelve:\n\n" + body


def build_first_message(slug, statement, stmt_source, forced, full, con_w=True):
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
    if full and con_w:
        w = E.w_path(slug).read_text(encoding="utf-8")
        parts.append(f"Plantilla actual de W (src/problemas/{slug}/JSolution.java):\n```java\n{w}\n```")
    if forced:
        parts.append("OBLIGATORIO: la solución debe usar estas plantillas: " + ", ".join(forced) + ".")
    return "\n\n".join(parts)


_ENUNCIADO_RE = re.compile(r"(?i)time limit per test|l[ií]mite de tiempo por test")
_VEREDICTO_RE = re.compile(r"(?i)verdict|judgement protocol|\bTest:\s*#|veredicto")


def read_feedback(nota=""):
    """La respuesta del juez, tal como la copiaste (Ctrl+A, Ctrl+C en el resultado del envío)."""
    fb = read_clipboard().strip()
    if len(fb) < 8:
        raise SystemExit(c("✗ no hay respuesta del juez en el portapapeles: copia el resultado del envío "
                           "(Ctrl+A, Ctrl+C) y repite", "red"))
    if _ENUNCIADO_RE.search(fb) and not _VEREDICTO_RE.search(fb):
        raise SystemExit(c("✗ el portapapeles parece el enunciado, no la respuesta del juez: copia el resultado "
                           "del envío (Ctrl+A, Ctrl+C) y repite", "red"))
    return fb


def judge_case(fb):
    """(entrada, respuesta_correcta | None) del caso que falló, si el veredicto copiado los trae."""
    heads = list(re.finditer(r"(?im)^[ \t]*(Input|Output|Answer|Checker Log|Entrada|Salida|Respuesta)[ \t]*:?[ \t]*$", fb))
    secs = {}
    for k, m in enumerate(heads):
        end = heads[k + 1].start() if k + 1 < len(heads) else len(fb)
        body = re.sub(r"(?m)^[ \t]*```\w*[ \t]*$", "", fb[m.end():end])
        body = "\n".join(l for l in body.split("\n") if l.strip() != "Copy").strip("\n")
        secs.setdefault(m.group(1).lower(), body + "\n" if body.strip() else "")
    return (secs.get("input") or secs.get("entrada") or None), (secs.get("answer") or secs.get("respuesta") or None)


def add_judge_case(slug, fb):
    """Si el veredicto trae entrada y respuesta correcta, queda como test local (juezN) para validar la corrección."""
    inp, ans = judge_case(fb)
    if not inp or not ans:
        return None
    d = E.PROBLEMAS / slug / "tests"
    if any(f.read_text(encoding="utf-8").split() == inp.split() for f in d.glob("*.in")):
        return None
    n = len(list(d.glob("juez*.in"))) + 1
    (d / f"juez{n}.in").write_text(inp, encoding="utf-8")
    (d / f"juez{n}.out").write_text(ans, encoding="utf-8")
    return f"juez{n}"


def build_fix_message(slug, statement, stmt_source, forced, full, fb, nota, w_code):
    base = build_first_message(slug, statement, stmt_source, forced, full, con_w=False)
    lim_fb, lim_code = (8000, 30000) if full else (2500, 6000)
    if len(fb) > lim_fb:
        fb = fb[:lim_fb] + "\n… (recortado)"
    if len(w_code) > lim_code:
        w_code = w_code[:lim_code] + "\n… (recortado)"
    parts = [base,
             f"La solución enviada (src/problemas/{slug}/JSolution.java) fue RECHAZADA por el juez de Codeforces.",
             f"Respuesta del juez:\n```\n{fb}\n```"]
    if nota:
        parts.append("Nota del usuario: " + nota)
    parts += [f"Solución enviada:\n```java\n{w_code}\n```",
              "Encuentra la causa REAL comparando la respuesta del juez con lo que hace el código y con el enunciado "
              "(formato de entrada, límites, casos borde, complejidad, memoria, recursión profunda). Comprueba también "
              "que el código corresponda a ESTE problema y a su formato de entrada. Responde con la causa (breve) y el "
              "archivo JSolution.java COMPLETO corregido en un bloque ```java."]
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
# Motores: send(system, texto, pdf=None) -> texto de la respuesta. Cada uno guarda su historial.
# ---------------------------------------------------------------------------

class MotorB:
    """Motor B (respaldo, sin costo). Credencial: variable del motor B (ver PRIVADO.md).
    Admite pocas unidades por minuto, así que se reenvía solo lo necesario en cada intento."""
    URL = os.environ.get("EDA_GROQ_URL", "https://api.groq.com/openai/v1/chat/completions")  # override solo para pruebas

    def __init__(self, model, effort, tpm):
        self.key = os.environ.get("GROQ_API_KEY", "").strip()
        if not self.key:
            raise SystemExit(c("✗ falta la clave del motor B (ver PRIVADO.md)", "red"))
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
        enc_unid = sum(est_unid(m["content"]) for m in msgs)
        max_out = self.tpm - enc_unid - 300
        if max_out < 1500:
            raise SystemExit(c(f"✗ el encargo (~{enc_unid} unidades) no entra en el límite de {self.tpm} unidades/min "
                               f"del motor B. Acorta enunciado.md o sube 'respaldo_upm' si tu cupo lo permite.", "red"))
        body = {"model": self.model, "messages": msgs, "max_completion_tokens": min(max_out, 32000)}
        if self.model.startswith("openai/gpt-oss") and self.effort:
            body["reasoning_effort"] = self.effort
        print(c(f"  [B · encargo ~{enc_unid} unidades · salida máx {body['max_completion_tokens']}]",
                "gray"))
        data = self._post(body)
        choice = data["choices"][0]
        reply = choice["message"].get("content") or ""
        u = data.get("usage", {})
        self.last_usage = {"in": u.get("prompt_tokens") or 0, "cache": 0, "out": u.get("completion_tokens") or 0, "usd": 0}
        print(c(reply, "gray"))
        print(c(f"  [unidades: entrada {u.get('prompt_tokens')}, salida {u.get('completion_tokens')}; "
                f"fin={choice.get('finish_reason')}]", "gray"))
        if choice.get("finish_reason") == "length":
            print(c("  ⚠ la respuesta se cortó por el límite de unidades (prueba --effort low)", "yellow"))
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
                        raise SystemExit(c(f"✗ motor B: límite diario alcanzado (reintentar en {wait / 60:.0f} min).\n{err}", "red"))
                    print(c(f"  … límite por minuto del motor B, espero {wait:.0f} s", "yellow"))
                    time.sleep(wait + 1)
                    continue
                if e.code == 401:
                    raise SystemExit(c("✗ clave del motor B inválida", "red"))
                if e.code == 413 or "too large" in err.lower():
                    raise SystemExit(c(f"✗ motor B: solicitud demasiado grande para tu límite.\n{err}", "red"))
                if e.code == 404 or "model_not_found" in err or "decommissioned" in err:
                    raise SystemExit(c(f"✗ motor B: la versión {self.model} no existe o fue retirada. "
                                       f"Elige otra con --modelo <versión> (ver PRIVADO.md).\n{err}", "red"))
                raise SystemExit(c(f"✗ motor B respondió {e.code}:\n{err[-2000:]}", "red"))
            except urllib.error.URLError as e:
                raise SystemExit(c(f"✗ sin conexión con el motor B: {e.reason}", "red"))
        raise SystemExit(c("✗ motor B siguió limitando después de varios reintentos", "red"))


class MotorC:
    """Motor C (API directa, de pago). Credencial: variable del motor C (ver PRIVADO.md)."""

    def __init__(self, model, effort):
        try:
            import anthropic
        except ImportError:
            raise SystemExit(c("✗ falta el SDK del motor C (ver PRIVADO.md)", "red"))
        self.anthropic = anthropic
        self.client = anthropic.Anthropic()
        self.model, self.effort = model, effort
        self.system = None
        self.messages = []

    def send(self, system, text, pdf=None):
        if self.system is None:  # fijo durante el hilo (va con caché)
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
            raise SystemExit(c("✗ clave del motor C inválida o ausente (ver PRIVADO.md)", "red"))
        except A.PermissionDeniedError as e:
            raise SystemExit(c(f"✗ la API key no tiene permiso: {e.message}", "red"))
        except A.NotFoundError:
            raise SystemExit(c(f"✗ versión no encontrada: {self.model}", "red"))
        except A.RateLimitError:
            raise SystemExit(c("✗ límite de uso alcanzado (rate limit / saldo). Espera o revisa tu cuenta.", "red"))
        except A.APIStatusError as e:
            raise SystemExit(c(f"✗ error de la API ({e.status_code}): {e.message}", "red"))
        except A.APIConnectionError:
            raise SystemExit(c("✗ sin conexión con el motor C", "red"))
        except TypeError as e:  # el SDK no encontró ninguna credencial
            if "authentication" not in str(e):
                raise
            raise SystemExit(c("✗ no hay credenciales del motor C (ver PRIVADO.md)", "red"))
        if msg.stop_reason == "refusal":
            raise SystemExit(c("✗ el motor rechazó la solicitud", "red"))
        self.messages.append({"role": "assistant", "content": msg.content})
        u = msg.usage
        self.last_usage = {"in": u.input_tokens or 0, "cache": u.cache_read_input_tokens or 0,
                           "out": u.output_tokens or 0, "usd": 0}
        print(c(f"  [unidades: entrada {u.input_tokens} (+{u.cache_read_input_tokens or 0} de caché), "
                f"salida {u.output_tokens}; stop={msg.stop_reason}]", "gray"))
        return "".join(b.text for b in msg.content if b.type == "text")


def buscar_motor_a():
    exe = shutil.which("claude")
    if not exe:  # el instalador nativo lo deja aquí; puede no estar en el PATH de una terminal ya abierta
        p = Path.home() / ".local" / "bin" / ("claude.exe" if os.name == "nt" else "claude")
        exe = str(p) if p.exists() else None
    return exe


class MotorA:
    """Motor A (principal): usa tu cupo, sin clave.

    Hilo continuo: los reintentos de un problema lo continúan y el SIGUIENTE
    problema también, así la guía de plantillas queda en caché y el contexto ya está. Se abre
    un hilo nuevo si cambian las plantillas/versión, cada `max_problemas` problemas, o con --nueva-sesion."""

    def __init__(self, model, effort, max_problemas=8, fresh=False):
        exe = buscar_motor_a()
        if not exe:
            raise SystemExit(c("✗ no encuentro el motor A (instalación y sesión: ver PRIVADO.md)", "red"))
        st = subprocess.run([exe, "auth", "status"], capture_output=True, text=True, encoding="utf-8", errors="replace")
        if st.returncode != 0:
            raise SystemExit(c("✗ el motor A está instalado pero sin sesión iniciada (ver PRIVADO.md)", "red"))
        # --tools Read: solo puede leer archivos (el PDF); --max-turns evita que se quede dando vueltas.
        # --strict-mcp-config sin --mcp-config: no carga conectores MCP (sus definiciones gastan unidades).
        self.base = [exe, "-p", "--output-format", "json", "--tools", "Read", "--max-turns", "8",
                     "--strict-mcp-config"]
        if model:
            self.base += ["--model", model]
        if effort:
            self.base += ["--effort", effort]
        self.model, self.effort = model, effort
        self.max_problemas, self.fresh = max_problemas, fresh
        self.persist = True                       # el ping lo desactiva para no pisar la sesión de trabajo
        self.state_file = E.ROOT / ".eda_w_hilo.json"
        self.session = None
        self.resumed = False                      # ¿este problema continúa una sesión anterior?
        self.first_send = True
        self.sys_file = E.BUILD / "w_encargo.md"

    def _load_state(self):
        try:
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def _call(self, cmd, text):
        r = subprocess.run(cmd + ["Sigue las instrucciones del mensaje recibido por la entrada estándar."],
                           input=text, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=E.ROOT)
        try:
            data = json.loads(r.stdout)
        except json.JSONDecodeError:
            return None, (r.stderr or r.stdout)[-2000:]
        if data.get("is_error"):
            return None, str(data.get("result") or data)
        return data, ""

    def send(self, system, text, pdf=None):
        import hashlib
        sig = hashlib.sha1((system + "|" + str(self.model) + "|" + str(self.effort)).encode()).hexdigest()[:16]
        state = self._load_state()
        if self.first_send and self.persist and not self.fresh and state.get("session") \
                and state.get("sig") == sig and state.get("problemas", 0) < self.max_problemas:
            self.session, self.resumed = state["session"], True
        if pdf:
            text = f"El enunciado está en el PDF {pdf} (léelo con la herramienta Read).\n\n" + text
        if self.resumed and self.first_send and getattr(self, "nuevo_problema", True):
            text = ("NUEVO PROBLEMA (seguimos en la misma sesión: mismas reglas, mismo manual de plantillas, "
                    "mismo formato de respuesta).\n\n" + text)

        def fresh_cmd():
            # REEMPLAZA el encargo de sistema por defecto (muy largo)
            # por el nuestro: gasta mucho menos cupo. Va en archivo porque no cabe en la línea de
            # comandos de Windows.
            self.sys_file.parent.mkdir(parents=True, exist_ok=True)
            self.sys_file.write_text(system + "\n\nSi el enunciado viene en un PDF, léelo con la herramienta Read.",
                                     encoding="utf-8")
            return list(self.base) + ["--system-prompt-file", str(self.sys_file)]

        if self.session:
            data, err = self._call(list(self.base) + ["--resume", self.session], text)
            if data is None and self.resumed and self.first_send:  # la sesión guardada ya no sirve: empieza otra
                print(c("  … no pude continuar la sesión anterior, abro una nueva", "yellow"))
                self.session, self.resumed = None, False
                text = text.split("\n\n", 1)[1] if text.startswith("NUEVO PROBLEMA") else text
        if not self.session:
            data, err = self._call(fresh_cmd(), text)
        if data is None:
            raise SystemExit(c(f"✗ motor A falló (¿sesión iniciada? ¿límite de uso de tu cupo?):\n{err}", "red"))
        self.session = data.get("session_id") or self.session
        if self.persist:
            n = state.get("problemas", 0) if self.resumed else 0
            if self.first_send:
                n += 1
            elif state.get("sig") == sig:
                n = state.get("problemas", 1)
            self.state_file.write_text(json.dumps({"session": self.session, "sig": sig, "problemas": n}), encoding="utf-8")
        self.first_send = False
        reply = data.get("result", "")
        print(c(reply, "gray"))
        cost = data.get("total_cost_usd")
        u = data.get("usage") or {}
        self.last_usage = {"in": u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0),
                           "cache": u.get("cache_read_input_tokens", 0), "out": u.get("output_tokens", 0),
                           "usd": cost or 0}
        toks = (f"entrada {u.get('input_tokens', 0) + u.get('cache_creation_input_tokens', 0)}"
                f" (+{u.get('cache_read_input_tokens', 0)} de caché), salida {u.get('output_tokens', 0)}") if u else ""
        print(c(f"  [A · {data.get('num_turns', '?')} turnos · unidades: {toks}"
                + (f" · equivale a ${cost:.3f} (no se cobra aparte)" if cost else "")
                + "]", "gray"))
        return reply


class MotorD:
    """Motor D (local)."""

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
            raise SystemExit(c(f"✗ no pude hablar con el motor D en {self.url}: {e}", "red"))
        reply = data["message"]["content"]
        self.messages.append({"role": "assistant", "content": reply})
        print(c(reply, "gray"))
        return reply


class MotorSim:
    """Para probar el ciclo sin gastar cupo: responde con <carpeta>/respuesta1.md, respuesta2.md, …
    y guarda en encargo<N>.md lo que se habría enviado (system + mensaje)."""

    def __init__(self, folder):
        self.folder, self.n = Path(folder), 0

    def send(self, system, text, pdf=None):
        self.n += 1
        f = self.folder / f"respuesta{self.n}.md"
        if not f.exists():
            raise SystemExit(c(f"✗ no hay {f}", "red"))
        sent = f"=== SYSTEM (~{est_unid(system)} unidades) ===\n{system}\n\n=== MENSAJE (~{est_unid(text)} unidades) ===\n{text}"
        (self.folder / f"encargo{self.n}.md").write_text(sent, encoding="utf-8")
        return f.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Ciclo principal
# ---------------------------------------------------------------------------

def parse_args(argv):
    opts = {"slug": None, "clip": False, "usar": [], "copy": False, "solve": False, "ping": False,
            "aplicar": False, "completo": False, "forzar": False, "uso": False, "error": False, "nota": ""}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--clip", "--copy", "--solve", "--ping", "--nueva-sesion", "--aplicar", "--completo", "--forzar", "--uso", "--error"):
            opts[a[2:]] = True
        elif a in ("--usar", "--proveedor", "--modelo", "--intentos", "--desde", "--effort", "--como", "--nota"):
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
    for k in ("proveedor", "como"):  # letras de motor: A, B, C, D
        if k in opts:
            opts[k] = LETRAS.get(str(opts[k]).upper(), opts[k])
    return opts


USO_FILE = E.ROOT / ".eda_uso.jsonl"   # una línea por llamada (no se sube a git)


def registrar_uso(slug, proveedor, modelo, intento, usage):
    if not usage:
        return
    rec = {"t": time.strftime("%Y-%m-%d %H:%M:%S"), "slug": slug, "proveedor": proveedor, "modelo": modelo,
           "intento": intento, **usage}
    with USO_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def plan_usage():
    """Consulta cuánto llevas usado de tu cupo (vía el motor A).
    Devuelve dict con session/week (% usado y cuándo se reinicia) y el texto completo; None si no se pudo."""
    exe = buscar_motor_a()
    if not exe:
        return None
    try:
        r = subprocess.run([exe, "-p", "/usage"], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=E.ROOT, timeout=90)
    except (OSError, subprocess.TimeoutExpired):
        return None
    out = r.stdout or ""
    res = {"texto": out}
    for key, label in (("session", r"Current session"), ("week", r"Current week \(all models\)")):
        m = re.search(label + r":\s*(\d+)% used[^\n]*?resets ([^\n]+)", out)
        if m:
            res[key] = (int(m.group(1)), m.group(2).strip())
    return res if ("session" in res or "week" in res) else None


def _fmt(n):
    return f"{n:,}".replace(",", " ")


def uso(argv):
    """`eda uso`: unidades que gastó eda work en esta máquina + cuánto llevas usado de tu cupo."""
    completo = "--completo" in argv
    print(c("> Consumo de eda work (esta máquina)", "bold"))
    recs = []
    if USO_FILE.exists():
        for line in USO_FILE.read_text(encoding="utf-8").splitlines():
            try:
                recs.append(json.loads(line))
            except ValueError:
                pass
    if not recs:
        print("  (todavía no hay llamadas registradas: corre .\\eda work)")
    else:
        hoy = time.strftime("%Y-%m-%d")

        def suma(rs):
            return (len(rs), sum(r.get("in", 0) for r in rs), sum(r.get("cache", 0) for r in rs),
                    sum(r.get("out", 0) for r in rs), sum(r.get("usd", 0) for r in rs))
        n, i, ca, o, usd = suma([r for r in recs if r["t"].startswith(hoy)])
        print(f"  hoy:     {n} llamadas · entrada {_fmt(i)} (+{_fmt(ca)} de caché) · salida {_fmt(o)}"
              + (f" · ≈ ${usd:.2f} equivalente" if usd else ""))
        last = recs[-1]["slug"]
        ult = [r for r in recs if r["slug"] == last][-8:]
        n, i, ca, o, usd = suma(ult)
        print(f"  último:  {last} ({ult[-1]['proveedor']}) · {n} llamadas · entrada {_fmt(i)} (+{_fmt(ca)} de caché)"
              f" · salida {_fmt(o)}" + (f" · ≈ ${usd:.3f} equivalente" if usd else ""))
        print(c("  (\"≈ $\" es un equivalente de referencia; con tu cupo no se cobra: solo gasta de tus límites)", "gray"))
    print(c("\n> Tu cupo (según el motor A)", "bold"))
    pu = plan_usage()
    if not pu:
        print(c("  no pude consultarlo: ¿motor A instalado y con sesión? (ver PRIVADO.md)", "yellow"))
        return 1
    if "session" in pu:
        pct, reset = pu["session"]
        print(f"  Sesión de 5 h:  {pct}% usado → te queda ≈ {100 - pct}%   (se reinicia {reset})")
    if "week" in pu:
        pct, reset = pu["week"]
        print(f"  Semana:         {pct}% usado → te queda ≈ {100 - pct}%   (se reinicia {reset})")
    print(c("  Es el total de tu cuenta (todo lo que uses), no solo eda work.", "gray"))
    if completo:
        print("\n" + pu["texto"])
    return 0


def resumen_uso(tot, antes, o):
    """Cierre de work/go: unidades gastadas en esta resolución y (con --uso) cuánto bajó tu cupo."""
    if not (tot["in"] or tot["out"]):
        return
    print(c(f"\n  gasto de esta resolución: entrada {_fmt(tot['in'])} (+{_fmt(tot['cache'])} de caché), "
            f"salida {_fmt(tot['out'])}" + (f" ≈ ${tot['usd']:.3f} equivalente" if tot["usd"] else ""), "gray"))
    if antes is not None:
        despues = plan_usage()
        if despues and "session" in antes and "session" in despues:
            d = despues["session"][0] - antes["session"][0]
            print(c(f"  tu sesión de 5 h: {antes['session'][0]}% → {despues['session'][0]}% (esta resolución ≈ {d} punto(s)) · "
                    f"te queda ≈ {100 - despues['session'][0]}%, se reinicia {despues['session'][1]}", "gray"))
    else:
        print(c("  cuánto te queda del plan:  .\\eda uso", "gray"))


def w_is_empty(text: str) -> bool:
    """¿El W todavía tiene el solve() vacío de la plantilla (nada tuyo que perder)?"""
    return bool(re.search(r"static\s+void\s+solve\s*\(\s*\)\s*\{\s*\}", E.strip_comments_and_strings(text)))


def apply_to_w(slug, code):
    """Escribe la solución en tu W. Si tu W tenía código, lo guarda antes en un respaldo .txt."""
    w = E.w_path(slug)
    cur = w.read_text(encoding="utf-8")
    backup = None
    if not w_is_empty(cur) and cur != code:
        backup = w.with_name(f"JSolution.{time.strftime('%H%M%S')}.antes.txt")  # .txt: el IDE no lo compila
        backup.write_text(cur, encoding="utf-8")
    w.write_text(code, encoding="utf-8")
    return backup


def entregar(slug, code, f_gen, wdir, snippet, o):
    """Qué pasa con la solución que ya pasó los tests: según el modo pedido."""
    if o["aplicar"]:
        backup = apply_to_w(slug, code)
        print(c("\n✓ solución aplicada a tu W: ", "green") + str(E.w_path(slug).relative_to(E.ROOT)))
        if backup:
            print(f"  (tu W anterior quedó en {backup.relative_to(E.ROOT)})")
    elif o["completo"] or o["copy"]:
        E.copy_to_clipboard(f_gen)
        print("  listo en portapapeles: Main_w.java completo")
    else:
        print(c("\n──── lo que va en tu W ────", "blue") + "\n" + snippet)
        E.copy_to_clipboard(wdir / "solve.java.txt")
        print("  portapapeles: imports + solve() → pégalo en tu JSolution.java y corre  .\\eda test")


def go(argv):
    """Resuelve tu problema y entrégalo: work → aplica a tu W → prueba tu W → copia Main.java para Codeforces."""
    rc = solve(argv + ["--aplicar"])
    if rc != 0:
        return rc
    slug = E.current_slug(parse_args(argv)["slug"])
    print(c("\n── probando tu W con los ejemplos ──", "blue"))
    ok, _ = E.run_tests(slug)
    if not ok:
        print(c("tu W no pasa los tests (ya se había probado: revisa el archivo)", "red"))
        return 1
    E.copy_to_clipboard(E.render(slug, quiet=True))
    print(c(f"\n✓ LISTO: entrega/{slug}/Main.java está en el portapapeles → pégalo en Codeforces (Java 21)", "green"))
    return 0


def resp(argv):
    """Corrige tu solución con la respuesta del juez (portapapeles): work --error → aplica a tu W → prueba → copia Main.java."""
    return go(argv + ["--error"])


def marcar_fallo(slug, msg):
    """Deja el motivo del fallo en tu W (en lugar de la línea //@work), para verlo sin mirar la terminal."""
    w = E.w_path(slug)
    try:
        text = w.read_text(encoding="utf-8")
    except OSError:
        return
    primera = (msg.strip().splitlines() or [""])[0].lstrip("✗ ").strip()  # solo la 1.ª línea, sin la marca ✗
    linea = " ".join(primera.split())[:170]
    aviso = lambda m: f"// work falló: {linea}  (detalle: entrega/{slug}/w/log.md)"  # noqa: E731
    nuevo = E.FIX_RE.sub(aviso, text, count=1)
    if nuevo == text:
        nuevo = E.MARKER_RE.sub(aviso, text, count=1)
    if nuevo != text:
        w.write_text(nuevo, encoding="utf-8")


def trigger(slug, args_text, fix=False):
    """Lo que ejecuta el listener al detectar `//@work [plantillas]` en tu W: es `go` (resuelve → aplica a tu W →
    prueba → copia Main.java). Devuelve (ok, mensaje corto). No lanza excepciones."""
    argv = [slug]
    if fix:  # `//Respuesta: error [nota]`: el texto que sigue es una nota para la corrección
        argv += ["--error"] + (["--nota", args_text] if args_text else [])
    else:
        names = [n for n in re.split(r"[\s,;]+", args_text or "") if n]
        if names:
            argv += ["--usar", ",".join(names)]
    argv += [str(x) for x in E.config().get("trigger_args", [])]
    E.set_current(slug)
    try:
        if go(argv) == 0:
            return True, (f"corregido: entrega/{slug}/Main.java está en el portapapeles y tu JSolution.java ya tiene la corrección"
                          if fix else f"listo: entrega/{slug}/Main.java está en el portapapeles y tu JSolution.java ya tiene la solución")
        msg = f"no salió: los tests siguen fallando (ver entrega/{slug}/w/log.md)"
    except SystemExit as e:
        msg = E.strip_ansi(str(e.code) if e.code not in (None, 0) else "terminó sin resultado")
    except Exception as e:  # noqa: BLE001 — el listener no debe caerse por un error del trabajo
        import traceback
        traceback.print_exc()
        msg = f"error inesperado: {e}"
    marcar_fallo(slug, msg)
    return False, msg


def make_provider(name, o, conf, respaldo=False):
    """respaldo=True: ignora --modelo/--effort/config (que eran del motor principal) y usa los del motor."""
    modelo = MODELOS.get(name, "") if respaldo else (o.get("modelo") or conf["w_version"] or MODELOS.get(name, ""))
    effort = EFFORT.get(name) if respaldo else (o.get("effort") or conf["w_esfuerzo"] or EFFORT.get(name))
    if name == "groq":
        return MotorB(modelo, effort, int(conf["respaldo_upm"])), modelo
    if name == "anthropic":
        return MotorC(modelo, effort), modelo
    if name == "claude-code":
        return MotorA(modelo, effort, int(conf["w_max_problemas_hilo"]),
                                  bool(o.get("nueva-sesion"))), modelo or "(versión de tu cupo)"
    if name == "ollama":
        return MotorD(modelo, conf["d_url"]), modelo
    if name == "archivo":
        return MotorSim(o["desde"]), o["desde"]
    raise SystemExit(f"motor desconocido: {name} (ver PRIVADO.md)")


def solve(argv):
    o = parse_args(argv)
    conf = cfg()
    for name in ("GROQ_API_KEY", "ANTHROPIC_API_KEY"):  # claves de tools/claves.env si no están en el entorno
        v = load_secret(name)
        if v:
            os.environ.setdefault(name, v)
    if o["ping"]:  # prueba la clave/conexión con una solicitud mínima
        name = o.get("proveedor", conf["w_motor"])
        prov, modelo = make_provider(name, o, conf)
        if hasattr(prov, "persist"):
            prov.persist = False  # el ping no debe pisar la sesión de trabajo
        print(c(f"> ping a motor {mot(name)}", "bold"))
        reply = prov.send("Eres un asistente. Responde en una sola palabra.", "Responde exactamente: OK")
        print(c("✓ el motor respondió: " + reply.strip()[:80], "green"))
        return 0
    slug = E.current_slug(o["slug"])
    for u in o["usar"]:
        if u not in E.template_names():
            raise SystemExit(c(f"✗ --usar {u}: no existe src/plantillas/{u}.java", "red"))

    proveedor = "archivo" if o.get("desde") else o.get("proveedor", conf["w_motor"])
    respaldo = None if o.get("proveedor") or o.get("desde") else conf["w_respaldo"]  # --proveedor explícito: sin respaldo
    if respaldo == proveedor or (respaldo and respaldo not in MODELOS):
        respaldo = None
    # "--como groq" junto con --desde: simula el formato del encargo de ese motor
    st = {"estilo": o.get("como", proveedor), "usando_respaldo": False}
    st["full"] = st["estilo"] in CONTEXTO_COMPLETO

    def can_fallback(err):
        if not respaldo or st["usando_respaldo"]:
            return False
        if respaldo == "groq" and not os.environ.get("GROQ_API_KEY"):
            print(c("  (no hay respaldo: falta la clave del motor B; ver PRIVADO.md)", "yellow"))
            return False
        print(err)
        print(c(f"↪ motor {mot(proveedor)} falló: sigo con el respaldo (motor {mot(respaldo)})", "yellow"))
        return True

    def cambiar_a_respaldo():
        st["usando_respaldo"] = True
        st["estilo"], st["full"] = respaldo, respaldo in CONTEXTO_COMPLETO
        return make_provider(respaldo, o, conf, respaldo=True)

    try:
        prov, modelo = make_provider(proveedor, o, conf)
    except SystemExit as e:
        if not can_fallback(e):
            raise
        proveedor = respaldo
        prov, modelo = cambiar_a_respaldo()

    fix = o["error"]
    if fix and hasattr(prov, "nuevo_problema"):
        prov.nuevo_problema = False  # es el mismo problema: el hilo no lo anuncia como nuevo
    statement, pdf, source = gather_statement(slug, False if fix else (True if o["clip"] else "auto"), o["forzar"])
    if pdf and st["estilo"] not in PDF_NATIVO:
        statement, source = pdf_text(pdf), f"{pdf.name} (texto extraído)"
        pdf = None

    wdir = E.ENTREGA / slug / "w"
    wdir.mkdir(parents=True, exist_ok=True)
    w_gen, f_gen, log = wdir / "JSolution.java", E.f_path(slug, gen=True), wdir / "log.md"
    if fix:
        w_code = E.w_path(slug).read_text(encoding="utf-8")
        if w_is_empty(w_code):
            raise SystemExit(c("✗ no hay una solución previa en tu JSolution.java para corregir", "red"))
        fb = read_feedback()
        nuevo_caso = add_judge_case(slug, fb)
        with (wdir / "respuesta_juez.md").open("a", encoding="utf-8") as f:
            f.write(f"## {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n```\n{fb}\n```\n\n")
        with log.open("a", encoding="utf-8") as f:
            f.write(f"\n---\n# corrección {time.strftime('%H:%M:%S')}\nmotor: {mot(proveedor)}\n\n")
    else:
        log.write_text(f"# {slug}\nmotor: {mot(proveedor)} · enunciado: {source}\n\n", encoding="utf-8")
    intentos = int(o.get("intentos", conf["w_intentos"]))

    print(c(f"{'Corregiremos' if fix else 'Resolveremos'} {slug}", "bold") + f"  [{mot(proveedor)}]")
    if fix:
        print(f"  respuesta del juez: {len(fb)} caracteres del portapapeles"
              + (f" · caso agregado a tus tests: {nuevo_caso}" if nuevo_caso else ""))
    print(f"  enunciado: {source}" + (f" · plantillas obligatorias: {', '.join(o['usar'])}" if o["usar"] else ""))

    antes = plan_usage() if o["uso"] and proveedor == "claude-code" else None
    tot = {"in": 0, "cache": 0, "out": 0, "usd": 0}
    detailed = set(o["usar"])  # plantillas cuya guía completa va en el encargo (modo compacto)
    def primer_mensaje():
        if fix:
            return build_fix_message(slug, statement, source, o["usar"], st["full"], fb, o["nota"], w_code)
        return build_first_message(slug, statement, source, o["usar"], st["full"])

    msg = primer_mensaje()
    t0 = time.time()
    for attempt in range(1, intentos + 1):
        print(c(f"\n── intento {attempt}/{intentos} ──", "blue"))
        while True:
            try:
                reply = prov.send(build_system(st["full"], detailed), msg, pdf if attempt == 1 else None)
                break
            except SystemExit as e:
                if not can_fallback(e):
                    raise
                proveedor = respaldo
                prov, modelo = cambiar_a_respaldo()
                if pdf and st["estilo"] not in PDF_NATIVO:
                    statement, source = pdf_text(pdf), f"{pdf.name} (texto extraído)"
                    pdf = None
                msg = primer_mensaje()  # empieza de cero
                with log.open("a", encoding="utf-8") as f:
                    f.write(f"_(cambio a motor {mot(proveedor)})_\n\n")
                print(c(f"  [{mot(proveedor)}]", "gray"))
        limit = 6000 if st["full"] else 1500
        usage = getattr(prov, "last_usage", None)
        registrar_uso(slug, proveedor, modelo, attempt, usage)
        for k in tot:
            tot[k] += (usage or {}).get(k, 0)
        with log.open("a", encoding="utf-8") as f:
            f.write(f"## intento {attempt}\n\n{reply}\n\n")
            if usage:
                f.write(f"_unidades: entrada {usage['in']} (+{usage['cache']} de caché), salida {usage['out']}_\n\n")
        code = extract_java(reply)
        if not code:
            msg = "No encontré un bloque ```java con `class JSolution`. Responde con el archivo completo."
            print(c("✗ la respuesta no trae un bloque ```java con class JSolution", "red"))
            continue
        code = normalize(code, slug)
        w_gen.write_text(code, encoding="utf-8")
        try:
            out, templates = E.render_code(code, slug)
        except SystemExit as e:  # import de una plantilla inexistente
            msg = feedback_message(str(e), limit)
            print(e)
            continue
        detailed |= set(templates) - {"FastScanner"}
        if out.startswith("//"):  # en Main_w.java no va esa línea
            out = out.split("\n", 1)[1]
        f_gen.write_text(out, encoding="utf-8")
        missing = [u for u in o["usar"] if u not in templates]
        ok, report = E.run_tests(slug, gen=True)
        if ok and missing:
            ok, report = False, "No usaste las plantillas obligatorias: " + ", ".join(missing)
            print(c("✗ " + report, "red"))
        with log.open("a", encoding="utf-8") as f:
            f.write(f"### resultado del intento {attempt}\n\n```\n{report}\n```\n\n")
        if ok:
            print(c(f"\n Pasamos test en {slug} en {attempt} intento(s), {time.time() - t0:.0f} s", "green"))
            print(f"  enviar:   {f_gen.relative_to(E.ROOT)}   (plantillas: {', '.join(templates) or 'ninguna'})")
            snippet = solve_snippet(code)
            (wdir / "solve.java.txt").write_text(snippet, encoding="utf-8")
            print(f"  su W:     {w_gen.relative_to(E.ROOT)}\n  solo solve(): {(wdir / 'solve.java.txt').relative_to(E.ROOT)}"
                  f"\n  bitácora: {log.relative_to(E.ROOT)}")
            entregar(slug, code, f_gen, wdir, snippet, o)
            resumen_uso(tot, antes, o)
            return 0
        msg = feedback_message(report, limit)
    print(c(f"\n no logró pasar los tests en {intentos} intentos. Revisa {log.relative_to(E.ROOT)}", "red"))
    return 1


if __name__ == "__main__":
    sys.exit(solve(sys.argv[1:]))
