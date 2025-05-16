#!/bin/bash

echo "=== [*] Lancement de OWASP Dependency-Check avec Docker ==="

# Variables du projet
PROJECT_NAME="SecureBDDApp"
REPORT_DIR="./securityReports"
SOURCE_DIR="./backend/app"

# Chargement des variables d'environnement
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Vérification que la clé API NVD est définie
if [ -z "$NVD_API_KEY" ]; then
    echo "[-] Erreur : NVD_API_KEY n'est pas définie. Veuillez la configurer dans le fichier .env."
    exit 1
fi

# Exécution de OWASP Dependency-Check avec Docker
docker run --rm \
    --platform linux/amd64 \
    --volume "$(pwd)/${SOURCE_DIR}:/src" \
    --volume "$(pwd)/${REPORT_DIR}:/report" \
    owasp/dependency-check \
    --project "${PROJECT_NAME}" \
    --scan /src \
    --format "HTML" \
    --out /report \
    --nvdApiKey "$NVD_API_KEY"

# Vérification du succès du scan
if [ $? -eq 0 ]; then
    echo "[✓] Rapport HTML généré dans ${REPORT_DIR}"
else
    echo "[-] Erreur lors du scan OWASP Dependency-Check"
    exit 1
fi
