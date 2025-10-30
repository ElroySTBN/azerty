#!/bin/bash

echo "🚀 Démarrage de la Mini App Le Bon Mot"
echo "======================================"
echo ""

# Vérifier si npm est installé
if ! command -v npm &> /dev/null; then
    echo "❌ npm n'est pas installé. Installez Node.js d'abord."
    exit 1
fi

# Vérifier si python3 est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 n'est pas installé."
    exit 1
fi

# Installation des dépendances frontend si nécessaire
if [ ! -d "miniapp/frontend/node_modules" ]; then
    echo "📦 Installation des dépendances frontend..."
    cd miniapp/frontend
    npm install
    cd ../..
fi

# Installation des dépendances backend si nécessaire
if ! python3 -c "import flask" &> /dev/null; then
    echo "📦 Installation des dépendances backend..."
    pip3 install -r miniapp/backend/requirements.txt
fi

echo ""
echo "✅ Prêt à démarrer !"
echo ""
echo "🔧 Terminal 1 : Backend API"
echo "   cd miniapp/backend && python3 api.py"
echo ""
echo "🎨 Terminal 2 : Frontend React"
echo "   cd miniapp/frontend && npm run dev"
echo ""
echo "📱 Ensuite, ouvrez http://localhost:3000"
echo ""
read -p "Appuyez sur Entrée pour démarrer le backend..."

cd miniapp/backend
python3 api.py

