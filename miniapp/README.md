# 🚀 Le Bon Mot - Telegram Mini App

Mini App Telegram moderne pour commander des avis et messages de forum en toute anonymité.

## 📋 Architecture

```
miniapp/
├── frontend/          # React + Vite + Telegram Web App SDK
│   ├── src/
│   │   ├── pages/     # Pages de l'application
│   │   ├── store/     # État global (Zustand)
│   │   └── App.jsx    # Composant principal
│   └── package.json
│
└── backend/           # API Flask REST
    ├── api.py         # Routes API
    └── requirements.txt
```

## ✨ Fonctionnalités

- ✅ **Authentification Telegram** sécurisée via initData
- 📝 **Commander des avis** (Google Reviews, Trustpilot, autres)
- 💬 **Commander des messages forum**
- 📦 **Historique des commandes**
- 🛡️ **Page de garanties**
- 💬 **Support direct**
- 🎨 **Design Telegram-style minimaliste**
- 📱 **Responsive et optimisé mobile**

## 🚀 Installation

### Frontend

```bash
cd miniapp/frontend
npm install
npm run dev
```

L'app sera accessible sur `http://localhost:3000`

### Backend

```bash
cd miniapp/backend
pip install -r requirements.txt
python api.py
```

L'API sera accessible sur `http://localhost:8081`

## ⚙️ Configuration

### Frontend (.env)

Créer un fichier `.env` dans `miniapp/frontend/` :

```env
VITE_API_URL=http://localhost:8081
```

### Backend

L'API utilise les variables d'environnement existantes :
- `CLIENT_BOT_TOKEN` : Token du bot Telegram
- `PORT` : Port de l'API (défaut: 8081)

## 📱 Intégration Telegram

### 1. Créer la Mini App sur BotFather

```
1. Ouvrez @BotFather sur Telegram
2. Envoyez /newapp
3. Sélectionnez votre bot
4. Nom : Le Bon Mot
5. Description : Service anonyme de e-réputation
6. Photo : Votre logo
7. URL : https://votre-frontend.vercel.app
```

### 2. Ajouter un bouton dans le bot

Dans `src/client_bot.py`, ajouter un bouton Menu :

```python
from telegram import MenuButton, MenuButtonWebApp, WebAppInfo

# Au démarrage du bot
await client_app.bot.set_chat_menu_button(
    menu_button=MenuButtonWebApp(
        text="🚀 Ouvrir l'app",
        web_app=WebAppInfo(url="https://votre-frontend.vercel.app")
    )
)
```

Ou ajouter un bouton inline :

```python
keyboard = [
    [InlineKeyboardButton(
        "🚀 Ouvrir l'app", 
        web_app=WebAppInfo(url="https://votre-frontend.vercel.app")
    )],
    # ... autres boutons
]
```

## 🌐 Déploiement

### Frontend sur Vercel

```bash
cd miniapp/frontend
npm run build

# Puis sur Vercel :
vercel deploy
```

Configurer les variables d'environnement sur Vercel :
- `VITE_API_URL` : URL de votre API Railway

### Backend sur Railway

Le backend peut être déployé avec votre app principale sur Railway.
Pas de changements nécessaires, l'API utilise la même base de données.

## 🔒 Sécurité

- ✅ Validation des données Telegram via `initData`
- ✅ CORS configuré
- ✅ Pas de données sensibles côté frontend
- ✅ Authentification obligatoire pour toutes les routes

## 🎨 Personnalisation

### Couleurs

Modifier dans `frontend/src/index.css` :

```css
:root {
  --tg-theme-button-color: #2481cc;  /* Couleur principale */
  --tg-theme-link-color: #2481cc;    /* Couleur des liens */
}
```

### Textes

Tous les textes sont dans les fichiers `src/pages/*.jsx`

## 📊 Analytics

Pour ajouter des analytics, installer :

```bash
npm install @vercel/analytics
```

Puis dans `src/main.jsx` :

```javascript
import { Analytics } from '@vercel/analytics/react'

// Ajouter dans le render
<Analytics />
```

## 🐛 Debug

### Mode développement

Le mode développement désactive la validation stricte de `initData`.

Pour tester sans Telegram :
1. Démarrer le frontend et backend en local
2. Ouvrir dans un navigateur normal
3. L'auth fonctionnera en mode dégradé

### Logs

- Frontend : Console du navigateur
- Backend : Terminal Python

## 🔄 Migration progressive

Pour migrer progressivement du bot vers la Mini App :

1. **Phase 1** : Garder le bot, ajouter un bouton "🚀 Nouvelle interface"
2. **Phase 2** : Utiliser les deux en parallèle
3. **Phase 3** : Rediriger tous les nouveaux utilisateurs vers la Mini App
4. **Phase 4** : Désactiver le bot (optionnel)

## 📝 TODO

- [ ] Page de paiement détaillée avec QR code
- [ ] Notifications push via Telegram
- [ ] Mode sombre / clair auto
- [ ] Support multi-langue
- [ ] PWA pour installation

## 🆘 Support

Des questions ? Contactez-nous :
- Telegram : @votreusername
- Email : support@lebonmot.com

---

**Version** : 1.0.0  
**Date** : 30 Octobre 2025

