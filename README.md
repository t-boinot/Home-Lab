# Homelab pve-01

Homelab personnel hébergé sur un **HP ProLiant MicroServer Gen8** sous **Proxmox VE 9.2**.
Il réunit un gestionnaire de mots de passe, un accès distant sécurisé, un écran de monitoring
sur une ancienne tablette et un agent n8n de veille cybersécurité.

## Infrastructure

| Conteneur | Rôle | État |
|-----------|------|------|
| LXC 101 · docker | n8n et l'agent de veille cyber | en service, n8n à installer |
| LXC 102 · tailscale | VPN, subnet router `192.168.1.0/24` | en service |
| LXC 103 · vaultwarden | Gestionnaire de mots de passe | en service |
| LXC 104 · dashboard | Tableau de bord pour la tablette | à créer |

- **Réseau** : hôte en `192.168.1.18`, passerelle `192.168.1.254`
- **Accès distant** : uniquement par Tailscale, aucun port ouvert sur la box
- **Matériel** : 2 Go de RAM aujourd'hui, passage prévu à 16 Go (2 × HP 669324-B21, DDR3 UDIMM ECC)

## Agent de veille cyber

Un workflow n8n se déclenche le lundi et le jeudi à 10 h. Il lit quatre flux RSS
(The Hacker News, BleepingComputer, ZATAZ et un quatrième), filtre les articles,
fait rédiger un post par **Gemini**, génère une image puis publie le tout sur **Discord**.
Les articles publiés sont mémorisés pour ne jamais être postés deux fois.

## Monitoring

Une tablette Klipad (Android 5.1.1, Chrome 59) sert d'écran permanent. Les tableaux de bord
existants (Homepage, ProxMenux Monitor, Glances) ne s'y affichent pas : un tableau de bord
maison en Python, sans dépendance, montre l'état de l'hôte, des conteneurs, du réseau et des agents IA.

## Sécurité

- Aucun service exposé directement sur Internet
- Un conteneur par service, jeton Proxmox en lecture seule pour le monitoring
- Double authentification sur Proxmox, Vaultwarden et Tailscale
- Aucun secret dans ce dépôt : clés et webhooks restent dans des fichiers `.env` ignorés par Git

## Prochaines étapes

- [ ] Passer à 16 Go de RAM
- [ ] Installer n8n et importer le workflow de veille
- [ ] Déployer le tableau de bord sur la tablette
- [ ] Mettre en place les sauvegardes (vzdump + copie hors site)
- [ ] Monter le NAS (ZFS + Samba)
