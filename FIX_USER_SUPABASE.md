# 🔧 Fix : Erreur "Tenant or user not found" - Supabase

## 🚨 Problème Identifié

L'erreur dans vos logs :
```
FATAL: Tenant or user not found
```

**Cause** : Le nom d'utilisateur dans l'URL Supabase n'est pas au bon format pour le connection pooling.

---

## ✅ Solution : Format Correct du Nom d'Utilisateur

### Pour Connection Pooling (Port 6543)

Le nom d'utilisateur doit être au format : `postgres.PROJECT_ID` (avec un point)

**❌ FAUX** :
```
postgresql://postgres:RmqvB2QzLt3CijtH@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

**✅ CORRECT** :
```
postgresql://postgres.pxncsdvqvpxtcuhfcvkf:RmqvB2QzLt3CijtH@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

**⚠️ Important** : `postgres.pxncsdvqvpxtcuhfcvkf` (avec le point après `postgres`)

---

## 🔧 Étape par Étape : Corriger l'URL

### Étape 1 : Construire l'URL Correcte

**Format complet** :
```
postgresql://postgres.PROJECT_ID:MOT_DE_PASSE@REGION.pooler.supabase.com:6543/postgres
```

**Avec vos valeurs** :
- `PROJECT_ID` = `pxncsdvqvpxtcuhfcvkf`
- `MOT_DE_PASSE` = `RmqvB2QzLt3CijtH`
- `REGION` = `aws-0-eu-central-1` (ou votre région)

**URL complète** :
```
postgresql://postgres.pxncsdvqvpxtcuhfcvkf:RmqvB2QzLt3CijtH@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

### Étape 2 : Vérifier la Région

1. Allez sur **Supabase** → Votre projet → **Settings** → **Database**
2. Cherchez **"Region"** ou **"Location"**
3. Si ce n'est pas `eu-central-1`, ajustez l'URL :
   - `eu-central-1` → `aws-0-eu-central-1.pooler.supabase.com`
   - `us-east-1` → `aws-0-us-east-1.pooler.supabase.com`
   - `ap-southeast-1` → `aws-0-ap-southeast-1.pooler.supabase.com`
   - etc.

### Étape 3 : Mettre à Jour sur Railway

1. **Railway** → Votre service → **Variables**
2. Trouvez `SUPABASE_URL`
3. **Remplacez par l'URL complète** avec le bon format :
   ```
   postgresql://postgres.pxncsdvqvpxtcuhfcvkf:RmqvB2QzLt3CijtH@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
   ```
4. **Sauvegardez**

### Étape 4 : Vérifier

Railway va redéployer automatiquement. Après 2-3 minutes, regardez les logs :

**✅ Si ça marche** :
```
🔗 Utilisation de Supabase Connection Pooling (plus fiable)
✅ Connexion Supabase réussie
📁 Base de données : Supabase (PostgreSQL)
```

**❌ Si ça ne marche toujours pas** :
Vérifiez que :
- Le nom d'utilisateur est `postgres.pxncsdvqvpxtcuhfcvkf` (avec le point)
- Le mot de passe est correct
- La région correspond à votre projet Supabase

---

## 📋 Récapitulatif : Format Correct

| Élément | Format | Exemple |
|---------|--------|---------|
| **Protocole** | `postgresql://` | `postgresql://` |
| **Utilisateur** | `postgres.PROJECT_ID` | `postgres.pxncsdvqvpxtcuhfcvkf` |
| **Mot de passe** | Votre mot de passe | `RmqvB2QzLt3CijtH` |
| **Host** | `REGION.pooler.supabase.com` | `aws-0-eu-central-1.pooler.supabase.com` |
| **Port** | `6543` | `6543` |
| **Database** | `postgres` | `postgres` |

---

## 🆘 Si Ça Ne Marche Toujours Pas

### Vérifier dans Supabase

1. **Supabase** → Settings → Database
2. Cherchez la section **"Connection pooling"**
3. Utilisez **exactement** l'URL fournie par Supabase (avec port 6543)
4. Remplacez seulement `[YOUR-PASSWORD]` par votre mot de passe

### Alternative : Variables Séparées

Si l'URL ne marche pas, utilisez les variables séparées sur Railway :

- **SUPABASE_DB_HOST** = `aws-0-eu-central-1.pooler.supabase.com`
- **SUPABASE_DB_PORT** = `6543`
- **SUPABASE_DB_NAME** = `postgres`
- **SUPABASE_DB_USER** = `postgres.pxncsdvqvpxtcuhfcvkf` (avec le point !)
- **SUPABASE_DB_PASSWORD** = `RmqvB2QzLt3CijtH`

---

## ✅ Une Fois Corrigé

Après avoir mis à jour l'URL avec le bon format de nom d'utilisateur :

1. **Attendez le redéploiement** Railway (2-3 minutes)
2. **Vérifiez les logs** : Devrait afficher "✅ Connexion Supabase réussie"
3. **Testez le bot** : Passez une commande
4. **Vérifiez Supabase** : Table Editor → La commande devrait apparaître

**Vos données seront maintenant stockées dans Supabase !** 🎉

