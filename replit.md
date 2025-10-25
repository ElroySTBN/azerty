# Marketplace d'avis en ligne

## Vue d'ensemble

Marketplace anonyme de gestion de réputation en ligne avec 2 bots Telegram et un dashboard admin Flask.

### Composants principaux

1. **Bot Client Telegram** - Pour les entreprises qui commandent des avis
2. **Bot Worker Telegram** - Pour les microworkers qui exécutent les tâches  
3. **Dashboard Web Admin** - Interface Flask pour gérer commandes et workers

### Stack technique

- Python 3.11
- python-telegram-bot (async)
- Flask (dashboard web)
- SQLite (base de données)
- Tout tourne en single process sur Replit

## Architecture du projet

```
├── src/
│   ├── database.py         # Gestion de la base de données SQLite
│   ├── client_bot.py       # Bot Telegram pour les clients
│   ├── worker_bot.py       # Bot Telegram pour les workers
│   └── web_admin.py        # Dashboard Flask admin
├── templates/              # Templates HTML pour Flask
│   ├── login.html
│   ├── dashboard.html
│   ├── order_details.html
│   └── screenshot.html
├── static/
│   └── style.css           # Styles CSS
├── uploads/                # Screenshots des workers
├── main.py                 # Point d'entrée principal
├── marketplace.db          # Base de données SQLite
└── .env                    # Variables d'environnement

```

## Base de données

### Tables

- **clients** - Entreprises qui commandent (ID anonyme C-XXXX)
- **workers** - Microworkers (ID anonyme WRK-XXX)
- **orders** - Commandes d'avis
- **reviews** - Contenu des avis à distribuer
- **tasks** - Tâches affectées aux workers

## Fonctionnalités MVP

### Bot Client

- ✅ Interface d'accueil avec ID anonyme
- ✅ Menu de commande d'avis (Google, Trustpilot, Pages Jaunes, Autre)
- ✅ Calcul automatique de prix (5 USDT par avis)
- ✅ Gestion des briefs
- ✅ Suivi des commandes

### Bot Worker

- ✅ Dashboard personnel avec profil, niveau et solde
- ✅ Liste des tâches disponibles avec détails
- ✅ Système d'acceptation de tâches
- ✅ Soumission de preuves (screenshot + lien)
- ✅ Suivi des gains

### Dashboard Admin

- ✅ Authentification par mot de passe
- ✅ Vue d'ensemble avec statistiques
- ✅ Gestion complète des commandes
- ✅ Éditeur d'avis manuel (saisie + import fichier .txt)
- ✅ Distribution des tâches aux workers
- ✅ Validation/rejet des tâches soumises
- ✅ Gestion des workers (validation, blocage)

## Configuration

### 1. Créer les bots Telegram

1. Aller sur https://t.me/BotFather
2. Créer 2 bots avec `/newbot`
3. Copier les tokens

### 2. Configurer les variables d'environnement

Créer un fichier `.env` à la racine :

```env
CLIENT_BOT_TOKEN=votre_token_bot_client
WORKER_BOT_TOKEN=votre_token_bot_worker
ADMIN_PASSWORD=votre_mot_de_passe
FLASK_SECRET_KEY=une_cle_secrete_aleatoire
```

### 3. Lancer l'application

```bash
python main.py
```

## Accès

- **Dashboard Admin**: http://localhost:5000
  - Username: `admin`
  - Password: (celui défini dans .env)

- **Bot Client**: Cherchez votre bot sur Telegram et faites `/start`
- **Bot Worker**: Cherchez votre bot sur Telegram et faites `/start`

## Workflow

### Pour commander des avis (Client)

1. Démarrer le bot client sur Telegram
2. Cliquer sur "Commander des avis"
3. Sélectionner la plateforme
4. Entrer la quantité
5. Fournir le lien cible
6. Décrire le brief

### Pour créer et distribuer les avis (Admin)

1. Se connecter au dashboard
2. Cliquer sur "Gérer" pour la commande
3. Rédiger les avis manuellement ou importer un fichier .txt
4. Cliquer sur "DISTRIBUER AUX WORKERS"
5. Les tâches sont créées et notifiées aux workers

### Pour exécuter une tâche (Worker)

1. Démarrer le bot worker sur Telegram
2. Voir les tâches disponibles
3. Accepter une tâche
4. Publier l'avis sur la plateforme
5. Envoyer screenshot + lien
6. Attendre la validation

### Pour valider (Admin)

1. Aller dans "Tâches en validation"
2. Voir le screenshot et le lien
3. Valider ou refuser
4. Le solde du worker est mis à jour automatiquement

## Changements récents

- **2024-10-25**: Création du MVP complet
  - Architecture des 2 bots Telegram
  - Dashboard admin Flask
  - Système de validation des tâches
  - Gestion anonyme des clients et workers

## Préférences utilisateur

- Pas de génération automatique d'avis (saisie manuelle uniquement)
- Anonymat total (pas de données personnelles)
- Interface simple et épurée
- Focus sur la sécurité et la discrétion
