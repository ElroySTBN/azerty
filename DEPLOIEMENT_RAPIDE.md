# ⚡ Déploiement Rapide - 5 Minutes

## 🚀 Option recommandée : Railway (Gratuit & Facile)

### Étape 1 : Préparer Railway (2 min)

1. Allez sur [Railway.app](https://railway.app)
2. Cliquez "Login with GitHub"
3. Autorisez Railway

### Étape 2 : Déployer (1 min)

1. Cliquez "New Project"
2. Sélectionnez "Deploy from GitHub repo"
3. Choisissez `ElroySTBN/-hh`
4. Railway démarre automatiquement le build

### Étape 3 : Configuration (2 min)

1. Dans votre projet Railway, allez dans "Variables"
2. Cliquez "New Variable" et ajoutez :

```
CLIENT_BOT_TOKEN = 7633849144:VOTRE_TOKEN_TELEGRAM
ADMIN_PASSWORD = votre_mot_de_passe_securise
FLASK_SECRET_KEY = [générer avec la commande ci-dessous]
```

Pour générer FLASK_SECRET_KEY :
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

3. Railway redémarre automatiquement

### Étape 4 : Obtenir l'URL (30 sec)

1. Dans "Settings" → "Networking" → "Public Networking"
2. Cliquez "Generate Domain"
3. Railway vous donne une URL (ex: `lebonmot-production.up.railway.app`)

### Étape 5 : Accéder au dashboard (30 sec)

Votre dashboard est accessible sur :
```
https://votre-url.railway.app
```

Login : `admin`  
Password : celui que vous avez défini dans les variables

---

## ✅ Vérification

### Tester le bot Telegram
1. Ouvrez Telegram
2. Cherchez votre bot
3. Envoyez `/start`
4. Le bot devrait répondre immédiatement ✅

### Tester le dashboard
1. Accédez à votre URL Railway
2. Connectez-vous
3. Vous devriez voir le dashboard ✅

---

## 📊 Monitoring

### Voir les logs en temps réel

1. Dans Railway, allez dans "Deployments"
2. Cliquez sur le déploiement actif
3. Onglet "View Logs"
4. Vous voyez tout ce qui se passe en temps réel

---

## 🔧 Modifications futures

Quand vous faites des changements :

```bash
# Sur votre machine locale
git add .
git commit -m "Description des changements"
git push origin main
```

Railway détecte automatiquement et redéploie ! 🎉

---

## 🆘 Problèmes courants

### Le bot ne répond pas

**Solution** :
1. Railway → "Deployments" → Logs
2. Cherchez les erreurs
3. Vérifiez que `CLIENT_BOT_TOKEN` est correct dans les variables

### Le dashboard ne s'affiche pas

**Solution** :
1. Vérifiez que Railway a bien généré un domaine public
2. Attendez 1-2 minutes après le déploiement
3. Essayez en navigation privée

### "Address already in use"

**Solution** :
C'est normal ! Railway gère les ports automatiquement. Ignorez ce message dans les logs.

---

## 💰 Coûts Railway

- **Gratuit** : 500h/mois (largement suffisant pour démarrer)
- **Starter ($5/mois)** : Illimité + meilleure performance
- **Pas de carte bancaire** nécessaire pour le plan gratuit

---

## 📱 Partager votre bot

Une fois déployé, partagez simplement le lien de votre bot :
```
https://t.me/VOTRE_BOT_USERNAME
```

---

## 🎯 Prochaines étapes

1. ✅ Testez une commande complète
2. ✅ Testez le système de support
3. ✅ Configurez votre adresse Bitcoin dans le code (si vous voulez)
4. ✅ Partagez votre bot !

---

## 📞 Besoin d'aide ?

Consultez le guide complet : [`DEPLOIEMENT.md`](DEPLOIEMENT.md)

---

**🎉 Félicitations ! Votre bot est en ligne !** 🚀

