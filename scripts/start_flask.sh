#!/bin/bash

# Se déplacer dans le répertoire racine du projet
cd $(dirname "$0")/..

# Activer l'environnement virtuel
source venv/bin/activate

# Définir l'application Flask (app.py dans le dossier app)
export FLASK_APP=app/app.py

# Vérifier les paramètres d'entrée pour sélectionner le mode
if [ "$1" == "development" ]; then
    echo "Lancement en mode développement..."
    export FLASK_ENV=development
    CMD="flask run --host=127.0.0.1 --port=5000"

elif [ "$1" == "test" ]; then
    echo "Lancement en mode test..."
    export FLASK_ENV=testing
    CMD="flask run --host=127.0.0.1 --port=5000"

elif [ "$1" == "production" ]; then
    echo "Lancement en mode production..."
    CMD="gunicorn -w 3 -b 127.0.0.1:5000 app:app"

else
    echo "Usage: $0 {development|test|production}"
    exit 1
fi

# Exécuter la commande avec nohup
nohup $CMD > flask.log 2>&1 &

# Afficher un message de confirmation
echo "Serveur Flask lancé."
echo "Vous pouvez consulter les logs avec la commande : cat flask.log"
