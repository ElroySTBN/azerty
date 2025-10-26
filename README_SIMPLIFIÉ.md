# 🔐 Marketplace d'avis - Version Simplifiée

Version simplifiée pour les clients uniquement. Les workers sont gérés manuellement.

## 🚀 Démarrage rapide

### 1. Configuration

Le fichier `.env` est déjà créé avec votre token Telegram.

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
# ou avec uv
uv pip install -r requirements.txt
```

### 3. Lancer l'application

```bash
python main.py
```

### 4. Accéder au Dashboard Admin

Ouvrez votre navigateur sur : **http://localhost:5000**

- Username : `admin`
- Password : `admin123` (configurable dans `.env`)

### 5. Tester le bot Telegram

1. Ouvrez Telegram
2. Cherchez votre bot (le nom que vous avez donné à BotFather)
3. Envoyez `/start`

## 📖 Utilisation

### Pour les clients (via Telegram)

1. Ouvrez le bot sur Telegram
2. Cliquez sur "📋 Commander des avis"
3. Sélectionnez la plateforme (Google Reviews, Trustpilot, etc.)
4. Indiquez la quantité d'avis souhaités
5. Fournissez le lien de la page cible
6. Décrivez le brief (points à mentionner, ton, note moyenne)

✅ La commande est créée et visible dans le dashboard admin

### Pour l'admin (via Dashboard)

1. Connectez-vous sur http://localhost:5000
2. Cliquez sur "Gérer" pour une commande
3. Rédigez les avis manuellement ou importez un fichier .txt
4. Les avis sont prêts pour traitement manuel

#### Ajout manuel d'avis
- Utilisez le formulaire pour ajouter un avis à la fois
- Ou importez un fichier .txt avec tous les avis (séparés par une ligne vide)

## ⚙️ Configuration

Le fichier `.env` contient :
- `CLIENT_BOT_TOKEN` : Token du bot Telegram
- `ADMIN_PASSWORD` : Mot de passe du dashboard
- `FLASK_SECRET_KEY` : Clé secrète Flask

Pour modifier ces valeurs, éditez le fichier `.env`

## 📁 Structure

```
├── .env                    # Configuration
├── main.py                 # Point d'entrée
├── src/
│   ├── client_bot.py      # Bot Telegram client
│   ├── database.py        # Base de données SQLite
│   └── web_admin.py       # Dashboard Flask
├── templates/              # Templates HTML
├── static/                # CSS
└── marketplace.db         # Base de données (créée automatiquement)
```

## 🔑 Mode Simplifié

- ✅ Bot client fonctionnel
- ✅ Dashboard admin opérationnel
- ✅ Gestion des commandes d'avis
- ✅ Édition et import d'avis
- ❌ Workers désactivés (gestion manuelle)

## 💡 Astuces

### Générer des données de test

```bash
python init_test_data.py
```

Cela créera :
- 1 client test
- 2 commandes avec quelques avis

### Import de fichiers .txt

Format du fichier :
```
Premier avis avec du texte assez long pour être réaliste...

Deuxième avis complètement différent et unique...

Troisième avis avec un ton différent...

```

Séparez chaque avis par une **ligne vide**.

## 🐛 Dépannage

**Le bot ne répond pas ?**
- Vérifiez que le token dans `.env` est correct
- Assurez-vous que l'application est en cours d'exécution

**Erreur de connexion à la base de données ?**
- Le fichier `marketplace.db` est créé automatiquement au premier lancement

**Dashboard inaccessible ?**
- Vérifiez que le port 5000 n'est pas déjà utilisé
- Essayez http://127.0.0.1:5000 au lieu de localhost

## 📝 Notes importantes

- La base de données est locale (fichier `marketplace.db`)
- Les workers sont gérés indépendamment
- Vous pouvez ajouter/supprimer des avis à tout moment
- Les commandes restent visibles dans le dashboard

---

**Besoin d'aide ?** Consultez le README.md principal pour plus de détails.
