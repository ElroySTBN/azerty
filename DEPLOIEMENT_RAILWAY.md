# 🚂 Guide de Déploiement Railway - Le Bon Mot

## ✅ Checklist Avant Déploiement

- [x] `Procfile` créé
- [x] `main_simple.py` prêt
- [x] Base de données SQLite configurée
- [x] `.env` local (NE PAS PUSHER)
- [x] `.gitignore` configuré

---

## 🚀 Étapes de Déploiement

### 1️⃣ Push sur GitHub

```bash
cd /Users/elroysitbon/-hh
git add .
git commit -m "Le Bon Mot - Version Simple MVP"
git push origin main
```

### 2️⃣ Configurer Railway

1. Allez sur [railway.app](https://railway.app)
2. Cliquez sur **"New Project"**
3. Sélectionnez **"Deploy from GitHub repo"**
4. Choisissez votre repo `-hh`

### 3️⃣ Ajouter les Variables d'Environnement

Dans Railway, allez dans **Settings > Variables** et ajoutez :

| Variable | Valeur |
|----------|--------|
| `CLIENT_BOT_TOKEN` | `votre_token_telegram` |
| `PORT` | *(Railway le configure automatiquement)* |

### 4️⃣ Vérifier le Déploiement

Railway va :
1. Détecter automatiquement le `Procfile`
2. Installer les dépendances depuis `requirements.txt`
3. Lancer `python3 main_simple.py`

### 5️⃣ Tester

Une fois déployé :
- Le bot Telegram sera actif 24/7
- Le dashboard sera accessible sur `https://votre-app.railway.app`
- Login : `admin123`

---

## 🔧 Configuration du Bot Telegram

1. Allez sur [@BotFather](https://t.me/BotFather)
2. Créez un nouveau bot : `/newbot`
3. Copiez le token
4. Ajoutez-le dans Railway comme `CLIENT_BOT_TOKEN`

---

## 📊 Monitoring

### Logs en Temps Réel

Dans Railway, cliquez sur **Deployments** puis **View Logs** pour voir :
- Démarrage du dashboard
- Démarrage du bot Telegram
- Messages reçus/envoyés

### Base de Données

La base de données SQLite (`lebonmot_simple.db`) est créée automatiquement au premier lancement.

⚠️ **Important** : Railway utilise un stockage éphémère. Les données peuvent être perdues lors d'un redéploiement.

**Solution** : Passer à PostgreSQL si besoin de persistance (migration facile).

---

## 🛠️ Commandes Utiles

### Forcer un Redéploiement

```bash
git commit --allow-empty -m "Redeploy"
git push origin main
```

### Vérifier l'État du Bot

Visitez `https://votre-app.railway.app/login` - si la page s'affiche, tout fonctionne.

---

## 🐛 Troubleshooting

### "Application failed to respond"

**Cause** : Le bot n'a pas démarré ou le port n'est pas bon.

**Solution** :
1. Vérifiez les logs Railway
2. Vérifiez que `CLIENT_BOT_TOKEN` est bien configuré
3. Relancez le déploiement

### "Bot not responding"

**Cause** : Conflit avec une autre instance du bot.

**Solution** :
1. Arrêtez TOUTES les instances locales du bot
2. Attendez 1-2 minutes
3. Redéployez sur Railway

### "Database locked"

**Cause** : Plusieurs processus tentent d'accéder à la DB.

**Solution** : Redémarrez l'app Railway.

---

## 📞 Support

Si un problème persiste :
1. Consultez les logs Railway
2. Vérifiez que le `CLIENT_BOT_TOKEN` est valide
3. Testez en local d'abord : `python3 main_simple.py`

---

## 🎯 Prochaines Étapes (Optionnel)

- [ ] Migrer vers PostgreSQL pour la persistance
- [ ] Ajouter un système de notifications admin
- [ ] Intégrer un système de paiement crypto
- [ ] Dashboard mobile PWA

---

**Version Simple MVP** - Prêt à être déployé ! 🚀

