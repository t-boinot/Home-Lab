# Vaultwarden (LXC 103)

Gestionnaire de mots de passe compatible avec les applications Bitwarden.

## À documenter

- [ ] Méthode d'installation (script communautaire, binaire, Docker ?)
- [ ] Emplacement des données (souvent `/opt/vaultwarden/data` ou `/var/lib/vaultwarden`)
- [ ] Adresse IP et port
- [ ] HTTPS : les clients Bitwarden exigent HTTPS (certificat local ou via Tailscale)

## Règles

- Accessible uniquement sur le LAN et via Tailscale.
- Inscriptions désactivées après création des comptes (`SIGNUPS_ALLOWED=false`).
- Jeton d'administration (`ADMIN_TOKEN`) en hash Argon2, jamais en clair, jamais dans Git.
- Double authentification sur chaque compte.

## Sauvegarde (critique)

À compléter avec le bon chemin de données :

```bash
# exemple : copie cohérente de la base SQLite + pièces jointes
DATA=/var/lib/vaultwarden
DEST=/root/backup-vaultwarden-$(date +%F)
mkdir -p "$DEST"
sqlite3 "$DATA/db.sqlite3" ".backup '$DEST/db.sqlite3'"
cp -a "$DATA/attachments" "$DATA/rsa_key"* "$DEST/" 2>/dev/null
tar czf "$DEST.tar.gz" -C "$(dirname "$DEST")" "$(basename "$DEST")" && rm -rf "$DEST"
```

Copier ensuite l'archive **hors site** (disque externe, autre machine). Tester une restauration.
