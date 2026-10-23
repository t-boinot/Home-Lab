# Journal

Problèmes rencontrés et décisions prises, du plus ancien au plus récent.

## 2026-10 — Choix de l'architecture

- Proxmox VE sur le MicroServer Gen8, services en conteneurs LXC plutôt qu'en VM (RAM limitée).
- NAS prévu : ZFS géré par Proxmox + Samba dans un LXC, plutôt qu'une VM TrueNAS
  (passthrough du contrôleur délicat sur le Gen8, RAM insuffisante).

## 2026-10 — Pas d'accès Internet sur l'hôte

- Symptôme : `Destination Host Unreachable` vers 8.8.8.8, échec de résolution DNS.
- Cause : passerelle `192.168.1.1` au lieu de `192.168.1.254`.
- Résolu : voir [reseau.md](reseau.md).

## 2026-10 — Seulement 2 Go de RAM

- ProxMenux affichait 2 Go : c'est la RAM physique (une barrette, slot 2 vide), pas un réglage Proxmox.
- Décision : achat de 2 × 8 Go UDIMM ECC (HP 669324-B21). Refusées : Timetec non-ECC, Lenovo 49Y1397 (RDIMM).

## 2026-10 — Écran de monitoring sur la tablette

- Klipad Smart i745 retenue (Android 5.1.1) plutôt que Galaxy Tab 4 (Android 4.4).
- ProxMenux Monitor : OK sur PC, bloqué sur « Loading… » sur la tablette → Chrome 59 trop ancien.
- Glances via apt : `RuntimeError: Directory '.../static/public' does not exist` → paquet incomplet.
- Glances 3.4.0.5 en venv : démarre, puis désinstallé.
- Fully Kiosk 1.61.4 : « erreur d'analyse » → trop récent pour Android 5.1.1.
- Décision : tableau de bord maison compatible Chrome 59 (`services/dashboard`).

## 2026-10 — Accès distant

- Étudiés : Tailscale, WireGuard auto-hébergé, Cloudflare Tunnel, reverse proxy exposé, tunnel SSH.
- Décision : Tailscale en subnet router (LXC 102). Aucun port ouvert.

## 2026-10 — Agent de veille cyber

- Workflow n8n : 4 flux RSS → filtrage → rédaction par Gemini → image → publication Discord.
- Décision : n8n hébergé dans le LXC 101 (docker). Voir [agents/veille-cyber](../agents/veille-cyber/README.md).

## 2026-10-23 — Création de ce dépôt
