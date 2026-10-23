#!/usr/bin/env python3
"""Tableau de bord leger pour tablette ancienne (Chrome 59+). Python 3.7+, aucune dependance.
Configuration : voir dashboard.env.example. Aucun secret dans ce fichier."""
import json, os, ssl, subprocess, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, urlopen

# Configuration lue dans l'environnement (fichier /etc/dashboard.env via systemd).
PVE = os.environ.get("PVE_URL", "https://192.168.1.18:8006")
NODE = os.environ.get("PVE_NODE", "pve-01")
TOKEN = os.environ.get("PVE_TOKEN", "")   # dashboard@pve!tablet=SECRET
PING = {}                                 # "Box=192.168.1.254,PC=192.168.1.30"
for _pair in os.environ.get("PING_TARGETS", "Box=192.168.1.254").split(","):
    if "=" in _pair:
        _k, _v = _pair.split("=", 1)
        PING[_k.strip()] = _v.strip()
PORT = int(os.environ.get("DASHBOARD_PORT", "8080"))
AGENT_TIMEOUT = int(os.environ.get("AGENT_TIMEOUT", "300"))  # defaut si l'agent n'envoie pas max_age

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE           # certificat Proxmox auto-signe
lock = threading.Lock()
cache = {"t": 0, "data": None}
agents = {}


def pve(path):
    req = Request(PVE + "/api2/json" + path, headers={"Authorization": "PVEAPIToken=" + TOKEN})
    with urlopen(req, timeout=5, context=CTX) as r:
        return json.load(r)["data"]


