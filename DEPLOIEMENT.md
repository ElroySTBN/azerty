# 🚀 Guide de Déploiement - Le Bon Mot

## 📋 Avant de déployer

### Checklist

- [ ] Repository GitHub créé et configuré
- [ ] Token Telegram bot obtenu (@BotFather)
- [ ] Compte hébergement créé (Railway/Render/VPS)
- [ ] Variables d'environnement préparées
- [ ] Tests locaux réussis

---

## 🌐 Méthode 1 : Railway.app (Recommandé - Gratuit)

### Avantages
- ✅ Gratuit jusqu'à 500h/mois
- ✅ Déploiement automatique depuis GitHub
- ✅ SSL/HTTPS inclus
- ✅ Base de données persistante
- ✅ Logs en temps réel

### Instructions

1. **Créer un compte**
   - Allez sur [Railway.app](https://railway.app)
   - Inscrivez-vous avec GitHub

2. **Nouveau projet**
   - Cliquez sur "New Project"
   - Sélectionnez "Deploy from GitHub repo"
   - Choisissez votre repository `lebonmot-bot`

3. **Configuration des variables**
   - Dans le projet, allez dans "Variables"
   - Ajoutez :
     ```
     CLIENT_BOT_TOKEN = votre_token_telegram
     ADMIN_PASSWORD = votre_mot_de_passe
     FLASK_SECRET_KEY = votre_cle_secrete
     PORT = 8081
     ```

4. **Déploiement**
   - Railway détecte automatiquement Python
   - Le build démarre automatiquement
   - Attendez que le statut passe à "Active"

5. **Accéder au dashboard**
   - Dans "Settings" → "Domains"
   - Railway génère une URL (ex: `lebonmot.up.railway.app`)
   - Accédez à : `https://votre-url.railway.app:8081`

6. **Vérifier le bot**
   - Testez sur Telegram avec `/start`
   - Le bot devrait répondre

### Logs et monitoring

```bash
# Via l'interface Railway
- Onglet "Deployments" → Logs
- Temps réel

# Via CLI Railway
railway logs
```

---

## 🌐 Méthode 2 : Render.com (Gratuit)

### Avantages
- ✅ Gratuit (avec limitations)
- ✅ SSL automatique
- ✅ Facile à configurer

### Instructions

1. **Créer un compte**
   - [Render.com](https://render.com)

2. **Nouveau Web Service**
   - "New" → "Web Service"
   - Connectez GitHub
   - Sélectionnez le repository

3. **Configuration**
   ```
   Name: lebonmot-bot
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python3 main.py
   ```

4. **Variables d'environnement**
   - Ajoutez les mêmes variables que Railway

5. **Déployer**
   - Cliquez "Create Web Service"
   - Attendez le déploiement

⚠️ **Note** : Render met en veille après 15 min d'inactivité (plan gratuit)

---

## 💻 Méthode 3 : VPS (Ionos, OVH, etc.)

[[memory:3750916]]

### Prérequis
- VPS avec Ubuntu 20.04+ ou Debian 11+
- Accès SSH root
- Nom de domaine (optionnel)

### Installation complète

#### 1. Connexion SSH

```bash
ssh root@votre-ip-vps
```

#### 2. Installation des dépendances

```bash
# Mise à jour système
sudo apt update && sudo apt upgrade -y

# Installation Python et outils
sudo apt install -y python3 python3-pip python3-venv git nginx

# Installation de certbot pour SSL (si domaine)
sudo apt install -y certbot python3-certbot-nginx
```

#### 3. Création d'un utilisateur dédié

```bash
# Créer un utilisateur
sudo adduser lebonmot
sudo usermod -aG sudo lebonmot

# Passer à cet utilisateur
su - lebonmot
```

#### 4. Clone du repository

```bash
cd /home/lebonmot
git clone https://github.com/VOTRE_USERNAME/lebonmot-bot.git
cd lebonmot-bot
```

#### 5. Configuration

```bash
# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Créer .env
nano .env
# Copiez vos variables
```

#### 6. Service systemd

```bash
sudo nano /etc/systemd/system/lebonmot.service
```

Contenu :
```ini
[Unit]
Description=Le Bon Mot Bot & Dashboard
After=network.target

[Service]
Type=simple
User=lebonmot
WorkingDirectory=/home/lebonmot/lebonmot-bot
Environment="PATH=/home/lebonmot/lebonmot-bot/venv/bin"
ExecStart=/home/lebonmot/lebonmot-bot/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Activer le service
sudo systemctl daemon-reload
sudo systemctl enable lebonmot
sudo systemctl start lebonmot
sudo systemctl status lebonmot
```

#### 7. Configuration Nginx (reverse proxy)

```bash
sudo nano /etc/nginx/sites-available/lebonmot
```

Contenu :
```nginx
server {
    listen 80;
    server_name votre-domaine.com;  # ou votre IP

    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Activer le site
sudo ln -s /etc/nginx/sites-available/lebonmot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 8. SSL avec Let's Encrypt (si domaine)

```bash
sudo certbot --nginx -d votre-domaine.com
```

#### 9. Firewall

```bash
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### Maintenance VPS

#### Voir les logs
```bash
sudo journalctl -u lebonmot -f
```

#### Redémarrer le service
```bash
sudo systemctl restart lebonmot
```

#### Mettre à jour
```bash
cd /home/lebonmot/lebonmot-bot
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart lebonmot
```

#### Backup automatique
```bash
# Créer script de backup
nano /home/lebonmot/backup.sh
```

Contenu :
```bash
#!/bin/bash
BACKUP_DIR="/home/lebonmot/backups"
mkdir -p $BACKUP_DIR
cp /home/lebonmot/lebonmot-bot/marketplace.db $BACKUP_DIR/marketplace_$(date +%Y%m%d_%H%M%S).db
# Garder seulement les 7 derniers jours
find $BACKUP_DIR -name "marketplace_*.db" -mtime +7 -delete
```

```bash
chmod +x /home/lebonmot/backup.sh

# Ajouter au cron (tous les jours à 2h du matin)
crontab -e
# Ajouter :
0 2 * * * /home/lebonmot/backup.sh
```

---

## 📊 Monitoring et logs

### Railway / Render
- Interface web intégrée
- Logs en temps réel

### VPS

```bash
# Logs en temps réel
sudo journalctl -u lebonmot -f

# Logs des 100 dernières lignes
sudo journalctl -u lebonmot -n 100

# Logs avec filtre d'erreur
sudo journalctl -u lebonmot | grep ERROR
```

---

## 🔒 Sécurité post-déploiement

### Checklist sécurité

- [ ] Mot de passe admin fort (min 16 caractères)
- [ ] FLASK_SECRET_KEY aléatoire (32+ caractères)
- [ ] SSL/HTTPS activé
- [ ] Firewall configuré (VPS)
- [ ] Backups automatiques configurés
- [ ] Logs monitoring configuré
- [ ] Variables d'environnement sécurisées

### Générer des secrets forts

```bash
# Mot de passe admin
python3 -c "import secrets; print(secrets.token_urlsafe(16))"

# FLASK_SECRET_KEY
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## ✅ Tests post-déploiement

### 1. Test du bot Telegram

```
1. Ouvrez Telegram
2. Cherchez votre bot
3. /start
4. Testez une commande complète
5. Testez le support
```

### 2. Test du dashboard

```
1. Accédez à l'URL de votre dashboard
2. Connectez-vous
3. Vérifiez que vous voyez les commandes
4. Testez les messages support
```

### 3. Test de la persistance

```
1. Créez une commande
2. Redémarrez le service
3. Vérifiez que la commande est toujours là
```

---

## 🆘 Dépannage

### Bot ne répond pas

```bash
# Railway/Render : Voir les logs
# VPS :
sudo journalctl -u lebonmot -n 50
sudo systemctl restart lebonmot
```

### Dashboard inaccessible

```bash
# Vérifier que le service tourne
sudo systemctl status lebonmot

# Vérifier nginx (VPS)
sudo nginx -t
sudo systemctl status nginx
```

### Erreur de base de données

```bash
# Sauvegarder d'abord !
cp marketplace.db marketplace_backup.db

# Recréer (perte de données)
rm marketplace.db
sudo systemctl restart lebonmot
```

---

## 📞 Support

En cas de problème :
1. Consultez les logs
2. Vérifiez la section dépannage
3. Ouvrez une issue GitHub
4. Contactez le support technique

---

**🎉 Félicitations !** Votre bot est maintenant en production ! 🚀

