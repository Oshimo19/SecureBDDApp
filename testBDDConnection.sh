#!/bin/bash

# Chargement les variables environnement
set -a
source .env
set +a

# Nom du conteneur a adapter
CONTAINER_NAME=$POSTGRES_CONTAINER_NAME

# Verifier si conteneur existe
docker inspect "$CONTAINER_NAME" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "[-] Erreur : BDD indisponible - Lancer 'docker compose up -d pgsdb'"
    exit 1
fi

# Verifier etat de sante de la BDD
STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME")
if [ "$STATUS" != "healthy" ]; then
    echo "[-] Erreur : BDD pas prete (Etat : $STATUS)"
    exit 2
fi

# Test connexion de la BDD
docker exec -i "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT current_database();" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "[+] Connexion BDD OK"
else
    echo "[-] Erreur : Connexion BDD invalide"
    exit 3
fi
