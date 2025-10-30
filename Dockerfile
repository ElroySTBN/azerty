FROM python:3.11-slim

# Installer sqlite3 et autres dépendances système (optimisé pour taille minimale)
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Variables d'environnement Python pour optimiser la mémoire
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Créer le répertoire de travail
WORKDIR /app

# Copier les requirements et installer les dépendances Python (cache optimisé)
COPY requirements.txt .
RUN pip install --no-cache-dir --compile -r requirements.txt

# Copier le code de l'application
COPY . .

# Créer le dossier /data pour la DB (persistent storage Railway)
RUN mkdir -p /data && chmod 755 /data

# Exposer le port (Railway le gérera automatiquement via PORT)
EXPOSE 8080

# Commande de démarrage avec optimisations Python
CMD ["python", "-O", "main.py"]

