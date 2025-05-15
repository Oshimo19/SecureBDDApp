#!/bin/bash

# Verifie que Django arrive a acceder a PostgreSQL
docker compose run --rm django python manage.py check > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "[+] Communication Django <-> PostgreSQL : OK"
else
    echo "[-] Erreur : Django n arrive pas a joindre PostgreSQL"
    exit 1
fi

# Verifie que PostgreSQL n est pas expose sur Internet (5432 ferme en dehors du reseau Docker)
POSTGRES_PORT=$(grep POSTGRES_PORT .env | cut -d '=' -f2)
EXTERNAL_OPEN=$(ss -tuln | grep ":$POSTGRES_PORT " | grep -v 127.0.0.1)

if [ -z "$EXTERNAL_OPEN" ]; then
    echo "[+] PostgreSQL n est pas expose sur Internet"
else
    echo "[-] Alerte : Le port $POSTGRES_PORT de PostgreSQL semble expose !"
    exit 2
fi
