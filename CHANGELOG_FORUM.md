# 🆕 Nouveauté : Messages sur Forums

## 📋 Résumé

Le bot supporte maintenant **deux types de commandes** :
- ⭐ **Avis** (Google Reviews, Trustpilot, autres plateformes)
- 💬 **Messages sur forums** (posts sur n'importe quel forum)

---

## ✨ Nouvelles fonctionnalités

### 1. Menu principal mis à jour
Le menu principal propose maintenant deux options distinctes :
- "📝 Commander des avis"
- "💬 Messages sur forums"

### 2. Workflow dédié pour les messages forum

#### Étapes du workflow forum :
1. **Nombre de messages** à poster
2. **URL du forum/topic** où poster
3. **Sujet/Contexte** des messages
4. **Choix de rédaction** (client ou Le Bon Mot)
5. **Instructions** (si génération par Le Bon Mot)
6. **Validation et paiement**

#### Différences avec les avis :
- Pas de choix de plateforme (plateforme = "💬 Messages Forum")
- Demande du sujet/contexte des messages
- Workflow en 5 étapes (au lieu de 6)
- Délai de livraison : 24-48h (au lieu de 48-72h)

### 3. Prix identiques
- Prix de base : **5 USDT** par message
- Génération de contenu : **+0.50 USDT** par message
- Même système de paiement crypto

---

## 🔧 Modifications techniques

### Base de données
- ✅ Nouvelle colonne `order_type` dans la table `orders`
- ✅ Valeurs possibles : `'reviews'` ou `'forum'`
- ✅ Migration automatique avec valeur par défaut `'reviews'`

### Bot Telegram (`src/client_bot.py`)
- ✅ Nouveau callback `order:type_reviews` et `order:type_forum`
- ✅ Nouvelle fonction `build_recap_text_forum()` pour les récapitulatifs
- ✅ Gestion du workflow forum dans `handle_order_flow()`
- ✅ Adaptation des messages selon le type (avis vs messages)
- ✅ Stockage du sujet du forum dans le brief de commande

### Dashboard Admin
- ✅ Colonne "Type" dans le tableau des commandes
- ✅ Badge coloré : 💬 (violet) pour forum, ⭐ (bleu) pour avis
- ✅ Nouvelle colonne "Plateforme" distincte du type
- ✅ Page de détails adaptée selon le type :
  - Affichage conditionnel des notes (uniquement pour les avis)
  - Terminologie adaptée (messages vs avis)
  - Formulaires d'import/ajout manuel adaptés

### Templates HTML
- ✅ `dashboard.html` : Affichage du type de commande
- ✅ `order_details.html` : Interface adaptative selon le type

---

## 🎯 Utilisation

### Pour les clients (Telegram)
1. `/start` → Choisir "💬 Messages sur forums"
2. Suivre le workflow guidé
3. Payer en crypto
4. Recevoir les messages sous 24-48h

### Pour l'admin (Dashboard)
1. Les commandes forum apparaissent avec un badge 💬 violet
2. La page de détails s'adapte automatiquement :
   - Pas de champ "Note" pour les messages forum
   - Labels adaptés ("Message" au lieu de "Avis")
3. Ajouter/importer les messages comme pour les avis

---

## 📊 Exemples de commandes forum

### Cas d'usage typiques :
- Promotion d'un produit sur un forum thématique
- Témoignages clients sur des forums d'entraide
- Questions/réponses techniques pour créer de l'engagement
- Posts informatifs pour améliorer la visibilité
- Messages de recommandation sur des forums professionnels

---

## 🔄 Compatibilité

- ✅ **Rétrocompatibilité** : Les anciennes commandes restent de type `'reviews'` par défaut
- ✅ **Aucun impact** sur les commandes existantes
- ✅ **Migration automatique** lors du démarrage

---

## 🚀 Déploiement

Pour déployer les changements :

```bash
# 1. Arrêter le bot actuel (si en local)
killall -9 Python

# 2. Commit et push sur GitHub
git add .
git commit -m "✨ Ajout fonctionnalité messages forum"
git push origin main

# 3. Railway redéploie automatiquement
# La migration de la base de données s'exécutera au démarrage
```

---

## 📝 Notes

- Les prix sont identiques entre avis et messages forum
- Le système de génération de contenu fonctionne de la même manière
- L'admin peut gérer les deux types de commandes de façon unifiée
- Le support client fonctionne de la même manière

---

**Date d'ajout** : 30 Octobre 2025  
**Version** : 1.1.0

