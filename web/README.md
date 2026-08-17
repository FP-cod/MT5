# Web dashboard léger pour supervision

Ce dossier contient une interface web minimale (FastAPI + Jinja2) pour :

- Démarrer / arrêter le bot (via PID file)
- Télécharger les trades simulés (trades_simulated.csv)
- Visualiser les métriques du dernier backtest

Installation minimale :

pip install fastapi uvicorn jinja2 pandas

Lancement :

cd web
uvicorn app:app --host 0.0.0.0 --port 8080 --workers 1

Sécurité : ne pas exposer le port sans authentification/accès restreint.
