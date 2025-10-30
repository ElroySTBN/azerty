# 📋 GUIDE ÉTAPE PAR ÉTAPE : Configurer le Volume Persistant sur Railway

## 🎯 Objectif

Faire en sorte que votre base de données **survive aux redéploiements** sur Railway.

---

## 🚀 Instructions Précis (Étape par Étape)

### ÉTAPE 1 : Ouvrir Railway

1. Allez sur **https://railway.app**
2. **Connectez-vous** avec votre compte
3. **Cliquez sur votre projet** (probablement nommé comme votre repo GitHub)

---

### ÉTAPE 2 : Trouver Votre Service

1. Dans votre projet Railway, vous verrez une liste de **services**
2. **Cliquez sur le service** qui contient votre bot (probablement le seul service, ou celui qui a été créé lors du déploiement depuis GitHub)
3. Le service s'ouvre et vous voyez plusieurs onglets en haut :
   - **Deployments**
   - **Metrics**
   - **Logs**
   - **Settings**
   - **Variables**

---

### ÉTAPE 3 : Configurer le Volume Persistant

1. **Cliquez sur l'onglet "Settings"** (ou **"Variables"** selon la version de Railway)
2. **Faites défiler vers le bas** jusqu'à la section **"Volumes"** ou **"Persistent Storage"**
   - Si vous ne voyez pas cette section, cherchez un bouton **"+ Add Volume"** ou **"Mount Volume"** ou **"Persistent Storage"**
3. **Cliquez sur "+ Add Volume"** ou **"New Volume"** ou **"Mount Volume"**
4. **Configurez le volume :**
   - **Mount Path** : `/data`
   - **Size** : `1 GB` (ou `1024 MB`)
   - **Name** : `database-storage` (ou n'importe quel nom)
5. **Cliquez sur "Create"** ou **"Add"** ou **"Save"**

---

### ÉTAPE 4 : Vérifier que ça Marche

1. **Attendez 1-2 minutes** que Railway configure le volume
2. **Cliquez sur l'onglet "Logs"**
3. **Cherchez cette ligne** dans les logs :
   ```
   ✅ Railway détecté : utilisation de /data/lebonmot_simple.db (volume persistant)
   📁 Base de données : /data/lebonmot_simple.db
   ```

   **Si vous voyez** `./lebonmot_simple.db` au lieu de `/data/lebonmot_simple.db` :
   - ❌ Le volume n'est pas monté correctement
   - ✅ **Revenez à l'ÉTAPE 3** et vérifiez que le volume est bien configuré

---

### ÉTAPE 5 : Tester la Persistance

1. **Passez une commande complète** via votre bot Telegram
2. **Vérifiez dans le bot** : "Mes commandes" → La commande doit apparaître
3. **Faites un petit changement de code** (par exemple, ajoutez un commentaire dans `main.py`)
4. **Git push** → Railway redéploie automatiquement
5. **Attendez que le redéploiement soit terminé** (2-3 minutes)
6. **Vérifiez à nouveau** : "Mes commandes" dans le bot
7. **✅ La commande doit toujours être là !**

---

## 🗺️ Où se Trouve "Volumes" dans Railway ?

### Option A : Dans l'Onglet "Settings"

1. Service → **"Settings"** (icône ⚙️)
2. Faites défiler → Section **"Volumes"** ou **"Persistent Storage"**
3. Bouton **"+ Add Volume"**

### Option B : Dans le Menu Latéral

1. Service → Menu latéral gauche
2. Cherchez **"Volumes"** ou **"Storage"**
3. Bouton **"+ New Volume"**

### Option C : Dans "Variables" avec un Sous-Menu

1. Service → **"Variables"**
2. Cherchez un bouton **"Storage"** ou **"Volumes"** en haut
3. Bouton **"+ Mount Volume"**

---

## ❓ Si Vous Ne Trouvez Pas "Volumes"

### Solution Alternative 1 : Via Railway CLI

Si l'interface ne fonctionne pas, vous pouvez utiliser Railway CLI :

```bash
railway volume create /data --size 1GB
```

### Solution Alternative 2 : Contacter le Support Railway

Si vous ne trouvez vraiment pas l'option :
1. Cliquez sur **"Help"** ou **"Support"** dans Railway
2. Demandez : "How do I mount a persistent volume at /data?"
3. Ils vous guideront directement dans l'interface

---

## ✅ Checklist de Vérification

- [ ] Volume créé dans Railway avec le path `/data`
- [ ] Taille du volume : au moins 1 GB
- [ ] Volume attaché à votre service
- [ ] Logs Railway affichent : `/data/lebonmot_simple.db`
- [ ] Test : commande persiste après redéploiement

---

## 🆘 En Cas de Problème

### Les Logs Affichent `./lebonmot_simple.db` au lieu de `/data/lebonmot_simple.db`

**Problème** : Le volume n'est pas monté

**Solution** :
1. Vérifiez que le volume existe dans Settings → Volumes
2. Vérifiez que le volume est attaché à votre service
3. Redéployez manuellement (Settings → Redeploy)

### Le Volume Existe Mais les Données se Perdent Quand Même

**Problème** : Le volume n'est pas au bon endroit ou pas attaché

**Solution** :
1. Vérifiez le Mount Path : doit être **exactement** `/data` (pas `/data/` ou autre)
2. Vérifiez que le volume est attaché au bon service
3. Regardez les logs pour confirmer le chemin DB utilisé

---

## 📞 Besoin d'Aide ?

Si vous ne trouvez toujours pas où configurer le volume :
1. Faites une **capture d'écran** de votre interface Railway (onglet Settings)
2. Envoyez-la-moi et je vous guiderai précisément

---

## ✅ Une Fois Configuré

Une fois le volume configuré, **vous n'aurez plus jamais à le refaire**. Toutes vos données seront persistantes ! 🎉

