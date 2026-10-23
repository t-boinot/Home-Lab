# Proxmox VE

## Nœud

- Nom : `pve-01` — Proxmox VE **9.2.21**
- Interface : `https://192.168.1.18:8006` (réseau local ou Tailscale uniquement)
- Dépôts : « no-subscription » activé, « enterprise » désactivé (sinon `apt update` échoue en 401)

## Conteneurs

| ID  | Nom         | Rôle                         | RAM conseillée (après passage à 16 Go) |
|-----|-------------|------------------------------|----------------------------------------|
| 101 | docker      | Docker + n8n                 | 1,5 à 2 Go                             |
| 102 | tailscale   | Subnet router                | 256 Mo                                 |
| 103 | vaultwarden | Gestionnaire de mots de passe| 512 Mo                                 |
| 104 | dashboard   | Tableau de bord tablette     | 192 Mo                                 |

Le LXC 101 nécessite les options **Nesting** et **keyctl** (Options → Features) pour Docker.
Le LXC 102 nécessite l'accès à `/dev/net/tun` : voir [`proxmox/lxc/102-tailscale.conf.snippet`](../proxmox/lxc/102-tailscale.conf.snippet).

Tant que l'hôte n'a que 2 Go, ne pas ajouter de VM ni activer ZFS.

## Stockage

| Stockage     | Usage                                        |
|--------------|----------------------------------------------|
| local        | ISO, templates, sauvegardes vzdump           |
| local-lvm    | disques des conteneurs                       |
| vms-storage  | à documenter (nature, disque, usage prévu)   |

Pour le futur NAS : pool ZFS géré par Proxmox + partage Samba dans un LXC, ARC limité :

```bash
echo "options zfs zfs_arc_max=2147483648" > /etc/modprobe.d/zfs.conf   # 2 Go
update-initramfs -u && reboot
```

## Jetons API

Utilisateur dédié en **lecture seule** pour le tableau de bord :

```bash
pveum user add dashboard@pve
pveum acl modify / --users dashboard@pve --roles PVEAuditor
pveum user token add dashboard@pve tablet --privsep 0
```

Le secret ne s'affiche qu'une fois. Il va dans `/etc/dashboard.env` du LXC 104, **jamais** dans ce dépôt.

## Sauvegardes (à mettre en place)

1. Datacenter → Backup → tâche quotidienne `vzdump` des LXC 101 à 104 (mode snapshot, compression zstd, rétention 7 jours).
2. Copie hors site : au minimum la base Vaultwarden et l'export des workflows n8n.
3. Tester une restauration une fois par trimestre.

Rappel 3-2-1 : 3 copies, 2 supports, 1 hors site. Le RAID n'est pas une sauvegarde.

## Outils installés puis retirés

| Outil              | État       | Pourquoi                                                    |
|--------------------|------------|-------------------------------------------------------------|
| ProxMenux Monitor  | installé, port 8008 | Fonctionne sur PC, pas sur la tablette (Chrome 59)  |
| Glances (apt)      | retiré     | Paquet Debian incomplet (`static/public` manquant)          |
| Glances 3.4.0.5 (venv) | retiré | Remplacé par le tableau de bord maison                      |

Pour libérer de la RAM : `systemctl disable --now proxmenux-monitor`.
