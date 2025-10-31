# 🔍 Déboguer l'URL Supabase - Guide Complet

## 🚨 Erreur "Tenant or user not found"

Cette erreur signifie que **le nom d'utilisateur ou le PROJECT_ID est incorrect** dans votre URL Supabase.

---

## ✅ Solution : Vérifier l'URL Exacte depuis Supabase

### Méthode 1 : Via Connection String (Recommandé)

1. **Allez sur Supabase** → Votre projet (`pxncsdvqvpxtcuhfcvkf`)
2. **Settings** (en bas du menu) → **Database**
3. **Cherchez la section "Connection string"**
4. **Cliquez sur l'onglet "URI"** (pas "JDBC" ou autre)
5. **Vous devriez voir** :
   ```
   postgresql://postgres.[PROJECT_ID]:[YOUR-PASSWORD]@aws-0-eu-west-3.pooler.supabase.com:6543/postgres
   ```
6. **Copiez cette URL complète**
7. **Remplacez `[YOUR-PASSWORD]`** par votre mot de passe réel (`RmqvB2QzLt3CijtH`)
8. **Utilisez cette URL exacte** sur Railway

### Méthode 2 : Vérifier le PROJECT_ID

1. **Supabase** → Votre projet
2. **Settings** → **General**
3. **Regardez "Reference ID"** ou **"Project ID"**
4. **Notez ce PROJECT_ID** (devrait être `pxncsdvqvpxtcuhfcvkf`)

### Méthode 3 : Connection Pooling Directement

1. **Supabase** → Settings → **Database**
2. **Cherchez "Connection pooling"**
3. **Vous devriez voir** :
   - **Host** : `aws-0-eu-west-3.pooler.supabase.com`
   - **Port** : `6543`
   - **User** : `postgres.pxncsdvqvpxtcuhfcvkf` (avec le point !)
   - **Password** : Votre mot de passe
   - **Database** : `postgres`

---

## 🔍 Vérification : Format Correct de l'URL

**Format attendu** :
```
postgresql://postgres.PROJECT_ID:MOT_DE_PASSE@REGION.pooler.supabase.com:6543/postgres
```

**Exemple avec vos valeurs** :
```
postgresql://postgres.pxncsdvqvpxtcuhfcvkf:RmqvB2QzLt3CijtH@aws-0-eu-west-3.pooler.supabase.com:6543/postgres
```

### ✅ Points à Vérifier :

1. **Nom d'utilisateur** : `postgres.pxncsdvqvpxtcuhfcvkf`
   - ✅ Commence par `postgres.` (avec le point)
   - ✅ Suivi du PROJECT_ID (`pxncsdvqvpxtcuhfcvkf`)
   - ❌ PAS juste `postgres`

2. **Mot de passe** : `RmqvB2QzLt3CijtH`
   - ✅ Correct (pas de caractères spéciaux problématiques)

3. **Host** : `aws-0-eu-west-3.pooler.supabase.com`
   - ✅ Région `eu-west-3`
   - ✅ Contient `pooler.supabase.com`

4. **Port** : `6543`
   - ✅ Connection pooling

5. **Database** : `postgres`
   - ✅ Standard

---

## 🆘 Si l'Erreur Persiste

### Vérification 1 : PROJECT_ID Correct

1. **Supabase** → Settings → **General**
2. **Vérifiez le "Reference ID"**
3. **Comparez avec celui dans votre URL** :
   - URL : `postgres.pxncsdvqvpxtcuhfcvkf`
   - Supabase : `pxncsdvqvpxtcuhfcvkf`
   - ✅ Doivent être identiques

### Vérification 2 : Mot de Passe Correct

1. **Vérifiez que le mot de passe dans l'URL** correspond au mot de passe de votre projet Supabase
2. **Pas d'espaces** avant/après
3. **Pas de caractères encodés** (comme `%40` pour `@`)

### Vérification 3 : Région Correcte

1. **Supabase** → Settings → **Database**
2. **Vérifiez la région** affichée
3. **Comparez avec l'URL** :
   - Si région = `eu-west-3` → URL doit avoir `aws-0-eu-west-3`
   - Si région = `us-east-1` → URL doit avoir `aws-0-us-east-1`
   - etc.

---

## 💡 Solution Alternative : Variables Séparées

Si l'URL complète ne fonctionne pas, utilisez les variables séparées sur Railway :

1. **Railway** → Service → **Variables**
2. **Ajoutez ces variables** (supprimez `SUPABASE_URL` si elle existe) :

   - **SUPABASE_DB_HOST** = `aws-0-eu-west-3.pooler.supabase.com`
   - **SUPABASE_DB_PORT** = `6543`
   - **SUPABASE_DB_NAME** = `postgres`
   - **SUPABASE_DB_USER** = `postgres.pxncsdvqvpxtcuhfcvkf` (avec le point !)
   - **SUPABASE_DB_PASSWORD** = `RmqvB2QzLt3CijtH`

3. **Sauvegardez**

---

## 📋 Checklist de Vérification

- [ ] **URL contient** `postgres.pxncsdvqvpxtcuhfcvkf` (avec le point)
- [ ] **PROJECT_ID correct** : Vérifié dans Supabase Settings → General
- [ ] **Mot de passe correct** : Correspond au mot de passe Supabase
- [ ] **Région correcte** : `eu-west-3` dans l'URL
- [ ] **Port correct** : `6543` (connection pooling)
- [ ] **Host correct** : `pooler.supabase.com` (pas `db.xxx.supabase.co`)

---

## 🔍 Pour Trouver l'URL Exacte dans Supabase

### Option A : Connection String URI

1. Supabase → Settings → Database
2. Section **"Connection string"**
3. Onglet **"URI"**
4. **Copiez l'URL** et remplacez `[YOUR-PASSWORD]`

### Option B : Connection Pooling

1. Supabase → Settings → Database
2. Section **"Connection pooling"**
3. **Copiez les infos** et construisez l'URL manuellement

### Option C : SQL Editor (Voir les infos)

1. Supabase → **SQL Editor**
2. **New Query**
3. Les informations de connexion sont parfois affichées en bas

---

## ✅ Une Fois l'URL Vérifiée

1. **Mettez l'URL exacte** sur Railway
2. **Attendez le redéploiement** (2-3 minutes)
3. **Vérifiez les logs** : Devrait afficher "✅ Connexion Supabase réussie"

**Si l'erreur persiste** → Le PROJECT_ID ou le mot de passe est probablement incorrect. Vérifiez dans Supabase Settings.

