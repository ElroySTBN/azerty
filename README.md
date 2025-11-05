# 🔐 Reputalys - Bot Telegram Simple

Service anonyme de e-réputation - Bot Telegram + Dashboard Admin

---

## 🚀 Démarrage Rapide

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Créez un fichier `.env` avec :

```env
CLIENT_BOT_TOKEN=votre_token_telegram
ADMIN_PASSWORD=votre_mot_de_passe

# Optionnel : Supabase (PostgreSQL)
# Si non configuré, utilise SQLite localement
SUPABASE_URL=votre_url_supabase
SUPABASE_DB_HOST=votre_host
SUPABASE_DB_NAME=votre_db_name
SUPABASE_DB_USER=votre_user
SUPABASE_DB_PASSWORD=votre_password
SUPABASE_DB_PORT=5432

# Optionnel : Notifications admin Telegram
# Pour recevoir des notifications sur votre compte Telegram
ADMIN_TELEGRAM_ID=votre_telegram_id
```

### Lancer

```bash
python main.py
```

Dashboard : `http://localhost:8081`

---

## 📦 Déploiement Railway

1. Créez un nouveau projet Railway
2. Connectez votre repo GitHub
3. Ajoutez les variables d'environnement :
   - `CLIENT_BOT_TOKEN` (obligatoire)
   - `ADMIN_PASSWORD` (obligatoire)
   - Variables Supabase si vous utilisez PostgreSQL (optionnel)
   - `ADMIN_TELEGRAM_ID` (optionnel, pour les notifications)
4. Railway déploie automatiquement !

## 🗄️ Configuration Base de Données

### Option 1 : SQLite (par défaut)
Par défaut, Reputalys utilise SQLite. La base de données est créée automatiquement.

### Option 2 : Supabase (PostgreSQL)
Pour utiliser Supabase :

1. **Créer la base de données** :
   - Exécutez le script `migrations/001_reputalys_schema.sql` dans Supabase SQL Editor
   - Ce script crée toutes les tables nécessaires avec RLS et permissions

2. **Nettoyer les tables inutiles** (si vous avez déjà des tables RaiseDesk) :
   - Exécutez le script `migrations/002_cleanup_raisedesk_tables.sql` dans Supabase SQL Editor
   - ⚠️ **ATTENTION** : Cette opération supprime définitivement les tables RaiseDesk

3. **Configurer les variables d'environnement** :
   ```env
   SUPABASE_URL=votre_url_supabase
   SUPABASE_DB_HOST=votre_host
   SUPABASE_DB_NAME=votre_db_name
   SUPABASE_DB_USER=votre_user
   SUPABASE_DB_PASSWORD=votre_password
   SUPABASE_DB_PORT=5432
   ```

### Tables de la base de données

Reputalys utilise 7 tables :
- `conversations` - Conversations Telegram avec les clients
- `messages` - Messages échangés
- `pricing` - Grille tarifaire configurable
- `crypto_addresses` - Adresses crypto pour paiements
- `message_templates` - Templates de messages
- `bot_messages` - Messages du bot
- `bot_buttons` - Boutons du bot

---

## 📂 Structure

```
-hh/
├── main.py                 # Point d'entrée
├── bot_simple.py           # Bot Telegram
├── dashboard_simple.py     # Dashboard admin
└── requirements.txt        # Dépendances
```

---

## 💰 Grille Tarifaire

- Avis Google : 18 EUR
- Trustpilot : 16 EUR
- Messages Forum : 5 EUR
- Pages Jaunes : 15 EUR
- Suppression liens : Sur devis

---

## 🧪 Procédure de Test

### Test 1 : Vérification de la Base de Données

1. **Vérifier les tables dans Supabase** :
   - Connectez-vous à Supabase Dashboard
   - Allez dans Table Editor
   - Vérifiez que seules les 7 tables Reputalys existent :
     - conversations
     - messages
     - pricing
     - crypto_addresses
     - message_templates
     - bot_messages
     - bot_buttons

2. **Vérifier les données par défaut** :
   - Ouvrez la table `pricing` : doit contenir les 6 services par défaut
   - Ouvrez la table `message_templates` : doit contenir 4 templates par défaut

### Test 2 : Test du Bot Telegram

