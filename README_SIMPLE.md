# 🔐 Le Bon Mot - Version Simple MVP

**Service Anonyme de E-réputation**

Bot Telegram ultra-simple pour qualifier les leads et gérer les devis.

---

## 🚀 Démarrage Rapide

### En Local

1. **Installer les dépendances**
```bash
pip install python-telegram-bot[job-queue] python-dotenv flask
```

2. **Configurer le .env**
```bash
CLIENT_BOT_TOKEN=votre_token_telegram
PORT=8081
```

3. **Lancer l'application**
```bash
python3 main_simple.py
```

4. **Accéder au dashboard**
- Dashboard Admin : `http://localhost:8081`
- Mot de passe : `admin123`

---

## 📦 Déploiement sur Railway

### 1. Créer un `Procfile`

Créez un fichier nommé `Procfile` à la racine :
```
web: python3 main_simple.py
```

### 2. Créer un `runtime.txt` (optionnel)

```
python-3.11
```

### 3. Configurer Railway

1. Créez un nouveau projet sur [railway.app](https://railway.app)
2. Connectez votre repo GitHub
3. Ajoutez les variables d'environnement :
   - `CLIENT_BOT_TOKEN` : Votre token Telegram
   - `PORT` : (Railway le configure automatiquement)

### 4. Déployer

Railway déploie automatiquement à chaque `git push`.

```bash
git add .
git commit -m "Deploy Le Bon Mot MVP"
git push origin main
```

---

## 📱 Fonctionnalités

### Bot Telegram

✅ **Qualification de leads en 4 étapes**
1. Type de service (Avis Google, Trustpilot, Forum, etc.)
2. Quantité approximative
3. Lien (optionnel)
4. Détails supplémentaires (optionnel)

✅ **Calcul automatique du prix** selon la grille tarifaire :
- Avis Google : 18 EUR (6 mois non-drop)
- Trustpilot : 16 EUR (1 an non-drop)
- Messages Forum : 5 EUR/message
- Pages Jaunes : 15 EUR
- Autre plateforme : 15 EUR
- Suppression de liens : Sur devis

✅ **Support direct** : Après le devis, tous les messages vont au support

### Dashboard Admin

✅ Vue d'ensemble des conversations
✅ Détails complets de chaque demande
✅ Réponse directe aux clients via Telegram
✅ Historique des messages

---

## 🗂️ Structure des Fichiers

```
-hh/
├── main_simple.py          # Point d'entrée principal
├── bot_simple.py           # Logique du bot Telegram
├── dashboard_simple.py     # Dashboard admin Flask
├── lebonmot_simple.db      # Base de données SQLite
├── .env                    # Variables d'environnement
├── Procfile                # Pour Railway
└── README_SIMPLE.md        # Ce fichier
```

---

## 🛠️ Base de Données

SQLite avec 2 tables :

### `conversations`
- ID, telegram_id, username, first_name
- service_type, quantity, link, details
- estimated_price, status
- created_at

### `messages`
- ID, conversation_id, telegram_id
- message, sender (client/admin/system)
- created_at

---

## 💡 Utilisation

### Pour le Client

1. Lance `/start` sur le bot
2. Clique sur "📝 Obtenir un devis"
3. Répond aux 4 questions
4. Reçoit un prix estimatif
5. Peut continuer à discuter avec le support

### Pour l'Admin

1. Va sur le dashboard
2. Voit toutes les conversations
3. Clique sur une conversation
4. Répond directement au client
5. Le client reçoit le message sur Telegram

---

## 🔒 Sécurité

- Dashboard protégé par mot de passe
- Token Telegram en variable d'environnement
- Base de données locale (non accessible en ligne)

---

## 📞 Support

Pour toute question, contactez @LeBonMot_Support sur Telegram.

---

**Version :** 1.0 Simple MVP  
**Dernière mise à jour :** Octobre 2024

