#!/bin/bash

echo "🔍 Vérification de l'environnement..."
echo ""

# Vérifier Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3: $(python3 --version)"
else
    echo "❌ Python3 non trouvé"
fi

# Vérifier Node.js
if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
else
    echo "❌ Node.js non trouvé"
fi

echo ""
echo "📁 Structure du projet:"
echo "   Backend:  $(ls -d ../backend 2>/dev/null && echo '✅' || echo '❌')"
echo "   Frontend: $(ls -d . && echo '✅')"
echo ""

echo "📄 Fichiers clés:"
echo "   index.html:     $(ls index.html 2>/dev/null && echo '✅' || echo '❌')"
echo "   js/main.js:     $(ls js/main.js 2>/dev/null && echo '✅' || echo '❌')"
echo "   script.backup:  $(ls script.js.backup 2>/dev/null && echo '✅' || echo '❌')"
echo ""

echo "🔢 Modules JavaScript: $(find js -name '*.js' | wc -l) fichiers"
echo ""

echo "🌐 Pour tester l'application:"
echo "   1. Démarrer le backend: cd ../backend && python3 app.py"
echo "   2. Démarrer le frontend: cd frontend && python3 -m http.server 8080"
echo "   3. Ouvrir: http://localhost:8080"
echo ""
