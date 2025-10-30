# 🔧 Configuration Volume Persistant Railway

## 🚨 Le Problème

À chaque redéploiement sur Railway, **la base de données se vide** car Railway ne monte pas de volume persistant par défaut.

---

## ✅ Solution : Configurer un Volume Persistant

### 1️⃣ Dans Railway - Ajouter un Volume Persistant

1. **Allez dans votre projet Railway**
2. **Cliquez sur votre service** (bot + dashboard)
3. **Onglet "Variables"** (ou **"Settings"**)
4. **Cherchez "Volumes"** ou **"Persistent Storage"**
5. **Cliquez sur "Add Volume"** ou **"Mount Volume"**
6. **Configurez :**
   - **Mount Path** : `/data`
   - **Size** : 1 GB (suffisant pour SQLite)
   - **Nom** : `database-storage` (ou autre)

### 2️⃣ Redéployer

Railway va automatiquement :
- ✅ Monter le volume `/data`
- ✅ Persister la base de données entre les redéploiements
- ✅ Sauvegarder toutes vos données

---

## 🧪 Vérifier que ça Fonctionne

### Après Configuration du Volume

1. **Dans les logs Railway**, vous devriez voir :
   ```
   ✅ Railway détecté : utilisation de /data/lebonmot_simple.db (volume persistant)
   📁 Base de données : /data/lebonmot_simple.db
   ```

2. **Passez une commande** via le bot

3. **Attendez quelques minutes**

4. **Faites un changement de code** (un petit changement, même un commentaire)

5. **Push sur GitHub** → Railway redéploie automatiquement

6. **Vérifiez vos commandes** → Elles devraient toujours être là ! ✅

---

## 🔍 Debug : Si ça ne Fonctionne Pas

### Vérifier les Logs Railway

Regardez les logs de démarrage :

```
✅ Base de données : /data/lebonmot_simple.db (abs: /data/lebonmot_simple.db)
```

**Si vous voyez** `./lebonmot_simple.db` au lieu de `/data/lebonmot_simple.db` :
- ❌ Le volume persistant n'est PAS monté
- ✅ **Solution** : Vérifiez que vous avez bien ajouté le volume `/data` dans Railway

---

## 📊 Emplacement des Données

### Localement
- **Fichier** : `./lebonmot_simple.db`
- **Chemin complet** : `/Users/elroysitbon/lebonmot-bot/lebonmot_simple.db`

### Sur Railway (AVEC volume persistant)
- **Fichier** : `/data/lebonmot_simple.db`
- **Persistant** : OUI ✅ (survit aux redéploiements)

### Sur Railway (SANS volume persistant)
- **Fichier** : `./lebonmot_simple.db` ou `/data/lebonmot_simple.db`
- **Persistant** : NON ❌ (perdu à chaque redéploiement)

---

## ⚠️ Important

**Sans volume persistant configuré dans Railway, vos données seront perdues à chaque redéploiement !**

**Avec volume persistant**, vos données survivent aux redéploiements, redémarrages et mises à jour.

---

## 🚀 Procédure Complète

1. **Configurez le volume persistant** dans Railway (`/data`)
2. **Redéployez** (push un changement sur GitHub)
3. **Vérifiez les logs** : doit afficher `/data/lebonmot_simple.db`
4. **Testez** : passez une commande, faites un redéploiement, vérifiez que la commande est toujours là

**C'est tout !** 🎉

