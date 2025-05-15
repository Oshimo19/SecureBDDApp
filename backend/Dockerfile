FROM python:3.13-slim

# Creer le repertoire de l application
WORKDIR /app

# Installer les dependances
COPY app/requirements.txt .
RUN pip install --upgrade pip --no-cache-dir \
 && pip install --no-cache-dir -r requirements.txt

# Copier le reste de l app
COPY app/ .

# Définir le port par défaut (pour debug local)
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
