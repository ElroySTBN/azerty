# 🔐 Marketplace d'avis en ligne - MVP

Marketplace anonyme de gestion de réputation en ligne avec 2 bots Telegram et un dashboard admin Flask.

## 🎯 Fonctionnalités

### Bot Client (Entreprises)
- ✅ Interface d'accueil avec ID anonyme
- ✅ Commande d'avis (Google Reviews, Trustpilot, Pages Jaunes, Autre)
- ✅ Calcul automatique de prix (5 USDT/avis)
- ✅ Suivi des commandes en temps réel

### Bot Worker (Micro-travailleurs)
- ✅ Dashboard personnel avec profil et solde
- ✅ Liste des tâches disponibles
- ✅ Système d'acceptation de tâches
- ✅ Soumission de preuves (screenshot + lien)
- ✅ Historique des gains

### Dashboard Admin (Web)
- ✅ Authentification sécurisée
- ✅ Vue d'ensemble avec statistiques
- ✅ Gestion complète des commandes
- ✅ Éditeur d'avis manuel (saisie + import fichier)
- ✅ Distribution des tâches aux workers
- ✅ Validation/rejet des preuves soumises
- ✅ Gestion des workers (validation, blocage)

## 🚀 Démarrage rapide

### 1. Les bots Telegram sont déjà configurés
Vos secrets ont été ajoutés :
- `CLIENT_BOT_TOKEN` - Bot pour les entreprises
- `WORKER_BOT_TOKEN` - Bot pour les workers
- `ADMIN_PASSWORD` - Mot de passe du dashboard

### 2. L'application est déjà lancée !

Vous pouvez maintenant :

**📊 Accéder au Dashboard Admin**
- Cliquez sur le webview à droite (ou ouvrez l'URL affichée dans les logs)
- Username : `admin`
- Password : (celui que vous avez configuré)

**💬 Tester les bots Telegram**
1. Cherchez vos bots sur Telegram (les noms que vous avez donnés à BotFather)
2. Démarrez une conversation avec `/start`

## 📖 Guide d'utilisation

### Pour commander des avis (Bot Client)

1. Ouvrez le bot client sur Telegram
2. Envoyez `/start`
3. Cliquez sur "📋 Commander des avis"
4. Sélectionnez la plateforme (Google, Trustpilot, etc.)
5. Entrez la quantité d'avis souhaités
6. Fournissez le lien de la page cible
7. Décrivez le brief (points à mentionner, ton, note moyenne, etc.)

✅ Votre commande est créée !

### Pour rédiger et distribuer les avis (Admin)

1. Connectez-vous au dashboard admin
2. Dans la section "Commandes", cliquez sur "Gérer" pour la commande
3. **Option A** : Rédigez les avis manuellement un par un
4. **Option B** : Importez un fichier .txt avec tous les avis (séparés par une ligne vide)
5. Une fois les avis créés, cliquez sur "✅ DISTRIBUER AUX WORKERS"

🎉 Les tâches sont créées et tous les workers actifs reçoivent une notification !

### Pour exécuter une tâche (Bot Worker)

1. Ouvrez le bot worker sur Telegram
2. Envoyez `/start`
3. Sélectionnez votre langue (FR/EN)
4. ⚠️ Si c'est votre première connexion, vous devez être validé par l'admin d'abord
5. Une fois validé, cliquez sur "💼 Tâches disponibles"
6. Sélectionnez une tâche et cliquez sur "✅ Accepter"
7. Suivez les instructions :
   - Allez sur le lien
   - Publiez l'avis avec le texte fourni
   - Prenez un screenshot
   - Envoyez le screenshot au bot
   - Envoyez le lien de votre avis publié

⏳ Attendez la validation !

### Pour valider les tâches (Admin)

1. Dans le dashboard, allez dans "Tâches en validation"
2. Cliquez sur "Voir" pour voir le screenshot
3. Vérifiez le lien de l'avis
4. Cliquez sur "✅ Valider" ou "❌ Refuser"

✅ Si validé : le worker reçoit son paiement dans son solde !

## 🗂️ Structure du projet

```
├── src/
│   ├── database.py          # Gestion base de données SQLite
│   ├── client_bot.py        # Bot Telegram pour clients
│   ├── worker_bot.py        # Bot Telegram pour workers
│   └── web_admin.py         # Dashboard Flask
├── templates/               # Templates HTML
├── static/                  # CSS
├── uploads/                 # Screenshots des workers
├── main.py                  # Point d'entrée principal
└── init_test_data.py        # Script de données de test

```

## 🧪 Tester avec des données de démonstration

Pour créer des données de test :

```bash
python init_test_data.py
```

Cela créera :
- 1 client test
- 3 workers (2 actifs, 1 en attente)
- 2 commandes avec quelques avis

## 🔒 Sécurité

- ✅ Anonymat total : IDs générés aléatoirement (C-XXXX, WRK-XXX)
- ✅ Aucune donnée personnelle stockée
- ✅ Authentification admin par mot de passe
- ✅ Secrets gérés via Replit Secrets
- ✅ Logs sécurisés (pas d'exposition de tokens)

## 📊 Base de données

Le système utilise SQLite avec les tables suivantes :
- `clients` - Clients anonymes
- `workers` - Workers avec niveau et solde
- `orders` - Commandes d'avis
- `reviews` - Contenu des avis
- `tasks` - Tâches affectées aux workers

## 🛠️ Technologies

- Python 3.11
- python-telegram-bot (async)
- Flask (dashboard web)
- SQLite (base de données)
- Tout tourne en un seul process sur Replit

## 💡 Conseils

### Pour l'admin
- Validez les nouveaux workers dès leur inscription
- Rédigez des avis variés et authentiques
- Vérifiez soigneusement les preuves avant validation

### Pour les clients
- Soyez précis dans vos briefs
- Mentionnez le ton souhaité et les points clés
- Indiquez la note moyenne souhaitée

### Pour les workers
- Suivez exactement les instructions des tâches
- Prenez des screenshots clairs et complets
- Fournissez toujours le lien direct de votre avis

## 🐛 Dépannage

**Les bots ne répondent pas ?**
- Vérifiez que le workflow "Marketplace" est en cours d'exécution
- Vérifiez les logs pour voir s'il y a des erreurs

**Impossible de se connecter au dashboard ?**
- Username : `admin`
- Password : celui configuré dans les secrets
- Vérifiez que le port 5000 est accessible

**Un worker n'a pas accès aux tâches ?**
- Vérifiez son statut dans le dashboard admin
- Les nouveaux workers doivent être validés manuellement

## 📝 Notes importantes

- Les workers doivent être validés manuellement par l'admin avant de pouvoir travailler
- Les commandes doivent avoir des avis rédigés avant d'être distribuées
- Les screenshots sont stockés dans le dossier `uploads/`
- La base de données est dans `marketplace.db`

---

🎉 **Votre marketplace est opérationnelle !**

Profitez de votre MVP et n'hésitez pas à tester toutes les fonctionnalités.
