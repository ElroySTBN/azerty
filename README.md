# 🔐 Le Bon Mot - Service Anonyme de E-réputation

Bot Telegram et Dashboard Admin pour gérer un service de marketplace d'avis en ligne.

## 🚀 Fonctionnalités

### Bot Telegram Client
- ✅ Commande d'avis (Google, Trustpilot, autres plateformes)
- ✅ Workflow complet de commande en 6 étapes
- ✅ Génération de contenu optionnelle (+0.50 USDT/avis)
- ✅ Paiement en crypto (Bitcoin/USDT)
- ✅ Support client intégré avec conversation continue
- ✅ Suivi des commandes en temps réel
- ✅ Garanties et sécurité

### Dashboard Admin
- ✅ Gestion des commandes
- ✅ Messagerie support bidirectionnelle
- ✅ Affichage des infos clients (ID Telegram, username)
- ✅ Statistiques en temps réel
- ✅ Mode simplifié (gestion manuelle)

## 📋 Prérequis

- Python 3.11+
- Bot Telegram (créé via @BotFather)
- Compte pour hébergement (Railway, Render, VPS, etc.)

## 🔧 Installation

### 1. Cloner le repository

```bash
git clone https://github.com/VOTRE_USERNAME/lebonmot-bot.git
cd lebonmot-bot
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configuration

Créez un fichier `.env` à la racine :

```env
CLIENT_BOT_TOKEN=votre_token_telegram
ADMIN_PASSWORD=votre_mot_de_passe_admin
FLASK_SECRET_KEY=votre_clé_secrète_flask
```

### 4. Lancer l'application

```bash
python3 main.py
```

L'application sera accessible sur :
- **Bot Telegram** : Votre bot configuré
- **Dashboard Admin** : http://localhost:8081
  - Username : `admin`
  - Password : celui défini dans `.env`

## 🌐 Déploiement en production

### Option 1 : Railway

1. Créez un compte sur [Railway.app](https://railway.app)
2. Connectez votre repository GitHub
3. Ajoutez les variables d'environnement :
   - `CLIENT_BOT_TOKEN`
   - `ADMIN_PASSWORD`
   - `FLASK_SECRET_KEY`
4. Railway détectera automatiquement Python et installera les dépendances
5. Changez le port dans `main.py` si nécessaire (Railway utilise la variable `PORT`)

### Option 2 : Render

1. Créez un compte sur [Render.com](https://render.com)
2. Créez un nouveau "Web Service"
3. Connectez votre repository GitHub
4. Configurez :
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `python3 main.py`
5. Ajoutez les variables d'environnement

### Option 3 : VPS (Ubuntu/Debian)

```bash
# Installation
sudo apt update
sudo apt install python3 python3-pip git

# Cloner le repo
git clone https://github.com/VOTRE_USERNAME/lebonmot-bot.git
cd lebonmot-bot

# Installation des dépendances
pip3 install -r requirements.txt

# Créer le fichier .env
nano .env
# (Copiez vos variables d'environnement)

# Lancer avec screen ou tmux
screen -S lebonmot
python3 main.py
# Ctrl+A puis D pour détacher

# Ou utiliser systemd (recommandé)
sudo nano /etc/systemd/system/lebonmot.service
```

#### Fichier systemd `/etc/systemd/system/lebonmot.service` :

```ini
[Unit]
Description=Le Bon Mot Bot
After=network.target

