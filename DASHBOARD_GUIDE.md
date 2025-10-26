# 📊 Guide du Dashboard Admin - Le Bon Mot

## 🚀 Accès

- **URL**: http://localhost:8081
- **Username**: admin
- **Password**: admin123

---

## ✨ Nouvelles Fonctionnalités

### 1. 📋 Tableau des Commandes Enrichi

Le tableau principal affiche maintenant :
- **Client Anonyme** : ID anonyme du client (ex: C-A1B2)
- **Telegram** : 
  - ID Telegram du client
  - Username Telegram (@username) si disponible
- **Preuve de paiement** : Lien direct "📸 Preuve" si le client a envoyé une capture d'écran

### 2. 💬 Messages Support

#### Page principale (Dashboard)
- Affiche les **10 derniers messages** support
- Voir qui a envoyé le message (Client ou Admin)
- Bouton **"Voir tout"** pour accéder à la page complète

#### Page Messages (/messages)
- Liste **toutes les conversations** groupées par client
- Pour chaque client :
  - ID anonyme
  - Username Telegram
  - Nombre de messages échangés
  - Date du dernier message
  - Aperçu du dernier message

#### Page Conversation (/messages/<client_id>)
- Historique complet des échanges avec un client
- Messages organisés chronologiquement
- Distinction visuelle :
  - 👤 Messages du client (bordure bleue)
  - 👨‍💼 Messages de l'admin (bordure verte)
- **Formulaire de réponse** en bas de page
- Les réponses sont envoyées automatiquement sur Telegram au client avec le format :
  ```
  ━━━━━━━━━━━━━━━━━━
  💬 SUPPORT
  ━━━━━━━━━━━━━━━━━━
  
  [Votre message]
  ```

### 3. 📸 Preuves de Paiement

#### Accès
- Depuis le tableau des commandes : cliquez sur **"📸 Preuve"** dans la colonne Statut
- Ou depuis les détails d'une commande : bouton **"Voir la preuve de paiement"**

#### Affichage
- Informations de la commande (ID, client, montant, date)
- Image de la preuve en grand format
- Bouton pour ouvrir en taille réelle dans un nouvel onglet

---

## 🔄 Workflow complet

### Quand un client contacte le support :

1. **Le client envoie un message** depuis le bot Telegram
   - Option : "💬 Contacter le support"
   - Peut joindre une capture d'écran

2. **Notification dashboard**
   - Le message apparaît dans la section "Messages Support"
   - Badge "Client" pour identifier l'expéditeur

3. **Réponse de l'admin**
   - Cliquez sur **"Répondre"**
   - Accédez à la conversation complète
   - Tapez votre réponse et envoyez

4. **Le client reçoit la réponse**
   - Message formaté avec header "💬 SUPPORT"
   - Reçu instantanément sur Telegram

### Quand un client envoie une preuve de paiement :

1. **Le client finalise sa commande**
   - Reçoit l'adresse Bitcoin et les instructions
   - Bouton "📸 Envoyer la preuve de paiement"

2. **Le client envoie une photo**
   - La photo est automatiquement sauvegardée dans `/uploads/`
   - Lien enregistré dans la base de données

3. **Consultation par l'admin**
   - Sur le dashboard, un lien "📸 Preuve" apparaît
   - Cliquez pour voir l'image en grand
   - Validez le paiement manuellement

---

## 📂 Structure des données

### Uploads
- Les preuves de paiement sont stockées dans : `/uploads/payment_[order_id]_[timestamp].jpg`

### Base de données
- **Table `support_messages`** :
  - `client_id` : ID anonyme du client
  - `message` : Contenu du message
  - `sender_type` : 'client' ou 'admin'
  - `telegram_username` : Username Telegram du client
  - `created_at` : Horodatage

- **Table `orders`** :
  - Colonne `payment_proof` : Chemin vers l'image de preuve

- **Table `clients`** :
  - Colonne `telegram_username` : Username Telegram

---

## 🧪 Test rapide

1. **Tester les messages support** :
   - Ouvrez Telegram et parlez au bot
   - Cliquez sur "💬 Contacter le support"
   - Envoyez un message
   - Vérifiez qu'il apparaît sur le dashboard
   - Répondez depuis le dashboard
   - Vérifiez la réception sur Telegram

2. **Tester les preuves de paiement** :
   - Créez une commande complète sur le bot
   - Finalisez jusqu'à l'étape de paiement
   - Envoyez une capture d'écran
   - Vérifiez qu'elle apparaît sur le dashboard

3. **Vérifier les infos Telegram** :
   - Créez une commande
   - Sur le dashboard, vérifiez que votre ID et username Telegram s'affichent

---

## 🐛 Dépannage

### Le bot ne répond pas
```bash
cd /Users/elroysitbon/-hh
killall -9 Python
python3 reset_bot.py
python3 main.py
```

### Le dashboard ne charge pas
- Vérifiez que le port 8081 n'est pas utilisé
- Relancez avec `python3 main.py`

### Les messages ne s'envoient pas
- Vérifiez que le bot est démarré
- Vérifiez que le client a bien un `telegram_id` dans la base

---

## 🎯 Prochaines étapes suggérées

1. **Gestion de statut de commande**
   - Ajouter la possibilité de changer le statut depuis le dashboard
   - Notifier le client automatiquement

2. **Statistiques enrichies**
   - Nombre de messages support non résolus
   - Nombre de preuves de paiement en attente

3. **Recherche et filtres**
   - Rechercher un client par ID ou username
   - Filtrer les commandes par statut, date, montant

4. **Notifications temps réel**
   - Alerte sonore ou visuelle pour nouveaux messages
   - Badge de notification

