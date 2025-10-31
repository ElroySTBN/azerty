# 🔒 Garantir la Persistance des Données - Reputalys

Ce guide vous explique comment garantir que vos données (commandes, conversations, messages) ne se perdent JAMAIS, même après un déploiement.

---

## ⚠️ Problème Actuel

Si vos données se perdent à chaque déploiement sur Railway, c'est que le **volume persistant n'est pas configuré** ou n'est pas monté correctement.

---

## ✅ Solution 1 : Volume Persistant Railway (Recommandé si vous restez sur SQLite)

### Étape 1 : Vérifier si un volume existe déjà

1. Allez sur **https://railway.app**
2. Sélectionnez votre projet **Reputalys**
3. Cliquez sur votre service (celui qui contient votre bot)
4. Allez dans l'onglet **"Volumes"** (ou **"Storage"**)

### Étape 2 : Créer un volume persistant

1. Cliquez sur **"New Volume"** ou **"+ Create Volume"**
2. Configurez :
   - **Name** : `database-storage` (ou n'importe quel nom)
   - **Mount Path** : `/data` (⚠️ EXACTEMENT `/data`, c'est important !)
   - **Size** : `1GB` (largement suffisant pour des milliers de commandes)
3. Cliquez sur **"Create"** ou **"Add"**

### Étape 3 : Vérifier que ça marche

1. Redéployez votre projet (ou attendez le prochain déploiement)
2. Dans les logs Railway, vous devriez voir :
   ```
   ✅ Railway détecté : utilisation de /data/lebonmot_simple.db (volume persistant)
   📁 Base de données : /data/lebonmot_simple.db
   ```
3. **Test** : Passez une commande via le bot, puis redéployez. La commande devrait toujours être là !

---

## ✅ Solution 2 : Supabase (Recommandé pour persistance garantie)

Supabase stocke vos données dans le cloud, donc **elles ne se perdent JAMAIS**, même si Railway redémarre ou change de serveur.

### Avantages de Supabase :
- ✅ **Persistance garantie** : données dans le cloud PostgreSQL
- ✅ **Backup automatique** : Supabase fait des backups automatiques
- ✅ **Pas de configuration de volume** : ça marche dès que la connexion est établie
- ✅ **Accessible partout** : vous pouvez voir vos données depuis Supabase directement

### Comment configurer Supabase :

Voir le guide : **`CONFIGURER_SUPABASE.md`** ou **`GUIDE_RAPIDE_SUPABASE.md`**

**⚠️ Note importante** : D'après vos logs, Supabase a un problème de connexion réseau. Voir **`FIX_SUPABASE_NETWORK.md`** pour les solutions.

---

## 🔍 Vérification : Vos données sont-elles persistantes ?

### Test simple :

1. **Passez une commande** via le bot Telegram
2. **Allez dans le dashboard** et vérifiez que la commande apparaît
3. **Redéployez votre projet** sur Railway (ou faites un petit changement et poussez sur GitHub)
4. **Après le redéploiement**, allez à nouveau dans le dashboard
5. **Vérifiez** : la commande devrait toujours être là !

Si la commande a disparu → Le volume persistant n'est pas configuré correctement.

---

## 🛠️ Diagnostic : Où sont vos données ?

### Option A : Volume persistant configuré

Si vous voyez dans les logs Railway :
```
📁 Base de données : /data/lebonmot_simple.db
```

**ET** un volume est monté sur `/data` → **✅ Vos données sont persistantes !**

### Option B : Pas de volume persistant

Si vous voyez :
```
📁 Base de données : ./lebonmot_simple.db
```

**OU** pas de volume monté sur `/data` → **❌ Vos données se perdront à chaque redéploiement !**

---

## 📋 Checklist pour garantir la persistance

- [ ] **Volume Railway créé** et monté sur `/data`
- [ ] **Logs Railway affichent** `/data/lebonmot_simple.db`
- [ ] **Test effectué** : commande passée → redéploiement → commande toujours là
- [ ] **OU** Supabase configuré et connecté (logs affichent "✅ Supabase (PostgreSQL) détecté")

---

## 🎯 Recommandation Finale

**Pour une persistance garantie à 100%** :

1. **Court terme** : Configurez le volume persistant Railway (Solution 1)
2. **Long terme** : Configurez Supabase correctement (Solution 2) - plus fiable et professionnel

**Les deux solutions fonctionnent, mais Supabase est plus robuste** car les données sont dans le cloud, pas sur un serveur Railway.

---

## 🆘 Si vos données se perdent encore

1. **Vérifiez que le volume est bien monté** : Railway → Service → Volumes → `/data` doit être listé
2. **Vérifiez les logs** : Le chemin doit être `/data/lebonmot_simple.db`, pas `./lebonmot_simple.db`
3. **Testez avec Supabase** : Si Railway pose problème, Supabase est plus fiable

---

**✅ Une fois configuré, vos données seront stockées de manière permanente et ne se perdront plus jamais !**

