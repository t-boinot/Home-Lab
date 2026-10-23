# Workflows exportés

Place ici `veille-cyber.json`, **après** nettoyage :

```bash
python3 scripts/sanitize-n8n-workflow.py ~/Téléchargements/export.json agents/veille-cyber/workflows/veille-cyber.json
```

Ne jamais committer un export brut : il peut contenir l'URL du webhook Discord ou la clé Gemini.
