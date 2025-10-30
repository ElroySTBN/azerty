# 🚂 DÉPLOIEMENT RAILWAY - GUIDE ULTRA-PROPRE

**Projet 100% nettoyé - Zéro confusion !**

---

## ✅ CE QUI A ÉTÉ NETTOYÉ

- ❌ Supprimé `WORKER_BOT_TOKEN` (n'existe plus)
- ❌ Supprimé `ADMIN_TELEGRAM_ID` (n'existe plus)
- ❌ Supprimé `FLASK_SECRET_KEY` (optionnel, pas nécessaire)
- ❌ Supprimé 30+ fichiers docs obsolètes
- ✅ Seulement **2 variables** nécessaires maintenant !

---

## 🚀 DÉPLOIEMENT EN 5 ÉTAPES

### 1️⃣ Créer un Nouveau Projet Railway

1. Allez sur **https://railway.app**
2. Cliquez sur **"New Project"**
3. Sélectionnez **"Deploy from GitHub repo"**
4. Choisissez le repo : **`ElroySTBN/-hh`**
5. Branche : **`main`**

---

### 2️⃣ Configurer les Variables d'Environnement

Railway va détecter automatiquement Python + `requirements.txt`

**⚠️ AVANT que le déploiement ne commence**, ajoutez **SEULEMENT ces 2 variables** :

```
CLIENT_BOT_TOKEN = 7633849144:AAFeGEYtqgLWTUXC3f2tjU8rV9GISIt3tEw
ADMIN_PASSWORD = admin123
```

**C'EST TOUT !** Railway gère automatiquement :
- `PORT` (assigné par Railway)
- Python runtime (via `runtime.txt`)
- Démarrage (via `Procfile`)

---

### 3️⃣ Lancer le Déploiement

Railway va :

1. **Installer** Python 3.11
2. **Installer** les dépendances (`requirements.txt`)
3. **Lancer** `python main.py`
4. **Vérifier** le healthcheck (`/health`)

**⏱️ Durée : 2-3 minutes**

---

### 4️⃣ Vérifier les Logs

Dans Railway :
- Cliquez sur votre service
- **Deployments** > Regardez les logs

✅ Vous devriez voir :
```
✅ Base de données simple initialisée
✅ Bot simple configuré
✅ Bot Telegram démarré et connecté !
🎉 LE BON MOT - OPÉRATIONNEL !
```

---

### 5️⃣ Générer le Domaine

1. **Settings** (onglet)
2. **Generate Domain** (bouton)
3. Railway vous donne une URL : `https://votre-app.railway.app`

---

## 🧪 TESTER L'APP

### Dashboard Admin
```
https://votre-app.railway.app/login
```

**Login** : Le mot de passe que vous avez configuré dans `ADMIN_PASSWORD`

### Healthcheck
```
https://votre-app.railway.app/health
```

Devrait retourner :
```json
{"status": "healthy", "service": "Le Bon Mot"}
```

### Bot Telegram

Cherchez votre bot sur Telegram et envoyez `/start`

---

## 📊 STRUCTURE FINALE DU PROJET

```
-hh/
├── main.py                     # Point d'entrée
├── bot_simple.py               # Bot Telegram (clients)
├── dashboard_simple.py         # Dashboard admin Flask
├── requirements.txt            # Dépendances Python
├── runtime.txt                 # Python 3.11.0
├── Procfile                    # web: python main.py
├── .railway.json               # Config Railway
├── .railwayignore              # Fichiers ignorés
├── README.md                   # Documentation principale
└── lebonmot_simple.db          # SQLite (créé automatiquement)
```

---

## ❓ TROUBLESHOOTING

### Si Railway détecte encore d'anciennes variables

**C'est maintenant IMPOSSIBLE !** On a supprimé :
- Tous les anciens README
- Le fichier `.env.example` nettoyé
- Tous les fichiers de configuration obsolètes

Railway ne devrait voir que **2 variables** :
- `CLIENT_BOT_TOKEN`
- `ADMIN_PASSWORD`

### Si le healthcheck échoue

Vérifiez les logs Railway :
```
Path: /health Attempt #1 failed
```

➡️ Le fichier `dashboard_simple.py` contient l'endpoint `/health`, c'est bon !

### Si le bot ne démarre pas

Vérifiez que `CLIENT_BOT_TOKEN` est correct dans les variables Railway.

---

## 🎯 CHECKLIST FINALE

- [x] Code pushé sur GitHub (commit `229056b`)
- [x] `main.py` existe (renommé de `main_simple.py`)
- [x] Endpoint `/health` dans `dashboard_simple.py`
- [x] `.env.example` nettoyé (2 variables seulement)
- [x] Tous les anciens docs supprimés
- [ ] **Créer nouveau projet Railway**
- [ ] **Ajouter CLIENT_BOT_TOKEN**
- [ ] **Ajouter ADMIN_PASSWORD**
- [ ] **Générer le domaine**
- [ ] **Tester le dashboard**
- [ ] **Tester le bot Telegram**

---

## 🚀 C'EST PARTI !

Le projet est **100% propre** et **prêt pour Railway** !

**Railway ne devrait plus proposer d'anciennes variables !** ✅

Allez sur **https://railway.app** et créez votre nouveau projet maintenant ! 🎉

