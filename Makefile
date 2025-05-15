# Variables globales chargees depuis .env
include .env
HOST_PATH := $(shell pwd)

# Repertoires de travail
APP_DIR=./backend/app
REQUIREMENTS_FILE=${APP_DIR}/requirements.txt

# Check si on est root (UID = 0)
checkRoot:
	@if [ "$$(id -u)" -ne 0 ]; then \
		echo "[-] Erreur : Executer en root"; \
		exit 1; \
	fi

## Supprimer les fichiers temporaires de Django (db.sqlite3)
cleanDjango: checkRoot
	@rm -f ${APP_DIR}/db.sqlite3 2>/dev/null || true

# Initialiser Django + Generer fichier "requirements.txt"
initDjango: checkRoot
	@if [ -f ${APP_DIR}/manage.py ]; then \
		echo "[-] Le projet Django existe déjà dans ${APP_DIR}"; \
		exit 1; \
	fi
	@mkdir -p ${APP_DIR}
	docker run --rm \
		-v ${HOST_PATH}/${APP_DIR}:/app \
		-w /app \
		${PYTHON_IMAGE} \
		bash -c "\
			pip install --upgrade pip --root-user-action ignore && \
			pip install --no-cache-dir django==${DJANGO_VERSION} --root-user-action ignore && \
			django-admin startproject ${DJANGO_PROJECT_NAME} . && \
			pip freeze > /app/requirements.txt"

# Lancer Django en mode debug avec fichier de base (settings2.py)
runDjango:
	docker run --rm \
		-v ${HOST_PATH}/${APP_DIR}:/app \
		-w /app \
		-p ${DJANGO_PORT}:8000 \
		--env-file .env \
		${PYTHON_IMAGE} \
		bash -c "\
			pip install --upgrade pip --root-user-action ignore && \
			pip install -r /app/requirements.txt && \
			python manage.py runserver 0.0.0.0:8000"
		$(MAKE) cleanDjango

# Installer les dependances depuis fichier "requirements.txt"
installDeps: checkRoot
	docker run --rm \
		-v ${HOST_PATH}/${APP_DIR}:/app \
		-w /app \
		${PYTHON_IMAGE} \
		bash -c "\
			pip install --upgrade pip --root-user-action ignore && \
		    pip install -r /app/requirements.txt"

# Lancer Django en mode debug avec notre fichier (settings2.py)
runDjangoBDD:
	docker run --rm \
		-v ${PWD}/${APP_DIR}:/app \
		-w /app \
		--env-file .env \
		--network securebddapp_netSec \
		-p ${DJANGO_PORT}:8000 \
		${PYTHON_IMAGE} \
		bash -c "\
			pip install --upgrade pip --root-user-action ignore && \
			pip install -r /app/requirements.txt && \
			python manage.py runserver 0.0.0.0:8000"

# Affiche la liste des commandes disponibles
help:
	@echo "Commandes disponibles :"
	@awk '/^# / { desc=$$0; getline; if ($$0 ~ /^[a-zA-Z0-9_-]+:.*$$/) { gsub(/^## /, "", desc); printf "  \033[36m%-16s\033[0m %s\n", $$1, desc } }' $(MAKEFILE_LIST)
