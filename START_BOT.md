# 🚀 Démarrage du Bot

## Méthode 1 : Arrière-plan (Actuel)

Le bot est actuellement lancé en arrière-plan.

**Statut** : ✅ En écoute
**Dashboard** : http://localhost:8081
**Bot Telegram** : @lebonmot_bot

### Tester
1. Ouvrez Telegram
2. Cherchez `@lebonmot_bot`
3. Envoyez `/start`

## Méthode 2 : Premier plan (Si problème)

Si le bot ne répond pas, lancez-le en premier plan pour voir les erreurs :

```bash
# Arrêter le bot en arrière-plan
pkill -f "python3 main.py"

# Lancer en premier plan
cd /Users/elroysitbon/-hh
python3 main.py
```

Vous verrez alors les logs en direct et pourrez voir les erreurs si le bot rencontre un problème.

## Résolution de problèmes

### Le bot ne répond pas

1. **Vérifier qu'il tourne** :
```bash
ps aux | grep "python3 main.py"
```

2. **Voir les derniers logs** :
```bash
tail -50 app.log
```

3. **Réinitialiser le bot Telegram** :
```bash
python3 reset_bot.py
```

4. **Redémarrer complètement** :
```bash
# Tout arrêter
killall -9 Python
pkill -9 -f python3

# Attendre 5 secondes
sleep 5

# Relancer
python3 main.py
```

### Conflit d'instance

Si vous voyez "Conflict: terminated by other getUpdates request" :

1. Fermez TOUTES les fenêtres de terminal/Python
2. Redémarrez votre Mac (solution radicale mais efficace)
3. Relancez le bot

## Vérifications

✅ Token configuré : `7633849144:AAFeGEYtqgLWTUXC3f2tjU8rV9GISIt3tEw`
✅ Bot nettoyé : Webhook supprimé
✅ Bot identifié : @lebonmot_bot
✅ Dashboard : Port 8081

## Support

Si rien ne fonctionne, envoyez-moi :
- Le contenu de `app.log`
- Le résultat de `ps aux | grep python`
- La capture d'écran de l'erreur sur Telegram