1. **Démarrer le bot** :
   ```bash
   python main.py
   ```

2. **Envoyer un message au bot** :
   - Ouvrez Telegram et cherchez votre bot
   - Envoyez `/start` ou un message simple
   - Vérifiez que le bot répond

3. **Vérifier dans le dashboard** :
   - Ouvrez le dashboard : `http://localhost:8081`
   - Connectez-vous avec votre `ADMIN_PASSWORD`
   - Vérifiez que la conversation apparaît dans "Vue d'ensemble"
   - Vérifiez que le message est visible dans la conversation

4. **Vérifier dans Supabase** :
   - Ouvrez la table `conversations` : une nouvelle ligne doit apparaître
   - Ouvrez la table `messages` : le message doit être enregistré

### Test 3 : Test de Commande Complète

1. **Passer une commande via le bot** :
   - Cliquez sur "📝 Passer une commande"
   - Choisissez un service (ex: "Avis Google")
   - Entrez une quantité (ex: "5")
   - Suivez les étapes jusqu'à la confirmation

2. **Vérifier dans le dashboard** :
   - Ouvrez l'onglet "🛒 Commandes"
   - Vérifiez que la commande apparaît avec :
     - Service correct
     - Quantité correcte
     - Prix estimé correct
     - Lien (si fourni)

3. **Vérifier dans Supabase** :
   - Ouvrez la table `conversations`
   - Vérifiez que la ligne contient :
     - `service_type` : le service choisi
     - `quantity` : la quantité
     - `estimated_price` : le prix calculé

### Test 4 : Test du Dashboard

1. **Vérifier les statistiques** :
   - Les stats doivent afficher :
     - Nombre de commandes
     - Nombre de clients
     - Nombre de messages

2. **Vérifier le rafraîchissement automatique** :
   - Ouvrez le dashboard sur "Vue d'ensemble"
   - Envoyez un nouveau message au bot depuis Telegram
   - Attendez 12 secondes maximum
   - Le dashboard doit se rafraîchir automatiquement
   - Un indicateur "🔄 Mise à jour..." apparaît en haut à droite

3. **Tester l'envoi de réponse** :
   - Ouvrez une conversation depuis le dashboard
   - Cliquez sur "📝 Templates rapides" (ex: "✅ Paiement reçu")
   - Modifiez le message si besoin
   - Cliquez sur "Envoyer ➤"
   - Vérifiez que le message arrive dans Telegram

### Test 5 : Vérification Supabase Directement

1. **Vérifier l'enregistrement des données** :
   - Connectez-vous à Supabase Table Editor
   - Vérifiez chaque table :
     - `conversations` : toutes les conversations
     - `messages` : tous les messages échangés
     - `pricing` : prix modifiables depuis le dashboard
     - `crypto_addresses` : adresses crypto ajoutées

2. **Vérifier la cohérence** :
   - Les `conversation_id` dans `messages` doivent correspondre aux `id` dans `conversations`
   - Les `telegram_id` doivent être cohérents entre les tables

## 🔔 Notifications Admin (Optionnel)

Pour recevoir des notifications Telegram sur votre compte lorsque vous recevez des messages :

1. **Obtenir votre Telegram ID** :
   - Envoyez un message à `@userinfobot` sur Telegram
   - Notez votre ID

2. **Configurer** :
   ```env
   ADMIN_TELEGRAM_ID=votre_telegram_id
   ```

3. **Activer les notifications** :
   - La fonction `send_admin_notification()` est déjà préparée dans le code
   - Elle sera activée automatiquement quand vous ajouterez votre ID
   - Pour l'instant, elle est en mode préparatoire (structure prête)

## 📊 Fonctionnalités du Dashboard

- **Rafraîchissement automatique** : Le dashboard se met à jour toutes les 12 secondes pour les vues "Vue d'ensemble", "Conversations" et "Commandes"
- **Templates de messages** : Envoyez rapidement des messages préconfigurés
- **Gestion des prix** : Modifiez les prix directement depuis le dashboard
- **Adresses crypto** : Gérez vos adresses de paiement crypto
- **Recherche et filtres** : Recherchez et filtrez les commandes par service

---

**Version Simple MVP - Prêt pour Railway**

