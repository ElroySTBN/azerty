#!/bin/bash

echo "🚂 Build Railway - Le Bon Mot Mini App"
echo "========================================"

# Vérifier si npm est disponible
if command -v npm &> /dev/null; then
    echo "📦 Build du frontend React..."
    cd miniapp/frontend
    
    # Installer les dépendances
    npm ci --silent
    
    # Build avec l'URL Railway
    if [ -n "$RAILWAY_PUBLIC_DOMAIN" ]; then
        export VITE_API_URL="https://$RAILWAY_PUBLIC_DOMAIN"
        echo "✅ VITE_API_URL défini: https://$RAILWAY_PUBLIC_DOMAIN"
    else
        export VITE_API_URL="https://lebonmot-production.up.railway.app"
        echo "⚠️  Utilisation de l'URL par défaut"
    fi
    
    # Build
    npm run build
    
    cd ../..
    echo "✅ Frontend build terminé !"
else
    echo "⚠️  npm non trouvé, skip du build frontend"
    echo "   Les fichiers statiques doivent être buildés localement"
fi

echo "✅ Build Railway terminé !"

