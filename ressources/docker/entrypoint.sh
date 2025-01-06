#!/bin/bash

# Fonction pour nettoyer à la fin du script
cleanup() {
    echo "Arrêt de Docker Compose..."
    exit 0
}

# Capturer les signaux SIGINT (Ctrl+C) et SIGTERM pour nettoyer proprement
trap cleanup SIGINT SIGTERM

# Début des tests
bats /app/tests/cabine.bats

# Lancer la commande qui garde le conteneur actif
tail -f /dev/null &
TAIL_PID=$!

# Attendre indéfiniment en arrière-plan
wait $TAIL_PID
