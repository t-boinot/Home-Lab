#!/usr/bin/env bash
# Exporte tous les workflows n8n (conteneur Docker "n8n", LXC 101), les nettoie
# de leurs secrets et les range dans agents/<nom>/workflows/ ou exports/.
# Usage : scripts/export-n8n-workflows.sh   (depuis la racine du depot, dans le LXC 101)
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

docker exec n8n sh -c 'rm -rf /tmp/wf && mkdir -p /tmp/wf && n8n export:workflow --all --separate --output=/tmp/wf'
docker cp n8n:/tmp/wf/. "$TMP/"
docker exec n8n rm -rf /tmp/wf

mkdir -p "$REPO/exports"
for f in "$TMP"/*.json; do
  name="$(python3 -c 'import json,re,sys; n=json.load(open(sys.argv[1])).get("name","workflow"); print(re.sub(r"[^a-z0-9]+","-",n.lower()).strip("-") or "workflow")' "$f")"
  case "$name" in
    *veille*) dest="$REPO/agents/veille-cyber/workflows/veille-cyber.json" ;;
    *)        dest="$REPO/exports/$name.json" ;;
  esac
  python3 "$REPO/scripts/sanitize-n8n-workflow.py" "$f" "$dest"
  echo "-> ${dest#$REPO/}"
done

echo "Termine. Verifie avec : git -C \"$REPO\" diff --stat"
