# Configuration des conteneurs

Pour garder une trace de la configuration réelle, copie ici les fichiers de l'hôte
**après avoir relu qu'ils ne contiennent aucun secret** :

```bash
# sur pve-01
for id in 101 102 103 104; do
  [ -f /etc/pve/lxc/$id.conf ] && cp /etc/pve/lxc/$id.conf ./$id.conf
done
```

Ces fichiers contiennent les adresses IP, la RAM, les points de montage et les options
(nesting, keyctl), mais pas de mots de passe.
