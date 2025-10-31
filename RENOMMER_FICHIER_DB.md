# 🔄 Renommer le Fichier de Base de Données (Optionnel)

## 📋 Pourquoi "lebonmot" Apparaît dans les Logs ?

Le nom `lebonmot_simple.db` est **juste le nom du fichier SQLite** (fallback si Supabase ne fonctionne pas).

**Ce n'est PAS lié à l'erreur Supabase !** C'est juste un nom de fichier local.

---

## ✅ Si Vous Voulez le Renommer

Vous pouvez changer `lebonmot_simple.db` en `reputalys_simple.db`, mais :
- ❌ **Cela ne résoudra PAS l'erreur Supabase** (erreur "Tenant or user not found")
- ✅ **C'est juste cosmétique** (pour avoir un nom cohérent)

---

## 🔧 Comment Renommer (Si Vous Voulez)

### Option 1 : Variable d'Environnement (Simple)

1. **Railway** → Service → **Variables**
2. **Ajoutez une nouvelle variable** :
   - **Name** : `DB_PATH`
   - **Value** : `/data/reputalys_simple.db`
3. **Sauvegardez**

Le bot utilisera ce chemin au lieu de `lebonmot_simple.db`.

### Option 2 : Modifier le Code (Permanente)

Je peux modifier le code pour utiliser `reputalys_simple.db` par défaut, mais **ce n'est pas urgent** - l'erreur Supabase est plus importante à résoudre d'abord.

---

## 🎯 Priorité

**Pour l'instant, concentrez-vous sur l'erreur Supabase** :
1. ✅ Vérifiez l'URL exacte depuis Supabase
2. ✅ Vérifiez le PROJECT_ID
3. ✅ Vérifiez le format du nom d'utilisateur

**Le nom du fichier SQLite peut attendre** - ce n'est qu'un détail cosmétique.

---

**Concentrons-nous d'abord sur Supabase !** Une fois que Supabase fonctionne, vos données seront dans le cloud et vous n'aurez plus besoin de vous soucier du fichier SQLite local.