[Service]
Type=simple
User=votre_user
WorkingDirectory=/chemin/vers/lebonmot-bot
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Activer et démarrer le service
sudo systemctl enable lebonmot
sudo systemctl start lebonmot
sudo systemctl status lebonmot
```

## 📱 Utilisation

### Pour les clients (Telegram)

1. Démarrez le bot avec `/start`
2. Choisissez "📝 Commander des avis"
3. Suivez le workflow en 6 étapes
4. Effectuez le paiement
5. Contactez le support pour confirmer
6. Recevez vos avis sous 48-72h

### Pour l'admin (Dashboard)

1. Accédez au dashboard (http://votre-url:8081)
2. Connectez-vous avec vos identifiants
3. Gérez les commandes
4. Répondez aux messages support
5. Changez les statuts manuellement

## 🗂️ Structure du projet

```
lebonmot-bot/
├── main.py                 # Point d'entrée
├── requirements.txt        # Dépendances Python
├── .env.example           # Exemple de configuration
├── reset_bot.py           # Utilitaire pour réinitialiser le bot
├── src/
│   ├── client_bot.py      # Logique du bot Telegram
│   ├── database.py        # Gestion SQLite
│   └── web_admin.py       # Dashboard Flask
├── templates/             # Templates HTML
│   ├── dashboard.html
│   ├── login.html
│   ├── messages.html
│   ├── client_messages.html
│   └── order_details.html
├── static/
│   └── style.css          # Styles du dashboard
└── uploads/               # Fichiers uploadés (git ignoré)
```

## 🔒 Sécurité

- ✅ Authentification admin obligatoire
- ✅ Session Flask sécurisée
- ✅ Fichiers sensibles ignorés par git
- ✅ Variables d'environnement pour les secrets
- ✅ Anonymat des clients (ID aléatoires)

⚠️ **Important** : 
- Ne commitez JAMAIS le fichier `.env`
- Utilisez des mots de passe forts en production
- Configurez un reverse proxy (nginx) en production
- Utilisez HTTPS pour le dashboard

## 🛠️ Maintenance

### Voir les logs

```bash
# Si lancé avec systemd
sudo journalctl -u lebonmot -f

# Si lancé avec screen
screen -r lebonmot
```

### Mettre à jour

```bash
cd lebonmot-bot
git pull
pip3 install -r requirements.txt --upgrade
sudo systemctl restart lebonmot  # Si systemd
```

### Réinitialiser le bot (en cas de conflit)

```bash
python3 reset_bot.py
```

## 📊 Base de données

SQLite est utilisé par défaut. En production, les données sont stockées dans `marketplace.db`.

### Tables principales :
- `clients` : Informations clients
- `orders` : Commandes
- `support_messages` : Messages support
- `reviews` : Contenu des avis

### Backup

```bash
# Créer un backup
cp marketplace.db marketplace_backup_$(date +%Y%m%d).db

# Planifier des backups automatiques (cron)
0 2 * * * cd /chemin/vers/lebonmot-bot && cp marketplace.db backups/marketplace_$(date +\%Y\%m\%d).db
```

## 🐛 Dépannage

### Le bot ne répond pas
```bash
python3 reset_bot.py
python3 main.py
```

### Port 8081 déjà utilisé
Changez le port dans `main.py` ligne 26 :
```python
app.run(host='0.0.0.0', port=8082, debug=False, use_reloader=False)
```

### Erreur de base de données
```bash
# Supprimer et recréer la base
rm marketplace.db
python3 main.py  # Recrée automatiquement
```

## 📝 Documentation complémentaire

- [`DÉMARRAGE.md`](DÉMARRAGE.md) - Guide de démarrage rapide
- [`SIMPLIFICATIONS_MVP.md`](SIMPLIFICATIONS_MVP.md) - Choix d'architecture MVP
- [`DASHBOARD_GUIDE.md`](DASHBOARD_GUIDE.md) - Guide du dashboard admin
- [`CORRECTIONS_FINALES.md`](CORRECTIONS_FINALES.md) - Dernières corrections

## 🤝 Support

Pour toute question :
- Ouvrez une issue sur GitHub
- Contactez l'équipe de développement

## 📜 Licence

Propriétaire - Tous droits réservés

---

**⚠️ Note** : Ce projet est un MVP. Certaines fonctionnalités sont volontairement simplifiées pour faciliter le lancement. L'automatisation complète viendra dans les versions futures.

**🎯 Version actuelle** : 1.0.0 MVP
