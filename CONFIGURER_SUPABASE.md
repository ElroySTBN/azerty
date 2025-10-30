# 🗄️ Configuration Supabase - Reputalys

Ce guide vous explique comment configurer Supabase (PostgreSQL hébergé) pour stocker vos données de manière permanente.

---

## 🎯 Avantages de Supabase

✅ **Persistance garantie** : Vos données ne se perdent jamais  
✅ **Hébergé dans le cloud** : Pas de gestion de serveur  
✅ **Scalable** : Supporte des millions de conversations  
✅ **Backup automatique** : Vos données sont sauvegardées automatiquement  
✅ **Gratuit jusqu'à 500MB** : Parfait pour commencer  

---

## 📋 Étape 1 : Créer un projet Supabase

1. **Allez sur** https://supabase.com

2. **Créez un compte** (ou connectez-vous si vous en avez déjà un)

3. **Créez un nouveau projet** :
   - Cliquez sur "New Project"
   - Choisissez une organisation (ou créez-en une)
   - Donnez un nom à votre projet (ex: `reputalys`)
   - Choisissez un mot de passe fort pour la base de données
   - Sélectionnez une région proche (ex: `West Europe` pour la France)
   - Cliquez sur "Create new project"

4. **Attendez que le projet soit créé** (environ 2 minutes)

---

## 🔑 Étape 2 : Récupérer les identifiants de connexion

Une fois le projet créé :

1. **Allez dans "Settings"** → **"Database"**

2. **Trouvez la section "Connection string"**

3. **Vous avez deux options** :

### Option A : URL complète (plus simple)

Dans la section "Connection string", vous verrez quelque chose comme :
```
postgresql://postgres.xxxxx:VOTRE_MOT_DE_PASSE@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

**⚠️ Important** : Remplacez `[YOUR-PASSWORD]` par le mot de passe que vous avez créé lors de la création du projet.

Copiez cette URL complète.

### Option B : Variables séparées (plus sécurisé)

Si vous préférez séparer les informations :

- **Host** : `db.xxxxx.supabase.co` (trouvable dans "Connection pooling")
- **Port** : `5432`
- **Database** : `postgres`
- **User** : `postgres`
- **Password** : Le mot de passe que vous avez créé

---

## 💻 Étape 3 : Configurer localement (`.env`)

Ajoutez l'une des deux configurations suivantes dans votre fichier `.env` :

### Configuration avec URL complète :

```env
SUPABASE_URL=postgresql://postgres.xxxxx:VOTRE_MOT_DE_PASSE@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
CLIENT_BOT_TOKEN=votre_token_telegram
ADMIN_PASSWORD=votre_mot_de_passe
```

### OU Configuration avec variables séparées :

```env
SUPABASE_DB_HOST=db.xxxxx.supabase.co
SUPABASE_DB_PORT=5432
SUPABASE_DB_NAME=postgres
SUPABASE_DB_USER=postgres
SUPABASE_DB_PASSWORD=votre_mot_de_passe
CLIENT_BOT_TOKEN=votre_token_telegram
ADMIN_PASSWORD=votre_mot_de_passe
```

**⚠️ Important** : 
- Ne partagez jamais ces informations publiquement
- Le fichier `.env` est automatiquement ignoré par Git (sécurité)

---

## ☁️ Étape 4 : Configurer sur Railway

1. **Allez sur** https://railway.app

2. **Sélectionnez votre projet** Reputalys

3. **Allez dans "Variables"** (ou "Environment Variables")

4. **Ajoutez les variables Supabase** :

   Si vous utilisez l'URL complète :
   - **Nom** : `SUPABASE_URL`
   - **Valeur** : `postgresql://postgres.xxxxx:VOTRE_MOT_DE_PASSE@aws-0-eu-central-1.pooler.supabase.com:6543/postgres`

   OU si vous utilisez les variables séparées :
   - `SUPABASE_DB_HOST` = `db.xxxxx.supabase.co`
   - `SUPABASE_DB_PORT` = `5432`
   - `SUPABASE_DB_NAME` = `postgres`
   - `SUPABASE_DB_USER` = `postgres`
   - `SUPABASE_DB_PASSWORD` = `votre_mot_de_passe`

5. **Sauvegardez** - Railway va redéployer automatiquement

---

## ✅ Étape 5 : Vérifier que ça fonctionne

1. **Attendez que Railway redéploie** (quelques minutes)

2. **Vérifiez les logs Railway** - Vous devriez voir :
   ```
   ✅ Supabase (PostgreSQL) détecté
   📁 Base de données : Supabase (PostgreSQL)
   ✅ Base de données simple initialisée
   ```

3. **Testez votre bot** :
   - Envoyez `/start` sur Telegram
   - Passez une commande complète
   - Vérifiez que les données apparaissent dans le dashboard admin

4. **Vérifiez sur Supabase** :
   - Allez dans votre projet Supabase
   - Cliquez sur "Table Editor"
   - Vous devriez voir les tables `conversations` et `messages` avec vos données

---

## 🔄 Migration depuis SQLite (optionnel)

Si vous avez déjà des données dans SQLite et voulez les migrer vers Supabase, contactez-moi et je pourrai créer un script de migration.

---

## 🆘 Dépannage

### Erreur "Variables Supabase manquantes"

**Solution** : Vérifiez que vous avez bien ajouté soit `SUPABASE_URL` soit toutes les variables `SUPABASE_DB_*` dans Railway.

### Erreur "Connection refused"

**Solution** : 
- Vérifiez que votre mot de passe est correct
- Vérifiez que l'URL/host est correct
- Vérifiez que le projet Supabase est bien actif

### Erreur "psycopg2-binary non installé"

**Solution** : Cela ne devrait pas arriver car `psycopg2-binary` est maintenant dans `requirements.txt`. Si ça arrive, vérifiez que Railway a bien installé toutes les dépendances.

---

## 💡 Notes importantes

- **Sécurité** : Ne partagez jamais vos identifiants Supabase publiquement
- **Backup** : Supabase fait des backups automatiques, mais vous pouvez aussi exporter vos données manuellement
- **Limite gratuite** : 500MB de stockage gratuit, largement suffisant pour des milliers de conversations
- **Fallback SQLite** : Si `SUPABASE_URL` n'est pas défini, le bot utilisera automatiquement SQLite (comportement actuel)

---

**✅ Une fois configuré, toutes vos données seront stockées de manière permanente sur Supabase !**

