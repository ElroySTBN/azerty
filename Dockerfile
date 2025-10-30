FROM python:3.11-slim

# Installer sqlite3 et autres dépendances système
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Copier les requirements et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Créer le dossier /data pour la DB (persistent storage Railway)
RUN mkdir -p /data

# Exposer le port (Railway le gérera automatiquement via PORT)
EXPOSE 8080

# Commande de démarrage
CMD ["python", "main.py"]

