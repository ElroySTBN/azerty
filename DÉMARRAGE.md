# 🚀 Guide de Démarrage Rapide

## ✅ Ce qui est configuré

1. **Token Telegram** : Configuré dans `.env`
2. **Mode simplifié** : Bot client uniquement (workers désactivés)
3. **Dashboard admin** : Accessible sur http://localhost:5000

## 🎯 Pour démarrer l'application

### Option 1 : Lancement direct

```bash
python3 main.py
```

L'application va :
- ✅ Initialiser la base de données
- ✅ Démarrer le bot Telegram client
- ✅ Lancer le dashboard admin sur http://localhost:5000

### Option 2 : En arrière-plan

```bash
nohup python3 main.py > app.log 2>&1 &
```

Ou avec un gestionnaire de processus (recommandé) :

```bash
# Installer tmux
brew install tmux

# Démarrer une session
tmux new -s marketplace

# Lancer l'app
python3 main.py

# Quitter tmux : Ctrl+B puis D
# Revenir à la session : tmux attach -t marketplace
```

## 📊 Accéder au Dashboard

1. Ouvrez votre navigateur
2. Allez sur : **http://localhost:5000**
3. Connectez-vous :
   - Username : `admin`
   - Password : `admin123` (configurable dans `.env`)

## 🤖 Tester le bot Telegram

1. Ouvrez Telegram
2. Cherchez votre bot (nom donné à BotFather)
3. Envoyez `/start`

Vous devriez voir le menu principal du bot client.

## 📋 Checklist

- [ ] Fichier `.env` créé avec votre token
- [ ] Dépendances installées (`pip install ...`)
- [ ] Application lancée avec `python3 main.py`
- [ ] Dashboard accessible sur http://localhost:5000
- [ ] Bot Telegram répond à `/start`

## 🐛 Si ça ne fonctionne pas

### Le bot ne répond pas
```bash
# Vérifier que l'app tourne
ps aux | grep python

# Vérifier les logs
tail -f app.log
```

### Le dashboard est inaccessible
```bash
# Vérifier que le port 5000 est libre
lsof -i :5000

# Tuer le processus si nécessaire
kill -9 <PID>
```

### Erreur de modules
```bash
# Réinstaller les dépendances
pip install --upgrade python-telegram-bot python-dotenv flask werkzeug
```

## 🎉 Tout est prêt !

Votre marketplace est maintenant opérationnelle en mode simplifié :

✅ **Bot Client** : Les entreprises peuvent commander des avis  
✅ **Dashboard Admin** : Vous gérez les commandes et rédigez les avis  
❌ **Workers** : Désactivés (gestion manuelle)

Pour commencer :
1. Testez le bot avec `/start`
2. Créez une commande test
3. Rédigez des avis via le dashboard
4. Gérez les workers manuellement

---

**Besoin d'aide ?** Voir `README_SIMPLIFIÉ.md`
