#!/usr/bin/env python3
r"""
eda — asistente de competitiva para el examen de EDA.

  W (trabajo)  : src/problemas/<slug>/JSolution.java   ← aquí programas (el IDE lo compila normal)
  F (entrega)  : entrega/<slug>/Main.java              ← se genera solo, esto es lo que envías
  Plantillas   : src/plantillas/*.java                 ← se incrustan en F solo si W las importa

Comandos (desde la raíz del proyecto:  .\eda <comando>   o   python tools/eda.py <comando>):
  eda                     listener de Competitive Companion + re-render en vivo (déjalo corriendo)
  eda render [slug]       genera F una vez
  eda test   [slug]       genera F, lo compila y lo corre contra los tests de muestra
  eda copy   [slug]       copia F al portapapeles (para pegar en Codeforces)
  eda new <slug>          crea un problema a mano (si Competitive Companion no está disponible)
  eda use <slug>          cambia el problema actual
  eda list                lista los problemas
  eda selftest            verifica las plantillas contra fuerza bruta
  eda demo                (re)crea el problema de práctica demo_pila (ver TUTORIAL.md)
  eda ia     [slug]       la IA resuelve el problema → entrega/<slug>/Main_ia.java (ver TUTORIAL_IA.md)
Sin [slug] se usa el problema actual (el último recibido o el elegido con `eda use`).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
PLANTILLAS = SRC / "plantillas"
PROBLEMAS = SRC / "problemas"
ENTREGA = ROOT / "entrega"
BUILD = ROOT / "build"
TEMPLATE_W = ROOT / "tools" / "JSolution.template"
CURRENT_FILE = ROOT / ".eda_current"
CONFIG_FILE = ROOT / "tools" / "config.json"

W_NAME = "JSolution.java"
W_CLASS = "JSolution"
F_CLASS = "Main"

DEFAULT_CONFIG = {"port": 27121, "watch_interval": 0.4, "run_timeout_s": 10}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
if os.name == "nt":
    os.system("")  # activa colores ANSI en la consola de Windows


def c(text, color):
    codes = {"red": 31, "green": 32, "yellow": 33, "blue": 34, "gray": 90, "bold": 1}
    return f"\033[{codes[color]}m{text}\033[0m"


def config():
    cfg = dict(DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        cfg.update(json.loads(CONFIG_FILE.read_text(encoding="utf-8")))
    return cfg


# ---------------------------------------------------------------------------
# Análisis de código Java (lo justo: comentarios, strings, imports)
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(
    r'//[^\n]*|/\*.*?\*/|"""(?:.|\n)*?"""|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'',
    re.S,
)


def strip_comments_and_strings(code: str) -> str:
    """Devuelve el código sin comentarios ni literales (para buscar nombres sin falsos positivos)."""
    return _TOKEN_RE.sub(lambda m: " " if m.group(0).startswith("/") else '""', code)


_TOPLEVEL_PUBLIC_RE = re.compile(r"^public\s+((?:(?:final|abstract|sealed|non-sealed)\s+)*)(class|interface|record|enum)\b", re.M)


def split_java(code: str):
    """Separa un archivo en (imports, cuerpo) quitando la línea package.
    Solo mira imports/package fuera de comentarios: se compara línea a línea contra una copia del código
    con comentarios y strings reemplazados por espacios (conserva los saltos de línea)."""
    imports = []
    body_lines = []
    clean_lines = _TOKEN_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), code).split("\n")
    for raw, cl in zip(code.split("\n"), clean_lines):
        s = cl.strip()
        m = re.fullmatch(r"import\s+(static\s+)?([\w.]+(?:\.\*)?)\s*;", s)
        if m:
            imports.append(("static " if m.group(1) else "") + m.group(2))
            continue
        if re.fullmatch(r"package\s+[\w.]+\s*;", s):
            continue
        body_lines.append(raw)
    body = "\n".join(body_lines).strip("\n") + "\n"
    return imports, body


def sub_outside_literals(pattern, repl, code):
    """re.sub que no toca strings ni chars literales (sí comentarios)."""
    out, pos = [], 0
    for m in _TOKEN_RE.finditer(code):
        out.append(re.sub(pattern, repl, code[pos:m.start()]))
        lit = m.group(0)
        out.append(lit if lit[0] in "\"'" else re.sub(pattern, repl, lit))
        pos = m.end()
    out.append(re.sub(pattern, repl, code[pos:]))
    return "".join(out)


def template_names():
    return sorted(p.stem for p in PLANTILLAS.glob("*.java"))


def template_deps(name: str, names) -> set:
    """Otras plantillas que usa una plantilla (están en el mismo paquete, así que no llevan import)."""
    code = strip_comments_and_strings((PLANTILLAS / f"{name}.java").read_text(encoding="utf-8"))
    return {o for o in names if o != name and re.search(rf"\b{re.escape(o)}\b", code)}


def resolve_templates(w_code: str):
    """Plantillas que necesita W: imports explícitos de plantillas.X (o plantillas.* → las que aparezcan
    en el código) + sus dependencias transitivas."""
    names = template_names()
    imports, body = split_java(w_code)
    clean_body = strip_comments_and_strings(body)
    wanted = []
    for imp in imports:
        plain = imp.removeprefix("static ")
        if not plain.startswith("plantillas."):
            continue
        rest = plain[len("plantillas."):]
        if rest == "*":
            wanted += [n for n in names if re.search(rf"\b{re.escape(n)}\b", clean_body)]
        else:
            cls = rest.split(".")[0]
            if cls not in names:
                raise SystemExit(c(f"✗ import plantillas.{rest}: no existe src/plantillas/{cls}.java", "red"))
            wanted.append(cls)
    # cierre transitivo, en orden estable
    result, stack = [], list(dict.fromkeys(wanted))
    while stack:
        n = stack.pop(0)
        if n in result:
            continue
        result.append(n)
        stack += sorted(template_deps(n, names) - set(result))
    return result


def render_code(w_code: str, slug: str) -> tuple[str, list]:
    templates = resolve_templates(w_code)
    w_imports, w_body = split_java(w_code)

    imports = [i for i in w_imports if not i.removeprefix("static ").startswith("plantillas.")]
    parts = []
    for t in templates:
        t_imports, t_body = split_java((PLANTILLAS / f"{t}.java").read_text(encoding="utf-8"))
        imports += [i for i in t_imports if not i.removeprefix("static ").startswith("plantillas.")]
        t_body = _TOPLEVEL_PUBLIC_RE.sub(lambda m: m.group(1) + m.group(2), t_body)
        parts.append(f"// ============ plantilla: {t} ============\n{t_body}")

    body = sub_outside_literals(rf"\b{W_CLASS}\b", F_CLASS, w_body)
    imports = sorted(set(imports), key=lambda i: (i.startswith("static "), i))
    header = (
        f"// GENERADO desde src/problemas/{slug}/{W_NAME} — no edites este archivo, edita W.\n"
        f"// Plantillas incluidas: {', '.join(templates) if templates else '(ninguna)'}\n"
    )
    out = header + "".join(f"import {i};\n" for i in imports) + "\n" + body
    for p in parts:
        out += "\n" + p
    return out, templates


# ---------------------------------------------------------------------------
# Problemas
# ---------------------------------------------------------------------------

def w_path(slug):
    return PROBLEMAS / slug / W_NAME


def f_path(slug, ia=False):
    return ENTREGA / slug / ("Main_ia.java" if ia else "Main.java")


def all_slugs():
    return sorted(p.parent.name for p in PROBLEMAS.glob(f"*/{W_NAME}"))


def current_slug(arg=None):
    if arg:
        if not w_path(arg).exists():
            raise SystemExit(c(f"✗ no existe {w_path(arg).relative_to(ROOT)}", "red"))
        return arg
    if CURRENT_FILE.exists():
        s = CURRENT_FILE.read_text(encoding="utf-8").strip()
        if s and w_path(s).exists():
            return s
    slugs = all_slugs()
    if not slugs:
        raise SystemExit(c("✗ no hay problemas todavía (usa Competitive Companion o `eda new <slug>`)", "red"))
    return max(slugs, key=lambda s: w_path(s).stat().st_mtime)


def set_current(slug):
    CURRENT_FILE.write_text(slug, encoding="utf-8")


def render(slug, quiet=False):
    code = w_path(slug).read_text(encoding="utf-8")
    out, templates = render_code(code, slug)
    dest = f_path(slug)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists() or dest.read_text(encoding="utf-8") != out:
        dest.write_text(out, encoding="utf-8")
    if not quiet:
        t = ", ".join(templates) if templates else "sin plantillas"
        print(f"{c('✓', 'green')} {time.strftime('%H:%M:%S')} {dest.relative_to(ROOT)}  [{t}]")
    return dest


def slug_from(data: dict) -> str:
    url = data.get("url", "")
    pats = [
        (r"codeforces\.\w+/(?:contest|problemset/problem)/(\d+)/(?:problem/)?(\w+)", "cf{}{}"),
        (r"codeforces\.\w+/gym/(\d+)/problem/(\w+)", "gym{}{}"),
        (r"codeforces\.\w+/group/\w+/contest/(\d+)/problem/(\w+)", "cf{}{}"),
        (r"atcoder\.jp/contests/[\w-]+/tasks/(\w+)", "{}"),
    ]
    for pat, fmt in pats:
        m = re.search(pat, url)
        if m:
            return re.sub(r"\W", "_", fmt.format(*m.groups()))
    s = re.sub(r"\W+", "_", data.get("name", "problema")).strip("_") or "problema"
    return s if re.match(r"[A-Za-z_]", s) else "p" + s


def create_problem(slug, data=None):
    data = data or {}
    d = PROBLEMAS / slug
    tests = d / "tests"
    tests.mkdir(parents=True, exist_ok=True)
    created = False
    if not w_path(slug).exists():
        w = TEMPLATE_W.read_text(encoding="utf-8")
        for k, v in {
            "SLUG": slug,
            "NAME": data.get("name", slug),
            "URL": data.get("url", ""),
            "TL": data.get("timeLimit", "?"),
            "ML": data.get("memoryLimit", "?"),
        }.items():
            w = w.replace("{{" + k + "}}", str(v))
        w_path(slug).write_text(w, encoding="utf-8")
        created = True
    if data:
        for old in tests.glob("sample*"):
            old.unlink()
        for i, t in enumerate(data.get("tests", []), 1):
            (tests / f"sample{i}.in").write_text(t["input"], encoding="utf-8")
            (tests / f"sample{i}.out").write_text(t["output"], encoding="utf-8")
        (d / "problem.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    set_current(slug)
    render(slug, quiet=True)
    return created


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def _num(tok):
    try:
        return float(tok)
    except ValueError:
        return None


def compare(expected: str, got: str):
    """(ok, nota). Compara por tokens; tolera diferencias de espacios, 1e-6 en reales y mayúsculas en YES/NO."""
    e, g = expected.split(), got.split()
    note = ""
    if len(e) != len(g):
        return False, f"se esperaban {len(e)} tokens, salieron {len(g)}"
    for i, (a, b) in enumerate(zip(e, g)):
        if a == b:
            continue
        if a.lower() == b.lower():
            note = "OK salvo mayúsculas (Codeforces suele aceptarlo en YES/NO, revisa el enunciado)"
            continue
        fa, fb = _num(a), _num(b)
        is_real = "." in a or "e" in a.lower()
        if fa is not None and fb is not None and is_real and abs(fa - fb) <= 1e-6 * max(1.0, abs(fa)):
            continue
        return False, f"token #{i + 1}: se esperaba '{a}', salió '{b}'"
    return True, note


_JDK_BIN = None


def jdk(tool: str) -> str:
    """Ruta real de java/javac. En Windows el `java` del PATH suele ser el launcher de Oracle (javapath),
    que lanza el JVM como OTRO proceso: si lo matamos por timeout, el JVM sigue vivo."""
    global _JDK_BIN
    if _JDK_BIN is None:
        _JDK_BIN = ""
        try:
            r = subprocess.run(["java", "-XshowSettings:properties", "-version"],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
            m = re.search(r"java\.home = (.+)", r.stderr)
            if m and (Path(m.group(1).strip()) / "bin").is_dir():
                _JDK_BIN = str(Path(m.group(1).strip()) / "bin")
        except OSError:
            pass
    exe = Path(_JDK_BIN) / (tool + (".exe" if os.name == "nt" else "")) if _JDK_BIN else None
    return str(exe) if exe and exe.exists() else tool


def run_limited(cmd, inp, timeout):
    """subprocess.run con timeout que mata TODO el árbol de procesos. Devuelve CompletedProcess o None si TLE."""
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, encoding="utf-8", errors="replace")
    try:
        out, err = p.communicate(inp, timeout=timeout)
        return subprocess.CompletedProcess(cmd, p.returncode, out, err)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
        p.kill()
        p.communicate()
        return None


def compile_java(src: Path, out_dir: Path) -> tuple[bool, str]:
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)
    target = src
    if src.name != F_CLASS + ".java":  # p. ej. Main_ia.java: `public class Main` exige llamarse Main.java
        target = out_dir / "_src" / (F_CLASS + ".java")
        target.parent.mkdir()
        shutil.copy(src, target)
    r = subprocess.run([jdk("javac"), "-encoding", "UTF-8", "-d", str(out_dir), str(target)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode == 0, r.stderr.replace(str(target), str(src))


def problem_meta(slug):
    p = PROBLEMAS / slug / "problem.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def run_tests(slug, ia=False, verbose=True) -> tuple[bool, str]:
    """Devuelve (todo_ok, reporte). Si ia=True prueba entrega/<slug>/Main_ia.java."""
    src = f_path(slug, ia) if ia else render(slug, quiet=True)
    if not src.exists():
        raise SystemExit(c(f"✗ no existe {src.relative_to(ROOT)}", "red"))
    out_dir = BUILD / (slug + ("_ia" if ia else ""))
    report = []

    def say(line):
        report.append(re.sub(r"\033\[\d+m", "", line))
        if verbose:
            print(line)

    ok, err = compile_java(src, out_dir)
    if not ok:
        say(c(f"✗ error de compilación en {src.relative_to(ROOT)}", "red"))
        say(err.strip())
        return False, "\n".join(report)

    tests = sorted((PROBLEMAS / slug / "tests").glob("*.in"),
                   key=lambda p: (not p.stem.startswith("sample"),
                                  [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", p.stem)]))
    if not tests:
        say(c("⚠ no hay tests en " + str((PROBLEMAS / slug / "tests").relative_to(ROOT)), "yellow"))
        return False, "\n".join(report)
    tl = problem_meta(slug).get("timeLimit")
    timeout = config()["run_timeout_s"]
    passed = 0
    for tin in tests:
        tout = tin.with_suffix(".out")
        inp = tin.read_text(encoding="utf-8")
        t0 = time.perf_counter()
        p = run_limited([jdk("java"), "-Xss64m", "-cp", str(out_dir), F_CLASS], inp, timeout)
        if p is None:
            say(f"{c('✗ TLE', 'red')} {tin.stem}: más de {timeout}s (¿bucle infinito o esperando input?)")
            continue
        ms = int((time.perf_counter() - t0) * 1000)
        slow = f" {c('(más que el TL de ' + str(tl) + ' ms, ojo: incluye arranque de la JVM)', 'yellow')}" \
            if tl and ms > tl else ""
        if p.returncode != 0:
            say(f"{c('✗ RE', 'red')}  {tin.stem} ({ms} ms){slow}\n{p.stderr.strip()[-1500:]}")
            continue
        if not tout.exists():
            say(f"{c('? --', 'yellow')}  {tin.stem} ({ms} ms) sin .out; salida:\n{p.stdout.rstrip()[:1500]}")
            continue
        ok, note = compare(tout.read_text(encoding="utf-8"), p.stdout)
        if ok:
            passed += 1
            say(f"{c('✓ OK', 'green')}  {tin.stem} ({ms} ms){slow}" + (f"  {c(note, 'yellow')}" if note else ""))
        else:
            say(f"{c('✗ WA', 'red')}  {tin.stem} ({ms} ms): {note}")
            say(c("  entrada:", "gray") + "\n" + _indent(inp))
            say(c("  esperado:", "gray") + "\n" + _indent(tout.read_text(encoding="utf-8")))
            say(c("  obtenido:", "gray") + "\n" + _indent(p.stdout))
            if p.stderr.strip():
                say(c("  stderr:", "gray") + "\n" + _indent(p.stderr))
    all_ok = passed == len(tests)
    say(c(f"{passed}/{len(tests)} tests OK", "green" if all_ok else "red") + f"  → {src.relative_to(ROOT)}")
    return all_ok, "\n".join(report)


def _indent(s, limit=1200):
    s = s.rstrip("\n")
    if len(s) > limit:
        s = s[:limit] + "\n… (recortado)"
    return "\n".join("    " + l for l in s.split("\n"))


# ---------------------------------------------------------------------------
# Listener de Competitive Companion + watcher
# ---------------------------------------------------------------------------

class CCHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        self.send_response(200)
        self.end_headers()
        try:
            data = json.loads(body.decode("utf-8"))
            slug = slug_from(data)
            created = create_problem(slug, data)
            n = len(data.get("tests", []))
            estado = "nuevo" if created else "ya existía: tu código se conserva, tests actualizados"
            print(f"\n{c('▶ ' + data.get('name', slug), 'bold')}  ({estado})")
            print(f"  W: {w_path(slug).relative_to(ROOT)}\n  F: {f_path(slug).relative_to(ROOT)}\n  {n} tests de muestra")
            open_in_editor(w_path(slug))
        except Exception as e:  # nunca tumbar el listener
            print(c(f"✗ error procesando problema: {e}", "red"))

    def log_message(self, *a):
        pass


def open_in_editor(path: Path):
    editor = config().get("open_with")  # "code", "idea", o null
    if editor:
        try:
            subprocess.Popen([editor, str(path)], shell=(os.name == "nt"))
        except OSError:
            pass


def watch_loop(interval):
    seen = {}
    while True:
        try:
            tmpl = max((p.stat().st_mtime for p in PLANTILLAS.glob("*.java")), default=0)
            for slug in all_slugs():
                m = max(w_path(slug).stat().st_mtime, tmpl)
                if seen.get(slug) != m:
                    first = slug not in seen
                    seen[slug] = m
                    try:
                        render(slug, quiet=first)
                    except SystemExit as e:
                        print(e)
        except FileNotFoundError:
            pass  # archivo guardándose en ese instante
        time.sleep(interval)


def cmd_start():
    cfg = config()
    port = cfg["port"]
    try:
        server = HTTPServer(("127.0.0.1", port), CCHandler)
    except OSError:
        raise SystemExit(c(f"✗ el puerto {port} está ocupado (¿otra instancia de eda o la extensión CPH de VS Code?). "
                           f"Cambia 'port' en tools/config.json y agrégalo en Competitive Companion → Custom ports.",
                           "red"))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(c(f"eda escuchando Competitive Companion en el puerto {port}", "bold"))
    print(f"re-render en vivo: {c('src/problemas/*/JSolution.java', 'blue')} → {c('entrega/*/Main.java', 'blue')}")
    print(c("Ctrl+C para salir", "gray"))
    try:
        watch_loop(cfg["watch_interval"])
    except KeyboardInterrupt:
        print("\nchao")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def copy_to_clipboard(path: Path):
    if os.name == "nt":
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        f"Get-Content -Raw -Encoding UTF8 -LiteralPath '{path}' | Set-Clipboard"], check=True)
    else:
        for tool in (["pbcopy"], ["xclip", "-selection", "clipboard"], ["wl-copy"]):
            if shutil.which(tool[0]):
                subprocess.run(tool, input=path.read_text(encoding="utf-8"), text=True, check=True)
                break
        else:
            raise SystemExit("no encontré herramienta de portapapeles")
    print(f"{c('✓', 'green')} {path.relative_to(ROOT)} copiado al portapapeles")


def cmd_selftest():
    out = BUILD / "selftest"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    srcs = [str(p) for p in PLANTILLAS.glob("*.java")] + [str(ROOT / "tests" / "PlantillasTest.java")]
    subprocess.run([jdk("javac"), "-encoding", "UTF-8", "-d", str(out)] + srcs, check=True)
    r = subprocess.run([jdk("java"), "-Dstdout.encoding=UTF-8", "-cp", str(out), "PlantillasTest"])
    sys.exit(r.returncode)


def cmd_demo():
    """(Re)crea el problema de práctica src/problemas/demo_pila con enunciado y tests."""
    import random
    slug = "demo_pila"
    shutil.rmtree(PROBLEMAS / slug, ignore_errors=True)
    shutil.rmtree(ENTREGA / slug, ignore_errors=True)
    create_problem(slug, {"name": "Demo — Pila con historia", "url": "(local) tools/demo/enunciado.md",
                          "timeLimit": 2000, "memoryLimit": 256, "tests": []})
    shutil.copy(ROOT / "tools" / "demo" / "enunciado.md", PROBLEMAS / slug / "enunciado.md")

    def solve(ops):  # referencia en Python: pila persistente como tuplas (valor, siguiente, tamaño)
        ver, out = [None], []
        for op in ops:
            h = ver[op[1]]
            if op[0] == 1:
                ver.append((op[2], h, (h[2] if h else 0) + 1))
            elif op[0] == 2:
                out.append(str(h[0] if h else -1))
                ver.append(h[1] if h else None)
            else:
                out.append(f"{h[0] if h else -1} {h[2] if h else 0}")
                ver.append(h)
        return "\n".join(out) + "\n"

    def gen(q, seed):
        rnd = random.Random(seed)
        ops = []
        for i in range(1, q + 1):
            t, k = rnd.randrange(i), rnd.choice((1, 1, 2, 3))
            ops.append((1, t, rnd.randint(-10**9, 10**9)) if k == 1 else (k, t))
        return ops

    handmade = [(1, 0, 5), (1, 1, 7), (2, 2), (3, 2), (2, 0), (3, 3)]
    for name, ops in (("sample1", handmade), ("random2", gen(25, 7)), ("grande3", gen(200_000, 42))):
        (PROBLEMAS / slug / "tests" / f"{name}.in").write_text(
            f"{len(ops)}\n" + "".join(" ".join(map(str, o)) + "\n" for o in ops), encoding="utf-8")
        (PROBLEMAS / slug / "tests" / f"{name}.out").write_text(solve(ops), encoding="utf-8")
    render(slug)
    print(f"  enunciado: {(PROBLEMAS / slug / 'enunciado.md').relative_to(ROOT)}\n"
          f"  W:         {w_path(slug).relative_to(ROOT)}   ← resuélvelo aquí y corre `eda test`")


def main(argv):
    cmd = argv[0] if argv else "start"
    arg = argv[1] if len(argv) > 1 else None
    flags = {a for a in argv[1:] if a.startswith("--")}
    if arg and arg.startswith("--"):
        arg = next((a for a in argv[2:] if not a.startswith("--")), None)

    if cmd in ("start", "watch"):
        cmd_start()
    elif cmd == "render":
        render(current_slug(arg))
    elif cmd == "test":
        slug = current_slug(arg)
        ok, _ = run_tests(slug, ia="--ia" in flags)
        if ok and "--copy" in flags:
            copy_to_clipboard(f_path(slug, "--ia" in flags))
        sys.exit(0 if ok else 1)
    elif cmd == "copy":
        slug = current_slug(arg)
        copy_to_clipboard(f_path(slug, "--ia" in flags) if "--ia" in flags else render(slug, quiet=True))
    elif cmd == "new":
        if not arg or not re.fullmatch(r"[A-Za-z_]\w*", arg):
            raise SystemExit("uso: eda new <slug>   (slug = identificador Java, ej. cf2043A)")
        create_problem(arg)
        print(f"{c('✓', 'green')} {w_path(arg).relative_to(ROOT)} — agrega tests en "
              f"{(PROBLEMAS / arg / 'tests').relative_to(ROOT)} (1.in / 1.out, ...)")
    elif cmd == "use":
        set_current(current_slug(arg))
        print("problema actual:", current_slug())
    elif cmd == "list":
        cur = current_slug() if all_slugs() else None
        for s in all_slugs():
            print(("→ " if s == cur else "  ") + s)
    elif cmd == "selftest":
        cmd_selftest()
    elif cmd == "demo":
        cmd_demo()
    elif cmd == "ia":
        sys.path.insert(0, str(ROOT / "tools"))
        import ia
        sys.exit(ia.solve(argv[1:]))
    elif cmd in ("-h", "--help", "help"):
        print(__doc__)
    else:
        raise SystemExit(f"comando desconocido: {cmd}\n{__doc__}")


if __name__ == "__main__":
    main(sys.argv[1:])
