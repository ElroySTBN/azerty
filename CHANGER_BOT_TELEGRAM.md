# 🤖 Guide : Changer de Bot Telegram

Ce guide vous explique comment créer un nouveau bot Telegram et le configurer pour Reputalys.

---

## 📱 Étape 1 : Créer un nouveau bot avec BotFather

1. **Ouvrez Telegram** sur votre téléphone ou ordinateur

2. **Recherchez et démarrez une conversation avec** `@BotFather` (le bot officiel de Telegram)

3. **Créez un nouveau bot** :
   ```
   /newbot
   ```

4. **Donnez un nom à votre bot** (ce que les utilisateurs verront) :
   ```
   Reputalys
   ```

5. **Choisissez un nom d'utilisateur** (doit se terminer par `bot`, exemple : `reputech_bot` ou `reputechbot`) :
   ```
   reputech_bot
   ```
   ⚠️ **Important** : Le nom d'utilisateur doit être unique. Si celui que vous voulez est pris, essayez :
   - `reputechbot`
   - `reputech_service_bot`
   - `reputech_support_bot`
   - Ou tout autre nom avec `_bot` à la fin

6. **Copiez le token** que BotFather vous donne :
   ```
   Exemple : 123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
   🔒 **Gardez ce token secret !** Ne le partagez jamais publiquement.

---

## 💻 Étape 2 : Configurer le token localement (sur votre ordinateur)

1. **Créez ou modifiez le fichier `.env`** à la racine du projet :

   ```bash
   # Si vous êtes sur Mac/Linux
   nano .env
   
   # Ou utilisez votre éditeur de texte préféré
   ```

2. **Ajoutez votre nouveau token** :
   ```env
   CLIENT_BOT_TOKEN=votre_nouveau_token_ici
   ADMIN_PASSWORD=votre_mot_de_passe
   SECRET_KEY=votre_cle_secrete
   ```

3. **Sauvegardez le fichier**

4. **Testez localement** :
   ```bash
   python main.py
   ```
   
   Vous devriez voir :
   ```
   🚀 Démarrage du Bot Reputalys - Version Simple...
   ✅ Bot Telegram démarré et connecté !
   ```

5. **Testez le bot** :
   - Recherchez votre bot sur Telegram (par son nom d'utilisateur, ex: `@reputech_bot`)
   - Envoyez `/start`
   - Vous devriez recevoir le message de bienvenue "🔐 **Reputalys**"

---

## ☁️ Étape 3 : Configurer le token sur Railway

1. **Connectez-vous à Railway** : https://railway.app

2. **Sélectionnez votre projet** Reputalys

3. **Allez dans "Variables"** (ou "Environment Variables")

4. **Trouvez la variable `CLIENT_BOT_TOKEN`** :
   - Si elle existe, **cliquez dessus** pour la modifier
   - Si elle n'existe pas, **cliquez sur "New Variable"**

5. **Entrez les valeurs** :
   - **Nom** : `CLIENT_BOT_TOKEN`
   - **Valeur** : Collez votre nouveau token (celui obtenu de BotFather)

6. **Cliquez sur "Save"** ou "Add"

7. **Railway va redéployer automatiquement** votre application avec le nouveau token

8. **Vérifiez que ça fonctionne** :
   - Attendez que le déploiement se termine (vérifiez les logs)
   - Testez votre bot sur Telegram : il devrait répondre avec le nouveau nom "Reputalys"

---

## 🔍 Vérification

### Sur Telegram :
- ✅ Le bot répond aux commandes `/start`
- ✅ Le message de bienvenue affiche "🔐 **Reputalys**"
- ✅ Le bot fonctionne normalement

### Sur Railway :
- ✅ Les logs affichent : `✅ Bot Telegram démarré et connecté !`
- ✅ Pas d'erreurs liées au token
- ✅ Le dashboard admin fonctionne toujours

---

## ⚠️ Important

- **Ne supprimez pas l'ancien bot** tout de suite : gardez-le en réserve au cas où
- **Le token est secret** : ne le partagez jamais publiquement (GitHub, forums, etc.)
- **Si vous perdez le token** : vous pouvez toujours le récupérer via BotFather avec `/token` et en sélectionnant votre bot
- **Les anciennes conversations** : elles sont stockées dans la base de données. Le nouveau bot ne verra que les nouvelles conversations

---

## 🆘 En cas de problème

### Le bot ne répond pas après le changement :
1. Vérifiez que le token est correct (copié-collé sans espaces)
2. Vérifiez les logs Railway pour voir les erreurs
3. Redéployez manuellement sur Railway si nécessaire

### Erreur "CLIENT_BOT_TOKEN manquant" :
1. Vérifiez que la variable est bien nommée `CLIENT_BOT_TOKEN` (exactement, avec des underscores)
2. Vérifiez qu'il n'y a pas d'espaces avant/après le token
3. Sur Railway, assurez-vous que la variable est bien enregistrée

### Besoin d'aide ?
- Vérifiez les logs Railway
- Testez le bot localement d'abord pour isoler le problème

---

**✅ Une fois terminé, votre nouveau bot Reputalys est prêt à être utilisé !**

