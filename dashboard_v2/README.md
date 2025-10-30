# 📱 Dashboard Mobile V2 - Le Bon Mot

Dashboard mobile-first avec PWA pour gérer les commandes d'avis en déplacement.

## ✨ Fonctionnalités

- 📱 **Mobile-First** : Interface optimisée pour smartphone
- 🔔 **PWA** : Installable sur le téléphone, notifications push
- 💬 **Chat intégré** : Réponds aux clients directement
- ⚡ **Temps réel** : Auto-refresh toutes les 30 secondes
- 🎨 **Design Telegram-style** : Interface familière et moderne

## 🚀 Installation

### 1. Intégrer à main.py

Ajoute ces lignes dans ton `main.py` :

```python
from dashboard_v2.api_mobile import mobile

# Dans ta fonction de création de l'app Flask
app.register_blueprint(mobile)
```

### 2. Générer les icônes PWA

Tu peux utiliser un service en ligne comme [Real Favicon Generator](https://realfavicongenerator.net/) ou créer manuellement :

- `static/icons/icon-192.png` (192x192px)
- `static/icons/icon-512.png` (512x512px)
- `static/icons/badge-72.png` (72x72px pour les notifications)

### 3. Lancer l'application

```bash
python main.py
```

Puis visite `http://localhost:8081/mobile`

## 📱 Installer comme PWA

### Sur iPhone
1. Ouvre Safari et va sur `http://localhost:8081/mobile`
2. Appuie sur le bouton "Partager" 
3. Sélectionne "Sur l'écran d'accueil"

### Sur Android
1. Ouvre Chrome et va sur `http://localhost:8081/mobile`
2. Appuie sur les 3 points (⋮)
3. Sélectionne "Installer l'application"

## 🔔 Notifications Push

Les notifications push nécessitent :
1. Un certificat HTTPS (même en local, utilise [ngrok](https://ngrok.com) ou [mkcert](https://github.com/FiloSottile/mkcert))
2. Une clé VAPID (génère avec `web-push generate-vapid-keys`)

Pour activer :
1. Remplace `YOUR_VAPID_PUBLIC_KEY` dans `notifications.js`
2. Configure le serveur push dans le backend

## 📊 Structure

```
dashboard_v2/
├── static/
│   ├── manifest.json      # Configuration PWA
│   ├── sw.js              # Service Worker
│   ├── css/
│   │   └── mobile.css     # Styles mobile-first
│   ├── js/
│   │   ├── app.js         # Application principale
│   │   └── notifications.js # Gestion des notifications
│   └── icons/             # Icônes PWA (à générer)
├── templates/
│   ├── mobile_dashboard.html  # Page principale
│   ├── mobile_order.html      # Détails commande
│   └── mobile_chat.html       # Chat avec client
├── api_mobile.py          # Backend API
└── README.md              # Ce fichier
```

## 🎯 Workflows

### Valider une commande
1. Dashboard → Clique sur la commande
2. Bouton "✅ Valider" → Status passe à "En cours"

### Ajouter des avis
1. Détails commande → "➕ Ajouter"
2. Saisis le contenu + note
3. Quand tous les avis sont ajoutés → "✅ Terminer"

### Livrer au client
1. Commande terminée → "📦 Livrer au client"
2. Le client reçoit une notification Telegram
3. Status passe à "Livré"

### Répondre à un client
1. Messages (onglet 💬) → Clique sur la conversation
2. Écris ton message et envoie
3. Le client reçoit sur Telegram

## 🔧 Personnalisation

### Changer les couleurs

Modifie les variables CSS dans `mobile.css` :

```css
:root {
  --telegram-blue: #0088cc;
  --telegram-light-blue: #54a9eb;
  /* ... */
}
```

### Modifier l'auto-refresh

Dans `app.js`, ligne ~165 :

```javascript
setInterval(() => this.loadOrders(), 30000); // 30 secondes
```

## 🐛 Dépannage

### Le Service Worker ne s'enregistre pas
- Vérifie que tu es en HTTPS ou `localhost`
- Ouvre la console du navigateur pour voir les erreurs
- Essaie un "hard refresh" (Ctrl+Shift+R)

### Les notifications ne marchent pas
- Vérifie que tu as autorisé les notifications
- Configure la clé VAPID
- Les notifications ne marchent que sur HTTPS

### Le chat ne rafraîchit pas
- Par défaut, il rafraîchit toutes les 5 secondes
- Pour du vrai temps réel, il faudrait WebSocket (V3)

## 🚀 Prochaines étapes (V3)

- [ ] WebSocket pour chat temps réel
- [ ] Notifications push complètes
- [ ] Mode offline complet
- [ ] Upload de photos dans le chat
- [ ] Statistiques avancées
- [ ] Mode sombre

## 💡 Conseils

- **Utilise-le en local** pour commencer
- **Teste sur ton téléphone** en local (trouve ton IP locale)
- **Déploie sur Railway** quand tu es prêt (HTTPS automatique)
- **Active les notifications** dès que possible pour être alerté

---

**Créé avec ❤️ pour Le Bon Mot MVP**

