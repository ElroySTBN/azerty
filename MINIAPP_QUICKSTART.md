# 🚀 GUIDE DE DÉMARRAGE - Mini App Telegram

## ✅ **La Mini App est prête !**

Tous les fichiers ont été créés. Voici comment la lancer :

---

## 📦 Étape 1 : Installation

### Frontend (React)

```bash
cd /Users/elroysitbon/-hh/miniapp/frontend
npm install
```

### Backend (API Flask)

```bash
cd /Users/elroysitbon/-hh/miniapp/backend
pip3 install -r requirements.txt
```

---

## 🚀 Étape 2 : Lancement en local

### Terminal 1 : Backend API

```bash
cd /Users/elroysitbon/-hh/miniapp/backend
python3 api.py
```

✅ L'API tournera sur `http://localhost:8081`

### Terminal 2 : Frontend React

```bash
cd /Users/elroysitbon/-hh/miniapp/frontend
npm run dev
```

✅ L'app tournera sur `http://localhost:3000`

---

## 🧪 Étape 3 : Test en local

1. **Ouvrir** `http://localhost:3000` dans votre navigateur
2. **Vous verrez** l'interface de la Mini App
3. **En mode dev**, l'authentification est simplifiée

> ⚠️ **Note** : En local, vous ne serez pas dans Telegram, donc certaines fonctionnalités (comme le bouton "Fermer") ne fonctionneront pas. C'est normal !

---

## 📱 Étape 4 : Tester dans Telegram

### Option A : ngrok (rapide pour test)

```bash
# Terminal 3
ngrok http 3000
```

Vous obtiendrez une URL comme : `https://abc123.ngrok.io`

Ensuite, sur Telegram :
1. Ouvrez votre bot
2. Envoyez un message avec un lien : `https://abc123.ngrok.io`
3. Cliquez sur le lien

### Option B : Déployer sur Vercel (recommandé)

```bash
cd /Users/elroysitbon/-hh/miniapp/frontend
npm run build
vercel deploy
```

---

## 🔧 Étape 5 : Intégrer au bot Telegram

### Méthode 1 : Menu Button (Recommandé)

Ajouter dans `main.py` après le démarrage du client_app :

```python
from telegram import MenuButtonWebApp, WebAppInfo

# URL de votre Mini App (Vercel ou autre)
MINIAPP_URL = "https://votre-app.vercel.app"

async with client_app:
    await client_app.start()
    
    # Configurer le bouton Menu
    await client_app.bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="🚀 Ouvrir l'app",
            web_app=WebAppInfo(url=MINIAPP_URL)
        )
    )
    
    await client_app.updater.start_polling()
    # ... reste du code
```

### Méthode 2 : Bouton Inline

Modifier `src/client_bot.py` dans la fonction `start()` :

```python
from telegram import WebAppInfo

keyboard = [
    [InlineKeyboardButton("🚀 Ouvrir l'app", web_app=WebAppInfo(url=MINIAPP_URL))],
    [InlineKeyboardButton("📝 Commander des avis", callback_data="order:type_reviews")],
    # ... autres boutons
]
```

---

## 🌐 Étape 6 : Déploiement Production

### Frontend sur Vercel

```bash
cd miniapp/frontend

# Build
npm run build

# Deploy
vercel deploy --prod

# Note : Configurer VITE_API_URL dans Vercel
# Settings → Environment Variables
# VITE_API_URL = https://votre-backend.up.railway.app
```

### Backend sur Railway

Votre backend actuel sur Railway peut servir l'API.  
Ajoutez simplement `flask-cors` aux requirements :

```bash
# Dans votre requirements.txt principal
flask-cors==4.0.0
```

Puis créez un nouveau fichier `api_miniapp.py` ou intégrez les routes dans votre Flask existant.

---

## 🎨 Personnalisation

### Changer les couleurs

Éditez `miniapp/frontend/src/index.css` :

```css
:root {
  --tg-theme-button-color: #2481cc;  /* Votre couleur */
}
```

### Changer les textes

Tous les textes sont dans `miniapp/frontend/src/pages/*.jsx`

---

## 🔒 Sécurité

### En production

1. **Activer la validation stricte** :
   - Supprimer la condition `ENV == 'development'` dans `api.py`
   - Vérifier que `CLIENT_BOT_TOKEN` est configuré

2. **HTTPS obligatoire** :
   - Telegram n'accepte que HTTPS pour les Mini Apps
   - Vercel fournit HTTPS automatiquement

---

## 🐛 Troubleshooting

### Erreur CORS

Si vous voyez des erreurs CORS dans la console :

```python
# Dans api.py
CORS(app, origins=["https://votre-frontend.vercel.app"])
```

### Authentification échoue

Vérifiez que :
1. `CLIENT_BOT_TOKEN` est correct
2. La Mini App est ouverte depuis Telegram (pas navigateur direct)
3. initData est bien envoyé

### Interface ne charge pas

1. Vérifier que l'API tourne (`http://localhost:8081/health`)
2. Vérifier `.env` dans frontend avec bon `VITE_API_URL`
3. Vérifier la console du navigateur pour les erreurs

---

## 📊 Workflow recommandé

```
1. Développement Local
   ├── Backend : localhost:8081
   ├── Frontend : localhost:3000
   └── Test navigateur direct

2. Test Telegram
   ├── ngrok pour exposer frontend
   └── Tester dans Telegram

3. Production
   ├── Frontend : Vercel
   ├── Backend : Railway (existant)
   └── Configurer les URLs
```

---

## 🎯 Prochaines étapes

Une fois que tout fonctionne :

- [ ] Ajouter la page de paiement avec QR code
- [ ] Implémenter les notifications Telegram
- [ ] Ajouter l'historique des messages support
- [ ] PWA pour installation sur mobile

---

## ❓ Questions ?

La Mini App est **complètement fonctionnelle** :
- ✅ 5 pages (Accueil, Commandes avis, Commandes forum, Liste, Support, Garanties)
- ✅ Authentification Telegram
- ✅ API REST complète
- ✅ Design moderne Telegram-style
- ✅ Responsive mobile

**Besoin d'aide ?** Demandez-moi ! 🚀

---

**Version** : 1.0.0  
**Date** : 30 Octobre 2025  
**Stack** : React + Vite + Flask + SQLite + Telegram Web App SDK

