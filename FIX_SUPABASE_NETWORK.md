# 🔧 Fix : Problème de connexion Supabase (Network unreachable)

## 📋 Problème identifié

D'après vos logs, Supabase ne peut pas se connecter :
```
connection to server at "db.pxncsdvqvpxtcuhfcvkf.supabase.co" (2a05:d012:42e:5700:5071:310:1f45:78a8), port 5432 failed: Network is unreachable
```

**Cause probable** : Railway bloque les connexions sortantes IPv6, ou le host Supabase n'est pas accessible depuis Railway.

---

## 🔧 Solutions

### Solution 1 : Utiliser Connection Pooling (Port 6543)

Le problème vient peut-être du port `5432`. Essayez avec le **port de connection pooling** (`6543`) :

1. Allez dans Supabase → **Settings** → **Database**
2. Cherchez la section **"Connection pooling"**
3. Utilisez l'URL avec le port **6543** au lieu de **5432**

L'URL devrait ressembler à :
```
postgresql://postgres.pxncsdvqvpxtcuhfcvkf:[VOTRE_MOT_DE_PASSE]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

**⚠️ Important** : 
- Utilisez `postgres.pxncsdvqvpxtcuhfcvkf` (avec le point) au lieu de `postgres`
- Port **6543** au lieu de **5432**
- Host `aws-0-eu-central-1.pooler.supabase.com` au lieu de `db.pxncsdvqvpxtcuhfcvkf.supabase.co`

### Solution 2 : Utiliser les variables séparées

Si l'URL complète ne marche pas, utilisez les variables séparées sur Railway :

- **SUPABASE_DB_HOST** = `aws-0-eu-central-1.pooler.supabase.com`
- **SUPABASE_DB_PORT** = `6543` (connection pooling)
- **SUPABASE_DB_NAME** = `postgres`
- **SUPABASE_DB_USER** = `postgres.pxncsdvqvpxtcuhfcvkf`
- **SUPABASE_DB_PASSWORD** = `votre_mot_de_passe`

### Solution 3 : Vérifier les Network Restrictions

Dans Supabase :
1. Allez dans **Settings** → **Database**
2. Cherchez **"Network Restrictions"**
3. Assurez-vous que **"Allow all IP addresses"** est activé (par défaut)

---

## ⚡ Solution temporaire : Continuer avec SQLite + Volume persistant

Si Supabase pose toujours problème, le bot fonctionne déjà avec SQLite + volume persistant sur Railway :

1. **Assurez-vous d'avoir un volume persistant configuré sur Railway** :
   - Allez dans votre projet Railway
   - **Settings** → **Volumes**
   - Créez un volume monté sur `/data`

2. **Le bot utilisera automatiquement** `/data/lebonmot_simple.db`

3. **Vos données seront persistantes** même après redéploiement

---

## 🎯 Recommandation

**Pour la persistance garantie**, je recommande vraiment Supabase, mais si vous avez des problèmes de réseau :

1. **Court terme** : Utilisez SQLite avec volume persistant (fonctionne déjà dans vos logs)
2. **Long terme** : Configurez Supabase avec connection pooling (port 6543) qui est plus fiable

Le bot fonctionne déjà en fallback SQLite, donc vous pouvez continuer à l'utiliser en attendant de régler Supabase ! ✅

