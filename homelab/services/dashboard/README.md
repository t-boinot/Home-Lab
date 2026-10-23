# Tableau de bord (LXC 104)

Page web légère pour la tablette Klipad (Chrome 59) : état de l'hôte, des conteneurs,
des équipements réseau et des agents IA. Python 3 sans aucune dépendance.

## Installation

1. Créer le jeton Proxmox en lecture seule (voir [docs/proxmox.md](../../docs/proxmox.md#jetons-api)).
2. Créer le LXC 104 : Debian, 1 vCPU, 192 Mo de RAM, 2 Go de disque, IP fixe, passerelle **192.168.1.254**.
3. Dans le conteneur :

```bash
apt update && apt install -y python3 iputils-ping
mkdir -p /opt/dashboard
# copier dashboard.py dans /opt/dashboard/
cp dashboard.env.example /etc/dashboard.env && chmod 600 /etc/dashboard.env
nano /etc/dashboard.env          # coller le secret du jeton, ajouter les appareils
cp dashboard.service /etc/systemd/system/
systemctl daemon-reload && systemctl enable --now dashboard
systemctl status dashboard
```

4. Ouvrir `http://IP_DU_LXC_104:8080` sur le PC, puis sur la tablette (page d'accueil du navigateur).

## Signes de vie des agents

```bash
curl -X POST http://IP_DU_LXC_104:8080/api/heartbeat \
  -d '{"name":"veille-cyber","status":"ok","task":"post publié","max_age":360000}'
```

| Champ     | Valeurs                          | Rôle                                      |
|-----------|----------------------------------|-------------------------------------------|
| `name`    | texte (40 car. max)              | Nom affiché                               |
| `status`  | `ok`, `busy`, `error`            | Vert, vert, rouge                          |
| `task`    | texte (80 car. max)              | Dernière action                            |
| `max_age` | secondes (optionnel)             | Délai avant passage en orange (« silent ») |

Les agents sont gardés en mémoire : après un redémarrage du service, ils réapparaissent à leur prochain signe de vie.

## Sécurité

- Jeton PVEAuditor (lecture seule), stocké dans `/etc/dashboard.env` en `chmod 600`, jamais dans Git.
- L'endpoint `/api/heartbeat` n'a pas d'authentification : réseau local et Tailscale uniquement.
- Le service tourne avec un utilisateur dynamique non privilégié (`DynamicUser=yes`).
