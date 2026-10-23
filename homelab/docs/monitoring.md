# Monitoring

## Objectif

Un écran permanent (tablette Klipad, Chrome 59) affichant :

- l'état de l'hôte Proxmox (CPU, RAM, disque, uptime) ;
- l'état de chaque conteneur ;
- la disponibilité des équipements réseau (ping) ;
- l'état des agents IA (dont l'agent de veille cyber) ;
- plus tard, une caméra (flux MJPEG ou snapshots).

## Solution retenue : tableau de bord maison

Un seul script Python sans dépendance ([`services/dashboard`](../services/dashboard)) dans le LXC 104 :

- sert une page HTML/JS écrite pour les vieux navigateurs (XMLHttpRequest, pas de framework) ;
- interroge l'API Proxmox avec un jeton **PVEAuditor** ;
- reçoit les signes de vie des agents sur `POST /api/heartbeat` ;
- consomme quelques dizaines de Mo de RAM.

## Pistes écartées

| Solution            | Résultat sur la tablette                                     |
|---------------------|--------------------------------------------------------------|
| Homepage            | Trop lourd (Next.js) pour Chrome 59 et pour 2 Go de RAM       |
| ProxMenux Monitor   | Reste sur « Loading… Connecting to ProxMenux Monitor »        |
| Glances (paquet apt)| Plante au démarrage du serveur web                            |
| Fully Kiosk 1.61.4  | « Erreur d'analyse » à l'installation (trop récent)           |
| VM sur la tablette  | Impossible / inutile sur Android 5.1.1                        |

Si un navigateur kiosque est nécessaire un jour : essayer Fully Kiosk **1.48.2**
(signalée comme fonctionnant sur Android 5.1, non vérifié) ou Webview Kiosk (F-Droid, Android 5.0+).

## Caméra (à faire)

Chrome 59 ne lit pas le RTSP. Il faut un flux **MJPEG** ou des **snapshots JPEG** rafraîchis,
affichés dans une balise `<img>`. La conversion RTSP → MJPEG (go2rtc) est trop lourde pour
l'hôte tant qu'il a 2 Go de RAM : préférer une caméra qui sort déjà du MJPEG.
Le flux caméra ne doit jamais être exposé sur Internet.
