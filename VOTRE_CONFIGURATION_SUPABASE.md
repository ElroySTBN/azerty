# 🔐 Votre Configuration Supabase - Reputalys

## ✅ Informations de votre projet

- **Project ID** : `pxncsdvqvpxtcuhfcvkf`
- **Project URL** : `https://pxncsdvqvpxtcuhfcvkf.supabase.co`
- **Database Host** : `db.pxncsdvqvpxtcuhfcvkf.supabase.co`

---

## 🔑 URL de connexion complète

Construisez votre URL de connexion avec cette formule :

### Format 1 : Direct connection (Port 5432)

```
postgresql://postgres:[VOTRE_MOT_DE_PASSE]@db.pxncsdvqvpxtcuhfcvkf.supabase.co:5432/postgres
```

**Remplacez `[VOTRE_MOT_DE_PASSE]` par le mot de passe que vous avez créé lors de la création du projet Supabase.**

### Format 2 : Connection pooling (Port 6543) - Recommandé

```
postgresql://postgres.pxncsdvqvpxtcuhfcvkf:[VOTRE_MOT_DE_PASSE]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

---

## 📋 Exemple concret

Si votre mot de passe est `MonMotDePasse123`, votre URL sera :

```
postgresql://postgres:MonMotDePasse123@db.pxncsdvqvpxtcuhfcvkf.supabase.co:5432/postgres
```

⚠️ **Important** : 
- Remplacez `MonMotDePasse123` par VOTRE vrai mot de passe
- Si votre mot de passe contient des caractères spéciaux (`@`, `:`, `/`, `#`, etc.), il faudra peut-être l'encoder dans l'URL

---

## ☁️ Configuration sur Railway

### Option A : URL complète (plus simple)

1. Allez sur **https://railway.app**
2. Sélectionnez votre projet **Reputalys**
3. Allez dans **"Variables"** → **"New Variable"**
4. Ajoutez :
   - **Name** : `SUPABASE_URL`
   - **Value** : L'URL complète que vous avez construite ci-dessus
5. **Save**

### Option B : Variables séparées (plus sécurisé)

Si vous préférez, ajoutez ces variables séparément :

- **SUPABASE_DB_HOST** = `db.pxncsdvqvpxtcuhfcvkf.supabase.co`
- **SUPABASE_DB_PORT** = `5432`
- **SUPABASE_DB_NAME** = `postgres`
- **SUPABASE_DB_USER** = `postgres`
- **SUPABASE_DB_PASSWORD** = `votre_mot_de_passe`

---

## ✅ Vérification

Une fois configuré sur Railway :

1. Attendez que Railway redéploie (2-3 minutes)
2. Vérifiez les logs Railway - vous devriez voir :
   ```
   ✅ Supabase (PostgreSQL) détecté
   📁 Base de données : Supabase (PostgreSQL)
   ✅ Base de données simple initialisée
   ```

3. Testez votre bot sur Telegram - tout devrait fonctionner normalement !

---

## 🆘 Si votre mot de passe contient des caractères spéciaux

Si votre mot de passe contient `@`, `:`, `/`, `#`, `%`, etc., il faut l'encoder dans l'URL.

**Dites-moi quel caractère spécial vous avez, et je vous donnerai l'URL encodée !**

Ou utilisez les **variables séparées** (Option B) - c'est plus simple et évite les problèmes d'encodage.

---

**✅ Une fois que vous avez ajouté `SUPABASE_URL` sur Railway, vos données seront stockées de manière permanente !**

