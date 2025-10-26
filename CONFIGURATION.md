# 🔧 Guide de Configuration des Bots Telegram

Ce guide vous explique comment configurer ce projet pour utiliser **n'importe quels bots Telegram**.

## 📋 Vue d'ensemble

Ce système utilise **2 bots Telegram distincts** :
1. **Bot CLIENT** - Pour les entreprises qui commandent des avis
2. **Bot WORKER** - Pour les microworkers qui exécutent les tâches

## 🚀 Configuration Rapide (5 minutes)

### Étape 1 : Créer vos bots

1. Ouvrez Telegram et cherchez **[@BotFather](https://t.me/BotFather)**
2. Envoyez `/newbot` et suivez les instructions
3. Créez **2 bots différents** avec des noms distincts :
   - Exemple : "MonMarketplace Client" et "MonMarketplace Worker"
4. Notez les **tokens** que BotFather vous donne

### Étape 2 : Configurer les variables

#### Sur Replit (Recommandé)

1. Cliquez sur l'onglet **"Secrets"** (cadenas) dans la sidebar
2. Ajoutez ces secrets :
   ```
   CLIENT_BOT_TOKEN = 1234567890:ABCdefGHIjkl...
   WORKER_BOT_TOKEN = 1234567890:XYZuvwRSTmno...
   ADMIN_PASSWORD = VotreMotDePasseSecurise
   FLASK_SECRET_KEY = UneCleAleatoireGeneratee
   ```
3. Sauvegardez

#### En local

1. Créez un fichier `.env` à la racine du projet
2. Copiez `env.example` vers `.env` :
   ```bash
   cp env.example .env
   ```
3. Éditez `.env` et remplissez vos tokens :
   ```bash
   CLIENT_BOT_TOKEN=votre_token_ici
   WORKER_BOT_TOKEN=votre_token_ici
   ADMIN_PASSWORD=votre_mot_de_passe
   FLASK_SECRET_KEY=votre_clé_secrète
   ```

### Étape 3 : Lancer

```bash
python main.py
```

## ✅ Vérification

Si tout fonctionne, vous verrez :
```
🚀 Démarrage de la Marketplace d'avis...
✅ Base de données initialisée
🤖 Configuration des bots Telegram...
✅ Bot Client démarré et en écoute
✅ Bot Worker démarré et en écoute
🌐 Démarrage du dashboard Flask...
📊 Dashboard Admin: http://0.0.0.0:5000
```

## 🔄 Changer de Bots

Pour utiliser d'autres bots Telegram :

1. Créez de nouveaux bots via BotFather (ou réutilisez d'anciens)
2. Mettez à jour seulement les tokens dans les secrets
3. Redémarrez l'application

C'est tout ! Le système fonctionne avec n'importe quels bots.

## 🐛 Problèmes Courants

### "Erreur : Les tokens des bots ne sont pas configurés"

➡️ Les secrets ne sont pas définis. Vérifiez que vous avez bien ajouté :
- `CLIENT_BOT_TOKEN`
- `WORKER_BOT_TOKEN`
- `ADMIN_PASSWORD`

### "Les bots ne répondent pas"

➡️ Vérifiez que :
- Les tokens sont corrects
- Les bots n'ont pas été supprimés sur BotFather
- L'application est bien en cours d'exécution

### "Bot API token invalid"

➡️ Le token est incorrect ou a expiré. Créez un nouveau bot et utilisez son nouveau token.

## 📱 Trouver vos bots

Une fois configurés, trouvez vos bots sur Telegram :
- Bot Client : `https://t.me/VotreBotClient`
- Bot Worker : `https://t.me/VotreBotWorker`

Envoyez `/start` pour tester !

## 🔒 Sécurité

⚠️ **IMPORTANT** :
- Ne partagez JAMAIS vos tokens publiquement
- Ne commitez PAS le fichier `.env` sur Git
- Utilisez des mots de passe forts pour `ADMIN_PASSWORD`
- Sur Replit, utilisez toujours les Secrets (pas de hard-coding)

## 💡 Conseils

- Vous pouvez utiliser des bots déjà existants
- Changez les bots à tout moment, juste en mettant à jour les tokens
- Testez chaque bot séparément avec `/start`
- Le système fonctionne avec n'importe quels noms de bots

---

**Besoin d'aide ?** Consultez le README.md principal.
