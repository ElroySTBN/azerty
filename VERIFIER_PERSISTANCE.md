# ✅ Comment Vérifier que Vos Données sont Persistantes

## 🔍 Vérification Rapide (30 secondes)

### 1. Regardez les Logs Railway au Démarrage

Dans les **logs Railway** (onglet "Logs"), cherchez ces lignes au démarrage :

```
✅ Railway détecté : utilisation de /data/lebonmot_simple.db (volume persistant)
📁 Base de données : /data/lebonmot_simple.db
   Chemin absolu : /data/lebonmot_simple.db
   Fichier existe : True
   Taille : XXXX octets
```

### ✅ Si vous voyez `/data/lebonmot_simple.db` :
**Vos données sont persistantes !** Le volume est monté correctement.

### ❌ Si vous voyez `./lebonmot_simple.db` :
**Vos données ne sont PAS persistantes !** Le volume n'est pas monté. Voir `GARANTIR_PERSISTANCE_DONNEES.md`.

---

## 🧪 Test Complet de Persistance (5 minutes)

### Étape 1 : Passer une Commande
1. Ouvrez votre bot Telegram
2. Tapez `/start`
3. Passez une commande complète (jusqu'au devis final)
4. Vérifiez dans le bot : "Mes commandes" → La commande doit apparaître

### Étape 2 : Noter la Commande
Notez les détails de la commande :
- Service : ?
- Quantité : ?
- Prix : ?
- Date : ?

### Étape 3 : Faire un Redéploiement
1. Faites un petit changement de code (ajoutez un commentaire dans `main.py`)
2. Committez et poussez sur GitHub :
   ```bash
   git add main.py
   git commit -m "test persistance"
   git push
   ```
3. Attendez que Railway redéploie (2-3 minutes)

### Étape 4 : Vérifier que la Commande est Toujours Là
1. Attendez la fin du redéploiement
2. Allez dans le bot : "Mes commandes"
3. **✅ La commande doit toujours être là avec tous les détails !**

---

## 📊 Checklist de Vérification

- [ ] Logs Railway affichent `/data/lebonmot_simple.db` (pas `./lebonmot_simple.db`)
- [ ] Volume `/data` est monté dans Railway (Settings → Volumes)
- [ ] Test effectué : commande persiste après redéploiement
- [ ] Dashboard affiche toujours les anciennes commandes après redéploiement

---

## 🆘 Problèmes Courants

### Les données se perdent toujours après redéploiement

**Cause probable** : Le volume persistant n'est pas configuré.

**Solution** :
1. Allez sur Railway → Votre Service → Settings → Volumes
2. Créez un volume avec le path `/data` et taille `1GB`
3. Redéployez
4. Vérifiez les logs : doivent afficher `/data/lebonmot_simple.db`

### Les logs affichent `./lebonmot_simple.db`

**Cause probable** : Le volume n'est pas monté ou mal configuré.

**Solution** :
1. Vérifiez que le volume existe dans Railway (Settings → Volumes)
2. Vérifiez que le Mount Path est exactement `/data` (pas `/data/`)
3. Vérifiez que le volume est attaché à votre service
4. Redéployez manuellement si nécessaire

---

## 🎯 Résultat Attendu

Une fois correctement configuré, **VOS DONNÉES NE SE PERDRONT JAMAIS**, même après :
- ✅ Redéploiements
- ✅ Redémarrages
- ✅ Mises à jour de code
- ✅ Changements de configuration

**Les données sont stockées dans le volume persistant `/data` qui survit à tout !**

