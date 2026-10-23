# Réseau

## Adressage

| Équipement        | Adresse          | Remarque                          |
|-------------------|------------------|-----------------------------------|
| Box FAI (passerelle) | 192.168.1.254 | **Pas** 192.168.1.1               |
| pve-01            | 192.168.1.18/24  | pont `vmbr0` sur `nic0`           |
| iLO4              | _à compléter_    | réseau local uniquement           |
| LXC 101 docker    | _à compléter_    | n8n sur le port 5678              |
| LXC 102 tailscale | _à compléter_    | subnet router                     |
| LXC 103 vaultwarden | _à compléter_  |                                   |
| LXC 104 dashboard | _à compléter_    | port 8080                         |
| Tablette Klipad   | _à compléter_    | réservation DHCP conseillée       |

DNS de l'hôte : `8.8.8.8` (`/etc/resolv.conf`, domaine de recherche `it-connect.local`).

## Ponts Proxmox

| Pont   | Port physique | Usage                                   |
|--------|---------------|-----------------------------------------|
| vmbr0  | nic0          | LAN 192.168.1.0/24, IP de l'hôte        |
| vmbr1  | nic1          | pas de câble branché (NO-CARRIER)       |
| vmbr2  | aucun         | réseau interne isolé                    |

Fichier de référence : [`proxmox/network/interfaces`](../proxmox/network/interfaces).

## Incident : pas d'accès Internet (passerelle fausse)

Symptôme : `ping 8.8.8.8` → `Destination Host Unreachable`, `github.com` non résolu.
Cause : `gateway 192.168.1.1` dans `/etc/network/interfaces`, alors que la box est en `.254`.

Correctif :

```bash
# test temporaire
ip route replace default via 192.168.1.254
ping -c 3 8.8.8.8 && ping -c 3 github.com

# correctif permanent : gateway 192.168.1.254 dans le bloc vmbr0, puis
ifreload -a
ip route   # doit afficher : default via 192.168.1.254 dev vmbr0
```

Tout nouveau conteneur doit lui aussi utiliser **192.168.1.254** comme passerelle.

## Accès distant

Choix : **VPN Tailscale** dans le LXC 102, en *subnet router* qui annonce `192.168.1.0/24`.
Aucun port ouvert sur la box. Procédure : [`services/tailscale/README.md`](../services/tailscale/README.md).

Règles :

- Ne jamais exposer Proxmox (8006), Vaultwarden, le NAS, n8n ou le tableau de bord directement sur Internet.
- Si le réseau distant utilise aussi `192.168.1.0/24`, il y a conflit : passer par l'IP Tailscale `100.x.y.z`.
- Proton VPN est un VPN de confidentialité : il ne donne **pas** accès au réseau local.

Alternative étudiée : WireGuard auto-hébergé (aucun tiers, mais un port UDP ouvert et une IP publique sans CGNAT requise).
