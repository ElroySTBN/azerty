# 🔧 Guide de résolution des problèmes de connexion Supabase

## Problème : Timeout de connexion à Supabase

Si vous voyez ces erreurs dans les logs Railway :
```
❌ Erreur connexion Supabase (réseau/timeout): timeout expired
⚠️ Fallback vers SQLite - connexion Supabase échouée
```

## ✅ Solution : Utiliser l'URL de connexion DIRECTE

### Étape 1 : Récupérer l'URL de connexion directe depuis Supabase

1. Allez sur [Supabase Dashboard](https://app.supabase.com)
2. Sélectionnez votre projet
3. Allez dans **Project Settings** → **Database**
4. Dans la section **Connection string**, vous verrez plusieurs options :
   - ❌ **Transaction mode (pooler)** - Port 6543 - Peut timeout
   - ✅ **Session mode (direct)** - Port 5432 - Recommandé
   - ❌ **URI** - Peut contenir le pooler

5. **Copiez l'URL "Session mode"** (port 5432)
   - Format : `postgresql://postgres:[PASSWORD]@db.xxxxx.supabase.co:5432/postgres`
   - ⚠️ **NE PAS utiliser** l'URL avec `pooler.supabase.com` ou port `6543`

### Étape 2 : Mettre à jour la variable d'environnement sur Railway

1. Allez sur [Railway Dashboard](https://railway.app)
2. Sélectionnez votre projet
3. Allez dans **Variables**
4. Trouvez `SUPABASE_URL`
5. Remplacez l'URL par celle de connexion **DIRECTE** (port 5432)
6. **Redéployez** l'application

### Exemple de configuration correcte

**❌ MAUVAISE (pooler - peut timeout) :**
```
SUPABASE_URL=postgresql://postgres:password@aws-1-eu-west-3.pooler.supabase.com:6543/postgres
```

**✅ BONNE (direct - recommandé) :**
```
SUPABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres
```

## 🔍 Vérification

Après avoir mis à jour l'URL, vérifiez les logs Railway. Vous devriez voir :
```
✅ Connexion Supabase réussie et testée
```

Au lieu de :
```
❌ Timeout connexion Supabase
⚠️ Fallback vers SQLite
```

## 📊 Vérifier que vos données sont dans Supabase

1. Allez sur Supabase Dashboard
2. **Table Editor**
3. Ouvrez la table `conversations`
4. Si vous voyez des lignes, **vos données sont là** ! ✅
5. Une fois la connexion rétablie, elles apparaîtront dans votre dashboard

## 🚨 Si le problème persiste

1. **Vérifiez que psycopg2-binary est installé** :
   - Il est déjà dans `requirements.txt`
   - Railway l'installera automatiquement

2. **Vérifiez les logs Railway** pour voir les erreurs exactes

3. **Testez la connexion localement** :
   ```bash
   python3 test_supabase_connection.py
   ```

4. **Contactez le support Supabase** si le problème persiste (peut être un problème de réseau/firewall)

