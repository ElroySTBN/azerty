# 📍 Où est le SERVICE sur Railway ? Guide Visuel

## 🎯 L'Organisation Railway : PROJET → SERVICE

Railway est organisé en **2 niveaux** :

```
PROJET (Project)
 └── SERVICES (Services)
      └── Bot + Dashboard = 1 SERVICE
```

---

## 🔍 Étape 1 : Trouver Votre PROJET

1. **Connectez-vous sur https://railway.app**
2. Vous voyez la **liste de vos projets** (titre en haut à gauche : "Projects")
3. **Cliquez sur votre projet** (probablement nommé comme votre repo GitHub : `azerty` ou `reputalys`)

---

## 🎯 Étape 2 : Dans le PROJET, Trouver le SERVICE

Une fois que vous avez cliqué sur le PROJET, vous devriez voir :

### Option A : Vue en Liste
- Une **liste de services** dans le projet
- Exemples de noms : `web`, `bot`, `dashboard`, ou le nom de votre repo
- **Cliquez sur ce SERVICE**

### Option B : Vue Graphique / Canvas
- Un **diagramme avec des boîtes**
- Une boîte représente un SERVICE
- **Cliquez sur la boîte** qui représente votre bot/dashboard

---

## ✅ Comment Reconnaître le SERVICE ?

Le SERVICE est généralement :
- 📦 Une **carte** ou **boîte** dans le projet
- 📱 Celui qui a été créé quand vous avez déployé depuis GitHub
- 🟢 Peut avoir un **point vert** (si en ligne) ou **orange/rouge** (si problème)
- 🔗 Peut avoir un **lien public** (ex: `web-production-xxxx.up.railway.app`)

---

## 🔍 Étape 3 : Ouvrir les Settings du SERVICE

Une fois que vous avez cliqué sur le SERVICE (pas le projet !) :

1. **En haut de l'écran**, vous verrez des onglets :
   - **Deployments** (ou Déploiements)
   - **Metrics** (ou Métriques)
   - **Logs** (ou Journaux)
   - **Settings** ⚙️ ← **CLIQUEZ ICI !**
   - **Variables** (ou Variables d'environnement)

2. **Cliquez sur "Settings"** ⚙️

3. **Dans Settings du SERVICE**, vous devriez voir :
   - General
   - Health
   - Build
   - Deploy
   - Networking
   - **Volumes** ← **ICI SONT LES VOLUMES !**
   - Danger Zone

---

## 🆘 Si Vous Ne Voyez Pas de SERVICE

### Cas 1 : Vous voyez seulement le PROJET

Si quand vous cliquez sur le projet, vous ne voyez pas de service séparé :
- **Votre code est peut-être directement dans le projet**
- **Cherchez quand même l'onglet "Settings"** en haut
- **Regardez les onglets** : Deployments, Metrics, Logs, Settings, Variables

### Cas 2 : Vous ne trouvez toujours pas

**Prenez une capture d'écran** et je vous guiderai précisément !

---

## 🎯 Résumé Visuel

```
1. Railway.app → Liste de PROJETS
   └── Cliquez sur votre PROJET (ex: "azerty")

2. Dans le PROJET → Vous voyez des SERVICES
   └── Cliquez sur le SERVICE (la boîte/carte)

3. Dans le SERVICE → Onglets en haut
   └── Cliquez sur "Settings" ⚙️

4. Dans Settings du SERVICE → Section "Volumes"
   └── Cliquez sur "+ Add Volume"
```

---

## 💡 Astuce : Utilisez Supabase à la Place !

Si vous avez du mal à trouver le SERVICE, **Supabase est beaucoup plus simple** :

1. ✅ Pas besoin de chercher dans Railway
2. ✅ Configuration en 5 minutes
3. ✅ Plus fiable (données dans le cloud)
4. ✅ Pas de problème de volumes

**Je vous guide pour Supabase ?** Voir : `GUIDE_RAPIDE_SUPABASE.md`

---

## 🆘 Besoin d'Aide ?

**Faites une capture d'écran** de :
1. La page d'accueil Railway (liste des projets)
2. L'intérieur de votre projet
3. Les onglets que vous voyez

Et je vous indiquerai exactement où cliquer ! 📸

