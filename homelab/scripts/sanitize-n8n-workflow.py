#!/usr/bin/env python3
"""Nettoie un export de workflow n8n avant de le committer.

- masque les webhooks Discord, les cles Google/Gemini, les jetons Bearer et les mots de passe ;
- retire les references aux credentials (id), les donnees epinglees et la memoire du workflow ;
- retire l'identifiant d'instance n8n.

Usage : sanitize-n8n-workflow.py ENTREE.json [SORTIE.json]
Code de sortie 0 si OK. Affiche le nombre d'elements masques.
"""
import json
import re
import sys

PATTERNS = [
    (re.compile(r"https://(?:ptb\.|canary\.)?discord(?:app)?\.com/api/webhooks/[\w/-]+"), "https://discord.com/api/webhooks/REDACTED"),
    (re.compile(r"AIza[0-9A-Za-z_-]{30,}"), "REDACTED_GOOGLE_API_KEY"),
    (re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{16,}"), "Bearer REDACTED"),
    (re.compile(r"(?i)([?&](?:key|api_key|apikey|token|access_token)=)[^&\s\"']+"), r"\1REDACTED"),
    (re.compile(r"PVEAPIToken=[^\s\"']+"), "PVEAPIToken=REDACTED"),
]
SENSITIVE_KEYS = re.compile(r"(?i)^(password|passwd|secret|api[_-]?key|token|access[_-]?token|authorization|x-goog-api-key)$")
DROP_TOP_LEVEL = ("pinData", "staticData")

count = 0


def scrub_str(s):
    global count
    for rx, repl in PATTERNS:
        s, n = rx.subn(repl, s)
        count += n
    return s


def scrub(obj, key=None):
    global count
    if isinstance(obj, dict):
        # en-tetes HTTP n8n : [{"name": "x-goog-api-key", "value": "..."}]
        if isinstance(obj.get("name"), str) and SENSITIVE_KEYS.match(obj["name"]) and isinstance(obj.get("value"), str) \
                and obj["value"] and not obj["value"].startswith("={{"):
            obj = dict(obj, value="REDACTED")
            count += 1
        out = {}
        for k, v in obj.items():
            if k == "credentials" and isinstance(v, dict):
                out[k] = {t: {"name": (c or {}).get("name", "")} if isinstance(c, dict) else c for t, c in v.items()}
            elif SENSITIVE_KEYS.match(k) and isinstance(v, str) and v and not v.startswith("={{"):
                out[k] = "REDACTED"
                count += 1
            else:
                out[k] = scrub(v, k)
        return out
    if isinstance(obj, list):
        return [scrub(v, key) for v in obj]
    if isinstance(obj, str):
        return scrub_str(obj)
    return obj


def clean_workflow(wf):
    for k in DROP_TOP_LEVEL:
        wf.pop(k, None)
    if isinstance(wf.get("meta"), dict):
        wf["meta"].pop("instanceId", None)
    return scrub(wf)


def main():
    if len(sys.argv) not in (2, 3):
        print(__doc__)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)
    data = [clean_workflow(w) for w in data] if isinstance(data, list) else clean_workflow(data)
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if len(sys.argv) == 3:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    print("%d element(s) masque(s)." % count, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
