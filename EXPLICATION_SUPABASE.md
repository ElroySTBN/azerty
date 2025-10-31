# 💡 Explication : Supabase pour Reputalys

## 🎯 Ce qu'on utilise dans Supabase

Pour Reputalys, on utilise **UNIQUEMENT** la partie **base de données PostgreSQL** de Supabase.

### ✅ Ce qu'on utilise :
- **PostgreSQL Database** : Pour stocker les conversations et messages de manière permanente
- C'est tout ! 

### ❌ Ce qu'on n'utilise PAS (et qu'on n'a pas besoin) :
- **Storage/Buckets** : Pour stocker des fichiers/images → On n'en a pas besoin car on stocke juste du texte
- **Authentication** : Pour gérer les utilisateurs → Notre bot Telegram gère déjà l'authentification
- **Real-time** : Pour les mises à jour en temps réel → Pas nécessaire pour notre cas
- **Edge Functions** : Pour exécuter du code → On utilise Railway pour ça

---

## 🔍 Pourquoi Supabase et pas juste un fichier SQLite ?

### Problème avec SQLite sur Railway :
- Les fichiers SQLite sont stockés sur le système de fichiers temporaire
- Quand Railway redémarre ou met à jour, les données peuvent être perdues
- Pas de backup automatique

### Avantage avec Supabase (PostgreSQL) :
- ✅ Stockage permanent dans le cloud
- ✅ Données jamais perdues, même si Railway redémarre
- ✅ Backup automatique
- ✅ Scalable (supporte des millions de conversations)
- ✅ Gratuit jusqu'à 500MB (largement suffisant)

---

## 📊 Ce qui est stocké dans Supabase

Notre bot stocke dans Supabase :

1. **Table `conversations`** :
   - ID, telegram_id, username
   - Type de service (Avis Google, Trustpilot, etc.)
   - Quantité, lien, détails
   - Prix estimé, statut
   - Date de création

2. **Table `messages`** :
   - Messages échangés entre le client et le bot
   - Messages du support admin
   - Liens avec les conversations

**Tout ça c'est du texte** - donc pas besoin de buckets pour stocker des fichiers !

---

## 🚀 Résumé

- **Supabase = Base de données PostgreSQL hébergée dans le cloud**
- **On utilise SEULEMENT la DB** - rien d'autre
- **Pas besoin de buckets** - on stocke juste du texte (conversations/messages)
- **Avantage principal** : Persistance garantie, plus de perte de données

C'est comme avoir une base de données MySQL/PostgreSQL hébergée, mais avec une interface simple et gratuite pour commencer ! 🎯