def ping(ip):
    try:
        return subprocess.call(["ping", "-c", "1", "-W", "1", ip], timeout=3,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    except (OSError, subprocess.TimeoutExpired):
        return False   # ping absent (apt install iputils-ping) ou hote muet


def collect():
    out = {"time": time.strftime("%H:%M:%S"), "host": None, "guests": [], "ping": [], "agents": [], "error": None}
    try:
        s = pve("/nodes/%s/status" % NODE)
        out["host"] = {
            "cpu": round(s["cpu"] * 100),
            "ram": round(s["memory"]["used"] * 100 / s["memory"]["total"]),
            "ram_txt": "%.1f / %.1f Go" % (s["memory"]["used"] / 2**30, s["memory"]["total"] / 2**30),
            "disk": round(s["rootfs"]["used"] * 100 / s["rootfs"]["total"]),
            "uptime": int(s["uptime"] // 3600),
        }
        for kind in ("qemu", "lxc"):
            for g in pve("/nodes/%s/%s" % (NODE, kind)):
                out["guests"].append({"id": g["vmid"], "name": g.get("name", "?"), "type": kind,
                                      "up": g["status"] == "running", "ram": round(g.get("mem", 0) / 2**20)})
        out["guests"].sort(key=lambda g: g["id"])
    except Exception as e:
        out["error"] = "Proxmox injoignable: %s" % e
    for name, ip in PING.items():
        out["ping"].append({"name": name, "up": ping(ip)})
    now = time.time()
    for name, a in sorted(agents.items()):
        age = int(now - a["t"])
        state = "silent" if age > a.get("max_age", AGENT_TIMEOUT) else a["status"]
        out["agents"].append({"name": name, "state": state, "task": a["task"], "age": age})
    return out


def status():
    with lock:
        if time.time() - cache["t"] > 5:
            cache["data"] = collect()
            cache["t"] = time.time()
        return cache["data"]


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        b = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == "/api/status":
            self._send(200, json.dumps(status()), "application/json")
        elif self.path == "/":
            self._send(200, PAGE, "text/html")
        else:
            self._send(404, "not found", "text/plain")

    def do_POST(self):
        # Les agents IA envoient: {"name":"agent1","status":"ok|error|busy","task":"...","max_age":300}
        # max_age (optionnel) : secondes sans nouvelles avant de passer en "silent".
        if self.path != "/api/heartbeat":
            return self._send(404, "not found", "text/plain")
        try:
            n = min(int(self.headers.get("Content-Length", 0)), 2048)
            d = json.loads(self.rfile.read(n))
            entry = {"t": time.time(), "status": str(d.get("status", "ok"))[:10],
                     "task": str(d.get("task", ""))[:80]}
            if "max_age" in d:
                entry["max_age"] = max(60, min(int(d["max_age"]), 30 * 86400))
            agents[str(d["name"])[:40]] = entry
            self._send(200, "ok", "text/plain")
        except Exception:
            self._send(400, "bad request", "text/plain")

    def log_message(self, *a):
        pass


PAGE = """<!DOCTYPE html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Homelab</title><style>
body{margin:0;padding:8px;background:#0e1116;color:#e6edf3;font-family:sans-serif;font-size:16px}
h2{margin:10px 4px 6px;font-size:14px;color:#8b949e;text-transform:uppercase}
.row{display:flex;flex-wrap:wrap}
.card{background:#161b22;border-radius:8px;padding:10px;margin:4px;min-width:130px;flex:1}
.big{font-size:26px;font-weight:bold}
.bar{height:6px;background:#30363d;border-radius:3px;margin-top:6px}
.bar div{height:6px;border-radius:3px}
.ok{background:#2ea043}.warn{background:#d29922}.bad{background:#f85149}.off{background:#6e7681}
.dot{display:inline-block;width:10px;height:10px;border-radius:5px;margin-right:6px}
.small{font-size:12px;color:#8b949e}
#err{background:#f85149;padding:6px;border-radius:6px;margin:4px;display:none}
</style></head><body>
<div id="err"></div><div id="host" class="row"></div>
<h2>Machines</h2><div id="guests" class="row"></div>
<h2>Reseau</h2><div id="ping" class="row"></div>
<h2>Agents IA</h2><div id="agents" class="row"></div>
<div class="small" id="time" style="margin:8px 4px"></div>
<script>
function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!==undefined)e.textContent=x;return e;}
function lvl(p){return p>=90?"bad":(p>=75?"warn":"ok");}
function meter(title,val,txt){var c=el("div","card");c.appendChild(el("div","small",title));
 c.appendChild(el("div","big",txt));var b=el("div","bar"),i=el("div",lvl(val));i.style.width=val+"%";
 b.appendChild(i);c.appendChild(b);return c;}
function item(name,cls,sub){var c=el("div","card");c.appendChild(el("span","dot "+cls));
 c.appendChild(el("b",null,name));if(sub)c.appendChild(el("div","small",sub));return c;}
function fill(id,nodes){var p=document.getElementById(id);p.innerHTML="";
 if(!nodes.length){p.appendChild(el("div","small","Rien a afficher"));}
 for(var i=0;i<nodes.length;i++)p.appendChild(nodes[i]);}
function render(d){
 var e=document.getElementById("err");e.style.display=d.error?"block":"none";e.textContent=d.error||"";
 var h=d.host,n=[];
 if(h){n=[meter("CPU",h.cpu,h.cpu+"%"),meter("RAM",h.ram,h.ram_txt),meter("Disque",h.disk,h.disk+"%"),
  (function(){var c=el("div","card");c.appendChild(el("div","small","Uptime"));c.appendChild(el("div","big",h.uptime+" h"));return c;})()];}
 fill("host",n);
 n=[];for(var i=0;i<d.guests.length;i++){var g=d.guests[i];
  n.push(item(g.name,g.up?"ok":"bad",(g.type=="lxc"?"LXC ":"VM ")+g.id+(g.up?" - "+g.ram+" Mo":" - arrete")));}
 fill("guests",n);
 n=[];for(i=0;i<d.ping.length;i++)n.push(item(d.ping[i].name,d.ping[i].up?"ok":"bad",d.ping[i].up?"en ligne":"hors ligne"));
 fill("ping",n);
 n=[];for(i=0;i<d.agents.length;i++){var a=d.agents[i];
  var cls=a.state=="ok"||a.state=="busy"?"ok":(a.state=="silent"?"warn":"bad");
  n.push(item(a.name,cls,a.state+" - il y a "+Math.round(a.age/60)+" min"+(a.task?" - "+a.task:"")));}
 fill("agents",n);
 document.getElementById("time").textContent="Mis a jour "+d.time;}
function load(){var x=new XMLHttpRequest();x.open("GET","/api/status?"+Date.now());
 x.onload=function(){try{render(JSON.parse(x.responseText));}catch(e){}};
 x.onerror=function(){var e=document.getElementById("err");e.style.display="block";e.textContent="Connexion perdue";};
 x.send();}
load();setInterval(load,5000);
</script></body></html>"""

if __name__ == "__main__":
    if not TOKEN:
        print("PVE_TOKEN absent : les donnees Proxmox ne s'afficheront pas.")
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
