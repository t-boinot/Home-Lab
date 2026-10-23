# Sécurité

## Principes

1. **Rien d'exposé sur Internet** : accès distant uniquement par Tailscale.
2. **Moindre privilège** : jeton Proxmox PVEAuditor pour le tableau de bord, un conteneur par service.
3. **Double authentification** sur Proxmox, Vaultwarden, le compte Tailscale et le compte Discord.
4. **Mises à jour régulières** : hôte, conteneurs, images Docker (n8n), Tailscale.
5. **Secrets hors du dépôt** : fichiers `.env` ignorés par Git, script de nettoyage pour les exports n8n.

## Secrets et où ils vivent

| Secret                       | Emplacement                         | Dans Git ? |
|------------------------------|-------------------------------------|------------|
| Jeton API Proxmox (dashboard)| `/etc/dashboard.env` (LXC 104)       | Non        |
| Clé de chiffrement n8n       | `services/n8n/.env` (LXC 101)        | Non — à sauvegarder à part |
| Clé API Gemini               | Credential n8n                      | Non        |
| Webhook(s) Discord           | Credential ou variable n8n          | Non        |
| Comptes Vaultwarden          | Base Vaultwarden (LXC 103)          | Non        |
| Clé d'authentification Tailscale | Interactif, non stockée         | Non        |

Un webhook Discord permet à n'importe qui de publier dans ton salon : s'il fuit, régénère-le.

## Avant chaque commit

```bash
git diff --cached | grep -nE "discord(app)?\.com/api/webhooks/[0-9]|AIza[0-9A-Za-z_-]{20,}|![A-Za-z0-9_-]+=[0-9a-f]{8}-[0-9a-f]{4}-" && echo "SECRET A RETIRER" || echo "OK"
```

Les workflows n8n exportés passent par [`scripts/sanitize-n8n-workflow.py`](../scripts/sanitize-n8n-workflow.py).

## Points de vigilance

- **iLO4** : mot de passe par défaut changé, réseau local uniquement.
- **ProxMenux** : script tiers exécuté en root sur l'hôte — relire ses mises à jour.
- **Endpoint heartbeat** du tableau de bord : sans authentification, donc réseau local uniquement.
- **CPU à 100 % sans raison** : vérifier `top` (un mineur installé sur une machine compromise est un classique).
- **Tablette** : Android 5.1.1 n'a plus de mises à jour de sécurité ; elle ne sert qu'à afficher une page locale.
