# 🚀 Guide Rapide : Configurer Supabase en 5 minutes

## Étape 1 : Créer un compte Supabase (2 min)

1. Allez sur **https://supabase.com**
2. Cliquez sur **"Start your project"** ou **"Sign in"**
3. Connectez-vous avec GitHub (recommandé) ou créez un compte email

## Étape 2 : Créer un projet (1 min)

1. Cliquez sur **"New Project"**
2. Remplissez :
   - **Name** : `reputalys` (ou autre nom)
   - **Database Password** : Créez un mot de passe fort (notez-le !)
   - **Region** : `West Europe` (ou la région la plus proche)
3. Cliquez sur **"Create new project"**
4. Attendez 2 minutes que le projet se crée

## Étape 3 : Récupérer l'URL de connexion (1 min)

Une fois le projet créé, plusieurs méthodes pour trouver l'URL :

### Méthode 1 : Via Settings → Database (Recommandé)

1. Dans le menu de gauche, cliquez sur **"Settings"** ⚙️ (en bas du menu)
2. Dans le menu Settings, cliquez sur **"Database"**
3. Vous verrez plusieurs sections. Cherchez :
   - **"Connection string"** OU
   - **"Connection info"** OU  
   - **"Connection pooling"**
4. Dans cette section, cherchez un onglet **"URI"** ou **"Connection string"**
5. Vous devriez voir quelque chose comme :
   ```
   postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
   ```
6. **Copiez cette URL** et **remplacez `[YOUR-PASSWORD]` par votre mot de passe**

### Méthode 2 : Via Connection Pooling (Si méthode 1 ne marche pas)

1. Dans **Settings** → **Database**
2. Cherchez la section **"Connection pooling"**
3. Vous verrez peut-être une URL qui commence par `postgresql://postgres.xxxxx`
4. Si vous voyez `[YOUR-PASSWORD]`, remplacez-le par votre mot de passe

### Méthode 3 : Récupérer les infos séparément

Si vous ne trouvez pas l'URL complète, cherchez ces informations dans Settings → Database :

- **Host** : `db.xxxxx.supabase.co` (trouvable dans "Connection info" ou "Connection pooling")
- **Port** : `5432` (ou `6543` pour connection pooling)
- **Database** : `postgres`
- **User** : `postgres`
- **Password** : Le mot de passe que vous avez créé à l'étape 2

Avec ces infos, on construira l'URL ensemble. 🛠️

### Exemple d'URL finale :

Une fois le mot de passe remplacé, ça devrait ressembler à :
```
postgresql://postgres.xxxxx:MonMotDePasse123@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
```

⚠️ **Note** : Si votre mot de passe contient des caractères spéciaux (comme `@`, `:`, `/`, `#`), il faudra peut-être l'encoder dans l'URL. Dans ce cas, dites-moi et je vous aiderai.

## Étape 4 : Ajouter sur Railway (1 min)

1. Allez sur **https://railway.app**
2. Sélectionnez votre projet **Reputalys**
3. Cliquez sur **"Variables"** (ou **"Environment Variables"**)
4. Cliquez sur **"New Variable"**
5. Remplissez :
   - **Name** : `SUPABASE_URL`
   - **Value** : Collez l'URL que vous venez de copier (avec le mot de passe remplacé)
6. Cliquez sur **"Add"** ou **"Save"**
7. Railway va **redéployer automatiquement** ⚡

## Étape 5 : Vérifier que ça marche (30 sec)

1. **Attendez 2-3 minutes** que Railway redéploie
2. **Regardez les logs Railway** - Vous devriez voir :
   ```
   ✅ Supabase (PostgreSQL) détecté
   📁 Base de données : Supabase (PostgreSQL)
   ✅ Base de données simple initialisée
   ```
3. **Testez votre bot** sur Telegram :
   - Envoyez `/start`
   - Passez une commande complète
   - Vérifiez que tout fonctionne

## ✅ C'est fait !

Vos données sont maintenant stockées de manière permanente sur Supabase. Elles ne se perdront plus jamais ! 🎉

---

## 🆘 En cas de problème

### Je ne vois pas "Connection string"
- Assurez-vous d'être dans **Settings** → **Database**
- Descendez un peu dans la page, c'est dans la section "Connection string"

### Erreur "password authentication failed"
- Vérifiez que vous avez bien remplacé `[YOUR-PASSWORD]` par votre vrai mot de passe
- Le mot de passe ne doit pas contenir de caractères spéciaux qui pourraient casser l'URL (comme `@`, `:`, `/`)

### Railway ne redéploie pas
- Cliquez manuellement sur "Redeploy" dans Railway
- Ou faites un petit changement dans le code et poussez sur GitHub

### Je vois toujours "SQLite" dans les logs
- Vérifiez que `SUPABASE_URL` est bien défini dans Railway
- Vérifiez qu'il n'y a pas d'erreur dans l'URL (espaces, caractères manquants)
- Redéployez manuellement sur Railway

---

## 💡 Astuce : Voir vos données

Une fois configuré, vous pouvez voir toutes vos données dans Supabase :

1. Allez sur votre projet Supabase
2. Cliquez sur **"Table Editor"** dans le menu de gauche
3. Vous verrez les tables `conversations` et `messages` avec toutes vos données ! 📊

---

**Besoin d'aide ? Dites-moi à quelle étape vous êtes bloqué !**

