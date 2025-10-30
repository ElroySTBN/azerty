# 🚂 Guide Railway - Trouver ton domaine et configurer l'app

## 1️⃣ Trouver ton domaine Railway

### Étape 1 : Va sur Railway
1. Va sur [railway.app](https://railway.app)
2. Connecte-toi avec ton compte
3. Tu verras ton **projet** (probablement nommé "lebonmot" ou similaire)

### Étape 2 : Ouvre ton projet
1. Clique sur le projet
2. Tu verras un ou plusieurs **services** (rectangles colorés)
3. Clique sur le service principal (celui qui contient ton code)

### Étape 3 : Trouve le domaine
Dans l'onglet **"Settings"** du service :
1. Cherche la section **"Networking"** ou **"Domains"**
2. Tu verras une URL qui ressemble à :
   ```
   lebonmot-production.up.railway.app
   ```
   ou
   ```
   votre-projet-production-xxxx.up.railway.app
   ```

**C'EST TON DOMAINE !** ✅

---

## 2️⃣ Configurer les variables d'environnement

### Étape 1 : Va dans l'onglet "Variables"
1. Dans ton service Railway, clique sur **"Variables"** (en haut)
2. Tu verras une liste de variables (ou vide si tu n'en as pas encore)

### Étape 2 : Ajoute ces variables OBLIGATOIRES

Clique sur **"+ New Variable"** et ajoute **UNE PAR UNE** :

```bash
# 1. Token du bot Telegram
CLIENT_BOT_TOKEN=7633849144:AAHyzWh5SwFaQtE7rf92rBbEWk3yakZtCF0

# 2. Clé secrète pour Flask (génère une chaîne aléatoire)
SECRET_KEY=change-moi-par-un-truc-random-123456789

# 3. URL de ta Mini App (remplace par TON domaine Railway)
MINIAPP_URL=https://TON-DOMAINE.railway.app

# 4. Port (Railway configure automatiquement, mais tu peux le forcer)
PORT=8080
```

### Étape 3 : Sauvegarder
- Railway **redémarre automatiquement** quand tu ajoutes/modifies des variables
- Attends 1-2 minutes pour que le redémarrage se termine

---

## 3️⃣ Vérifier que tout fonctionne

### Test 1 : Le bot Telegram
1. Ouvre Telegram
2. Cherche ton bot (le nom que tu as donné à @BotFather)
3. Lance `/start`
4. Tu devrais voir le menu avec le bouton **"🚀 Ouvrir l'app"**

### Test 2 : La Mini App
1. Va sur `https://TON-DOMAINE.railway.app`
2. Tu devrais voir la page d'accueil de la Mini App
3. Si tu vois "Not Found" ou "404", c'est que le build n'est pas terminé

### Test 3 : Le Dashboard Admin
1. Va sur `https://TON-DOMAINE.railway.app/admin`
2. Tu devrais voir la page de connexion
3. Login : `admin`
4. Password : `admin123`

---

## 🐛 Dépannage

### ❌ "Not Found" / "404"
**Problème** : Le frontend React n'est pas buildé correctement

**Solution** :
1. Va dans les **"Deployments"** de ton service Railway
2. Clique sur le dernier déploiement
3. Regarde les logs de **Build**
4. Si tu vois une erreur, partage-la moi

### ❌ Le bot ne répond pas sur Telegram
**Problème** : Le bot n'est pas démarré ou les variables ne sont pas configurées

**Solution** :
1. Vérifie que `CLIENT_BOT_TOKEN` est bien configuré dans les Variables
2. Va dans **"Deployments"** → dernier déploiement → logs de **Deploy**
3. Cherche le message : `✅ Bot client démarré`
4. Si tu vois `Conflict: terminated by other getUpdates request`, c'est que tu as une autre instance qui tourne (probablement en local sur ton Mac)

### 🔧 Forcer un redéploiement
Si rien ne fonctionne :
1. Va dans **"Deployments"**
2. Clique sur les 3 points `...` du dernier déploiement
3. Clique sur **"Redeploy"**

---

## 📝 Checklist finale

- [ ] J'ai trouvé mon domaine Railway
- [ ] J'ai ajouté `CLIENT_BOT_TOKEN` dans les Variables
- [ ] J'ai ajouté `SECRET_KEY` dans les Variables
- [ ] J'ai ajouté `MINIAPP_URL` avec MON domaine Railway
- [ ] Railway a redémarré (attendre 1-2 min)
- [ ] Le bot répond sur Telegram
- [ ] Je peux accéder à la Mini App sur mon domaine
- [ ] Je peux me connecter au dashboard admin sur `/admin`
- [ ] **IMPORTANT** : J'ai arrêté le bot en local sur mon Mac (sinon conflit !)

---

## 🆘 Si ça ne marche toujours pas

Envoie-moi :
1. Ton domaine Railway (l'URL complète)
2. Les logs de déploiement (dans Deployments → dernier déploiement)
3. Ce que tu vois quand tu vas sur ton domaine

