#!/usr/bin/env python3
"""Web-Frontend fuer den Whitespace-Taschenrechner.

Start:  python web_calc.py
Dann im Browser oeffnen: http://localhost:8000
Das Terminal bleibt sichtbar und loggt jeden Befehl mit.

Nur Standardbibliothek, keine Abhaengigkeiten.
"""
import io
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

BASE = Path(__file__).resolve().parent
CALC_WS = BASE / "calc.ws"

import ws_interpreter  # lokaler Interpreter

with open(CALC_WS, "r", encoding="utf-8") as f:
    PROGRAM = ws_interpreter.parse(f.read())

OP_MAP = {"+": "1", "-": "2", "*": "3", "/": "4", "%": "5",
          "1": "1", "2": "2", "3": "3", "4": "4", "5": "5"}
OP_NAME = {"1": "+", "2": "-", "3": "*", "4": "/", "5": "%"}

PAGE = """<!DOCTYPE html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>WC Taschenrechner (Whitespace)</title>
<style>
body{font-family:Consolas,monospace;max-width:640px;margin:30px auto;padding:0 15px;background:#f4f4f4}
.card{background:#fff;padding:20px;border-radius:10px;box-shadow:0 2px 8px #0002}
input,select,button{font-size:18px;padding:8px;margin:4px}
#opbtns button{width:48px;cursor:pointer}
#opbtns button.sel{background:#007acc;color:#fff}
#res{font-size:28px;font-weight:bold;margin:10px 0}
#console{background:#111;color:#0f0;padding:12px;border-radius:8px;white-space:pre-wrap;min-height:90px}
</style></head><body>
<div class="card">
<h2>WC Taschenrechner (Whitespace)</h2>
<input id="a" type="number" value="10" style="width:110px"> 
<span id="opsign">+</span>
<input id="b" type="number" value="3" style="width:110px">
<div id="opbtns">
<button data-op="1" class="sel">+</button><button data-op="2">-</button><button data-op="3">*</button><button data-op="4">/</button><button data-op="5">%</button>
</div>
<button onclick="calc()">= Rechnen (via calc.ws)</button>
<div id="res">Ergebnis: ...</div>
<h3>Command Prompt (live):</h3>
<div id="console">$ bereit...</div>
</div>
<script>
let op="1";
const names={"1":"+","2":"-","3":"*","4":"/","5":"%"};
document.querySelectorAll("#opbtns button").forEach(b=>b.onclick=()=>{
 document.querySelectorAll("#opbtns button").forEach(x=>x.classList.remove("sel"));
 b.classList.add("sel"); op=b.dataset.op; document.getElementById("opsign").textContent=names[op];});
async function calc(){
 const a=document.getElementById("a").value||"0", b=document.getElementById("b").value||"0";
 const cmd=`printf "${a}\\\\n${b}\\\\n${op}\\\\n" | python ws_interpreter.py calc.ws`;
 document.getElementById("console").textContent="$ "+cmd+"\\n... laeuft ...";
 const r=await fetch(`/api/calc?a=${encodeURIComponent(a)}&b=${encodeURIComponent(b)}&op=${op}`);
 const j=await r.json();
 document.getElementById("res").textContent="Ergebnis: "+j.result.trim()+"  ("+a+" "+names[op]+" "+b+")";
 document.getElementById("console").textContent="$ "+j.command+"\\n"+j.result+(j.stderr?"\\nERR: "+j.stderr:"");
}
</script></body></html>"""


def run_calc(a: str, b: str, op: str):
    op = OP_MAP.get(op, "1")
    # robust: nur ints, sonst 0 (wie Interpreter)
    def to_int(s):
        try:
            return str(int(str(s).strip()))
        except Exception:
            return "0"
    a, b = to_int(a), to_int(b)
    input_text = f"{a}\n{b}\n{op}\n"
    command = f'printf "{a}\\n{b}\\n{op}\\n" | python ws_interpreter.py calc.ws'
    buf = io.StringIO()
    err = ""
    try:
        ws_interpreter.run(PROGRAM, input_text, out=buf)
    except Exception as e:  # z.B. Division durch Null bei fremdem .ws
        err = str(e)
    result = buf.getvalue()
    # --- im echten Terminal (Command Prompt) anzeigen ---
    print(f"$ {command}\n{result.strip()}" + (f"\nERR: {err}" if err else ""), flush=True)
    return result, err, command


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # ruhiger; wir loggen selbst

    def _send(self, body: bytes, ctype="text/html; charset=utf-8"):
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlsplit(self.path)
        if u.path in ("/", "/index.html"):
            self._send(PAGE.encode("utf-8"))
        elif u.path == "/api/calc":
            q = urllib.parse.parse_qs(u.query)
            a = q.get("a", ["0"])[0]
            b = q.get("b", ["0"])[0]
            op = q.get("op", ["1"])[0]
            result, err, command = run_calc(a, b, op)
            self._send(json.dumps({"result": result, "stderr": err,
                                   "command": command}).encode("utf-8"),
                       "application/json")
        else:
            self.send_error(404)


if __name__ == "__main__":
    srv = HTTPServer(("127.0.0.1", 8000), Handler)
    print("WC Taschenrechner Web-UI laeuft auf http://localhost:8000")
    print("Terminal bleibt offen und zeigt jeden Befehl. Strg+C zum Stoppen.", flush=True)
    srv.serve_forever()
