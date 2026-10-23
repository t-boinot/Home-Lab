# Tailscale — subnet router (LXC 102)

Donne accès au réseau `192.168.1.0/24` depuis n'importe où, sans ouvrir de port sur la box.

## Installation

1. LXC Debian, 256 Mo de RAM, passerelle **192.168.1.254**.
2. Sur l'hôte, ajouter [`proxmox/lxc/102-tailscale.conf.snippet`](../../proxmox/lxc/102-tailscale.conf.snippet) à `/etc/pve/lxc/102.conf`, puis démarrer le conteneur.
3. Dans le conteneur :

```bash
apt update && apt install -y curl
curl -fsSL https://tailscale.com/install.sh | sh
echo 'net.ipv4.ip_forward = 1' > /etc/sysctl.d/99-tailscale.conf
sysctl -p /etc/sysctl.d/99-tailscale.conf
tailscale up --advertise-routes=192.168.1.0/24
```

4. Console d'administration Tailscale → Machines → le conteneur :
   - **Edit route settings** → approuver `192.168.1.0/24` ;
   - **Disable key expiry** pour ce serveur.

## Clients

- Windows / macOS : installer Tailscale, se connecter au même compte (routes acceptées par défaut).
- Linux : `sudo tailscale up --accept-routes`.

## Durcissement

- Double authentification sur le compte utilisé pour Tailscale.
- ACL : limiter les appareils autorisés à joindre le sous-réseau.
- Supprimer les appareils perdus ou inutilisés.

## Vérification

```bash
tailscale status
tailscale ip -4
```
