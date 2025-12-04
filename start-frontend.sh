#!/bin/bash
# Script pour démarrer le serveur frontend

cd "$(dirname "$0")/frontend"
echo "🚀 Démarrage du serveur frontend sur http://localhost:8000"
echo "📂 Répertoire: $(pwd)"
echo ""
echo "Ouvrez votre navigateur à:"
echo "  → http://localhost:8000"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter"
echo ""

python3 -m http.server 8000
