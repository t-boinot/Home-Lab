# n8n (LXC 101)

## Prérequis

- LXC 101 avec **Nesting** et **keyctl** activés, Docker installé.
- RAM : n8n demande 300 à 500 Mo. Donner au moins **1 Go** au LXC 101, idéalement 2 Go après le passage à 16 Go.

## Installation

```bash
mkdir -p /opt/n8n && cd /opt/n8n
# copier docker-compose.yml et .env.example depuis ce dépôt
cp .env.example .env
sed -i "s/^N8N_ENCRYPTION_KEY=.*/N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)/" .env
nano .env            # renseigner l'IP du LXC
docker compose up -d
docker compose logs -f
```

Ouvre `http://IP_DU_LXC_101:5678`, crée le compte propriétaire, puis importe le workflow
de veille : menu **Workflows → Import from file** → `agents/veille-cyber/workflows/veille-cyber.json`.

Recrée ensuite les credentials (clé Gemini, webhook Discord) : ils ne sont jamais dans le dépôt.

## Mise à jour

```bash
cd /opt/n8n
/opt/homelab/scripts/export-n8n-workflows.sh   # sauvegarde avant
docker compose pull && docker compose up -d
docker image prune -f
```

## Sauvegarde

- Workflows : `scripts/export-n8n-workflows.sh` (exporte et nettoie les secrets, prêts à committer).
- Données complètes : le volume `n8n_data` est inclus dans la sauvegarde vzdump du LXC 101.
- `N8N_ENCRYPTION_KEY` : à garder dans Vaultwarden.
