# 🔍 Comment trouver l'URL de connexion Supabase

## Méthode 1 : Via Settings → Database (cherchez plus bas)

Dans Settings → Database, descendez plus bas dans la page. Il devrait y avoir une section **"Connection info"** ou **"Connection string"** après toutes les sections que vous avez listées.

**Cherchez spécifiquement :**
- Scroll vers le bas de la page Database
- Regardez s'il y a une section avec un titre comme "Connection string", "Connection info", ou "Database connection"
- Il devrait y avoir un champ avec une URL qui commence par `postgresql://`

## Méthode 2 : Via Settings → API

1. Dans le menu de gauche, allez dans **Settings** → **API** (pas Database)
2. Cherchez une section **"Project URL"** ou **"Database URL"**
3. Parfois l'URL de connexion DB est là

## Méthode 3 : Construire l'URL manuellement

Si vous ne trouvez toujours pas, on peut construire l'URL avec ces informations :

### Informations à trouver :

1. **Le host de votre projet** :
   - Allez dans **Settings** → **General** (ou **Settings** → **Project Settings**)
   - Vous devriez voir votre **Project URL** qui ressemble à : `https://xxxxx.supabase.co`
   - Le host de la DB sera : `db.xxxxx.supabase.co` (remplacez juste le début par `db.`)

2. **Le mot de passe** : Vous l'avez créé lors de la création du projet (celui mentionné dans "Database password")

3. **Les autres infos** :
   - **Port** : `5432` (port standard PostgreSQL)
   - **Database** : `postgres`
   - **User** : `postgres`

### Construire l'URL :

Avec ces infos, l'URL sera :
```
postgresql://postgres:[VOTRE_MOT_DE_PASSE]@db.xxxxx.supabase.co:5432/postgres
```

Remplacez :
- `[VOTRE_MOT_DE_PASSE]` par le mot de passe de votre DB
- `xxxxx` par votre ID de projet (trouvable dans l'URL de votre projet Supabase)

## Méthode 4 : Via Table Editor

1. Dans Supabase, allez dans **Table Editor** (menu de gauche)
2. Parfois il y a un bouton "Connect" ou "View connection info" qui montre l'URL

## ⚡ Solution rapide : Dites-moi ces informations

Si vous préférez, donnez-moi :
1. L'URL de votre projet Supabase (ex: `https://xxxxx.supabase.co`)
2. Votre mot de passe de base de données (celui que vous avez créé)

Et je vous construirai l'URL complète ! 🛠️

---

**Astuce** : Vous pouvez aussi utiliser **Connection pooling** si c'est disponible. Le port sera `6543` au lieu de `5432`, mais ça fonctionne aussi.

