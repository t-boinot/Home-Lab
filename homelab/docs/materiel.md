# Matériel

## Serveur : HP ProLiant MicroServer Gen8

| Élément      | Détail                                                        |
|--------------|---------------------------------------------------------------|
| Hôte         | `pve-01`, Proxmox VE 9.2.21                                    |
| CPU          | 2 cœurs (Celeron/Pentium d'origine — à confirmer)             |
| RAM actuelle | **2 Go** DDR3 ECC (1 barrette, slot `PROC 1 DIMM 1`), slot 2 vide |
| Swap         | 4 Go                                                          |
| Réseau       | 2 × 1 GbE (`nic0` utilisé, `nic1` sans câble) + iLO4           |
| Baies        | 4 × 3,5" (non hot-swap), contrôleur B120i à laisser en AHCI   |

Relevé du 2026-10 (`dmidecode -t memory`) :

```
Error Correction Type: Single-bit ECC
Size: 2 GB            Locator: PROC  1 DIMM  1   Type: DDR3  Speed: 1600 MT/s
Size: No Module Installed   Locator: PROC  1 DIMM  2
```

Au repos, l'hôte utilise environ 56 % de ses 2 Go : c'est la contrainte principale du homelab.

## Mise à niveau RAM (prioritaire)

Objectif : **16 Go = 2 × 8 Go**, en remplaçant la barrette de 2 Go.

**Référence retenue : HP 669324-B21** (pièce 684035-001)
— 8 Go, 2Rx8, PC3-12800E (DDR3-1600), **UDIMM unbuffered ECC**, CL11.

Équivalents acceptables :

- HP 647909-B21 — 8 Go UDIMM ECC mais en 1333 MHz (PC3L-10600E), un peu plus lente
- Kingston KVR16E11/8, Crucial CT102472BD160B — à revérifier sur la fiche avant achat

Règles d'achat :

| ✅ Requis                          | ❌ Refusé                                   |
|-----------------------------------|---------------------------------------------|
| UDIMM / unbuffered                | RDIMM, REG, registered (ex. Lenovo 49Y1397) |
| ECC                               | Non-ECC (ex. Timetec PC3-12800 Non-ECC)     |
| DDR3 / DDR3L, PC3-12800E          | DDR4, SO-DIMM                               |
| 2Rx8 de préférence                | 2Rx4 (presque toujours de la RDIMM)         |

Après installation :

```bash
free -h
dmidecode -t memory | grep -E "Size|Speed"
```

Puis quelques passes de **MemTest86**, surtout pour des barrettes d'occasion.

Option budget : une seule 8 Go dans le slot libre → 10 Go, puis remplacement de la 2 Go plus tard.

## Écran de monitoring : tablette Klipad Smart i745

| Élément    | Détail                               |
|------------|--------------------------------------|
| Android    | 5.1.1                                |
| Navigateur | Chrome 59 (2017), pas de mise à jour |
| Usage      | Affiche le tableau de bord (LXC 104) |

Ce qui ne fonctionne pas sur cette tablette (voir [journal.md](journal.md)) :
ProxMenux Monitor (bloqué sur « Loading… »), Fully Kiosk Browser v1.61.4 (« erreur d'analyse »).

Réglages retenus : adresse du tableau de bord en page d'accueil, option développeur
**Rester allumé**, luminosité basse, branchée en permanence (surveiller un éventuel
gonflement de la batterie).

Tablette écartée : Samsung Galaxy Tab 4 7.0 (SM-T230), bloquée sur Android 4.4.
