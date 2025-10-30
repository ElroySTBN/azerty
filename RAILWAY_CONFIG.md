# ⚙️ Configuration Railway - Le Bon Mot

## ✅ FIX APPLIQUÉ !

J'ai ajouté l'endpoint `/health` qui manquait ! Railway va maintenant pouvoir déployer correctement.

---

## 🔧 Variables d'Environnement à Configurer

### ✅ Variables NÉCESSAIRES

Dans Railway, **gardez SEULEMENT ces 2 variables** :

| Variable | Valeur | Description |
|----------|--------|-------------|
| `CLIENT_BOT_TOKEN` | Votre token Telegram | ✅ OBLIGATOIRE |
| `ADMIN_PASSWORD` | Votre mot de passe admin | ✅ OBLIGATOIRE |

### ❌ Variables à SUPPRIMER

Supprimez ces variables, elles ne servent plus :

| Variable | Raison |
|----------|--------|
| `MINIAPP_URL` | ❌ Mini App abandonnée |
| `FLASK_SECRET_KEY` | ❌ Optionnelle (valeur par défaut OK) |

⚠️ **IMPORTANT** : Ne configurez PAS la variable `PORT`. Railway la gère automatiquement.

---

## 🚀 Procédure de Déploiement

### 1️⃣ Dans Railway

1. **Allez dans votre projet Railway**
2. **Cliquez sur votre service `-hh`**
3. **Variables > Settings**
4. **Supprimez** : `MINIAPP_URL` et `FLASK_SECRET_KEY`
5. **Gardez** : `CLIENT_BOT_TOKEN` et `ADMIN_PASSWORD`

### 2️⃣ Railway va Redéployer Automatiquement

Railway détecte le nouveau push GitHub et redéploie automatiquement ! ⏱️

### 3️⃣ Vérifier les Logs

Dans Railway, onglet **Deployments** :

Vous devriez voir :
```
✅ Bot Telegram démarré
✅ Dashboard admin démarré
🎉 LE BON MOT - OPÉRATIONNEL !
```

Et le healthcheck devrait réussir :
```
✅ Healthcheck passed!
```

---

## 🎯 Qu'est-ce qui a été Corrigé ?

### Avant (❌ Erreur)
```
Path: /health
Attempt #1 failed with service unavailable
...
Healthcheck failed!
```

### Maintenant (✅ Fonctionne)
```
GET /health
→ 200 OK
{
  "status": "healthy",
  "service": "Le Bon Mot"
}
```

---

## 📊 Ce Que Railway va Faire

1. **Build** : Installer Python + dépendances ✅
2. **Deploy** : Lancer `python main_simple.py` ✅
3. **Healthcheck** : Vérifier `/health` toutes les 10s ✅ (nouveau !)
4. **Démarrage** :
   - Flask sur le port automatique de Railway
   - Bot Telegram connecté
   - Dashboard accessible

---

## 🌐 Accès à Votre App

Une fois déployé :

### Dashboard Admin
```
https://votre-app.railway.app/login
```

**Mot de passe** : Celui que vous avez configuré dans `ADMIN_PASSWORD`

### Bot Telegram
Le bot sera actif 24/7 sur Telegram ! 🤖

---

## 🐛 Si Ça ne Marche Toujours Pas

### 1️⃣ Vérifier les Logs
Railway > Service `-hh` > Deployments > View Logs

### 2️⃣ Erreurs Possibles

#### "CLIENT_BOT_TOKEN not found"
➡️ Vérifiez que la variable est bien configurée sur Railway

#### "Port already in use"
➡️ Supprimez la variable `PORT` si elle existe (Railway la gère auto)

#### "Conflict: terminated by other getUpdates"
➡️ Arrêtez TOUS les bots locaux sur votre Mac :
```bash
ps aux | grep "main_simple.py" | grep -v grep | awk '{print $2}' | xargs kill -9
```

---

## ✅ Checklist Finale

- [x] Endpoint `/health` ajouté
- [x] Code pushé sur GitHub (commit `f89fc2c`)
- [ ] **TODO : Supprimer `MINIAPP_URL` sur Railway**
- [ ] **TODO : Supprimer `FLASK_SECRET_KEY` sur Railway** (optionnel)
- [ ] **TODO : Vérifier que `CLIENT_BOT_TOKEN` et `ADMIN_PASSWORD` sont bien configurés**
- [ ] **TODO : Attendre le redéploiement (2-3 min)**
- [ ] **TODO : Tester le dashboard sur Railway**

---

## 🎉 Prochaines Étapes

1. **Supprimez les variables inutiles** sur Railway
2. **Attendez 2-3 minutes** que Railway redéploie
3. **Testez votre dashboard** : `https://votre-app.railway.app/login`
4. **Testez votre bot** sur Telegram

---

**🚀 Le code est prêt, Railway va redéployer automatiquement !**

**Temps estimé** : 2-3 minutes ⏱️

