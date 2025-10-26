#!/bin/bash

echo "🔄 Arrêt de toutes les instances Python..."
killall -9 Python 2>/dev/null
pkill -9 -f "python3 main.py" 2>/dev/null

echo "🧹 Nettoyage du webhook Telegram..."
cd /Users/elroysitbon/-hh
python3 reset_bot.py

echo "⏳ Attente de 10 secondes pour que Telegram libère la connexion..."
sleep 10

echo "🚀 Démarrage du bot..."
python3 main.py > app.log 2>&1 &

echo "⏳ Attente du démarrage..."
sleep 8

echo ""
echo "📊 Vérification du statut..."
if grep -q "Bot Client démarré et en écoute" app.log; then
    echo "✅ Bot démarré avec succès !"
    echo ""
    echo "🔗 Accès :"
    echo "   - Dashboard Admin: http://localhost:8081"
    echo "   - Bot Telegram: @lebonmot_bot"
    echo ""
    echo "📝 Pour voir les logs en direct :"
    echo "   tail -f app.log"
else
    echo "❌ Problème de démarrage. Voir les logs :"
    echo ""
    tail -20 app.log
fi

