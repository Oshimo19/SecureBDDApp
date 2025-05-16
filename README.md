# SecureBDDApp

SecureBDDApp est un projet Django sécurisé avec base de données PostgreSQL. Il est conçu selon les bonnes pratiques de cybersécurité web, incluant un middleware personnalisé, une API RESTful avec JWT, la limitation des tentatives de connexion (bruteforce), et une architecture Docker prête pour la production.

---

## 🚀 Lancement rapide

### 1. Cloner le dépôt

```bash
git clone https://github.com/mon-repo/SecureBDDApp.git
cd SecureBDDApp
```

### 2. Configurer l'environnement

Créer un fichier `.env` à la racine du projet :

```env
POSTGRES_DB=securedb
POSTGRES_USER=secureuser
POSTGRES_PASSWORD=securepass
POSTGRES_HOST=pgsdb
POSTGRES_PORT=5432
DJANGO_SECRET_KEY=dev-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1
POSTGRES_CONTAINER_NAME=securebdd-db
DJANGO_CONTAINER_NAME=securebdd-django
POSTGRES_VERSION=15
POSTGRES_INITDB_ARGS=--auth-host=scram-sha-256
```

### 3. Lancer l'application

```bash
docker compose up --build
```

---

## 🧪 Tests de sécurité et de l’API

### Exécution

```bash
sudo ./backend/app/testAPI.sh
sudo ./backend/app/testAPI2.sh
```

- `testAPI.sh` : Test d'inscription, login, profil, accès admin, bruteforce
- `testAPI2.sh` : Test XSS, suppression, élévation de privilèges

---

## 🛡️ OWASP Dependency-Check

### Initialisation (si besoin)

```bash
make startOWASPDepCheck
```

### Lancer le scan :

```bash
make runOWASPDepCheck
```

Rapport généré dans `./securityReports/dependency-check-report.html`

---

## 🔐 Fonctionnalités de sécurité implémentées

- Middleware d'authentification JWT (sans dépendance externe)
- Middleware anti-bruteforce basé sur IP/email
- Validation stricte des champs (regex, sanitizing)
- Contrôle d’accès (BAC vertical & horizontal)
- Logging de sécurité (`checkDBtests.py`)
- Protection contre XSS dans les champs `firstName` et `lastName`

---

## 📁 Arborescence simplifiée

```bash
SecureBDDApp
├── backend/app/accounts/       # App Django sécurisée
├── backend/app/testAPI.sh      # Script de test API simple
├── backend/app/testAPI2.sh     # Script de test API avancé (XSS, suppression, escalade)
├── backend/runOWASPDepCheck.sh # Scan sécurité OWASP
├── databases/                  # Scripts TLS/SSL (optionnel)
├── docker-compose.yml          # Configuration Docker
├── Makefile                    # Commandes automatisées
├── securityReports/            # Rapport OWASP
└── .env                        # Variables d'environnement
```

---

## ❌ Limites actuelles

- Pas encore de suppression admin via API (sécurité volontaire)
- Pas de frontend (Vue.js/React) actuellement
- Le token JWT n’est pas invalidé côté client après logout
- Pas encore de CI/CD ou production HTTPS avec Nginx

---

## 🚧 Améliorations futures

- 🔄 Ajout d’un frontend sécurisé (Vue.js ou React)
- 🔐 Support TLSv1.3 sur PostgreSQL avec certificats CA
- ⚙️ Déploiement production (reverse proxy Nginx + HTTPS)
- 🔍 Intégration de SonarQube ou Bandit
- 📦 Pipeline CI/CD avec GitHub Actions
- ⛔ Invalidation des tokens JWT côté client

---

## 📸 Schémas dans le dossier `docs/` (branche `dev`)

- MCD (Modèle Conceptuel de Données)
- Cas d'utilisation (UML)
- Séquence login JWT
- Séquence suppression utilisateur admin

---

## 📜 Licence

Projet réalisé dans un cadre pédagogique.
Auteur : Michel WU - Etudiant IPSSI Promo 2026
