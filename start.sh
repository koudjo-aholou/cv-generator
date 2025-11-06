#!/bin/bash

echo "🚀 Démarrage de LinkedIn CV Generator..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Check if venv exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 Installation des dépendances..."
    pip install -r requirements.txt
    cd ..
else
    echo "✅ Environnement virtuel trouvé"
fi

# Start backend
echo ""
echo "🔧 Démarrage du backend Flask..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Attente du démarrage du serveur..."
sleep 3

# Open frontend in browser
echo "🌐 Ouverture du navigateur..."
if command -v xdg-open &> /dev/null; then
    xdg-open "frontend/index.html"
elif command -v open &> /dev/null; then
    open "frontend/index.html"
else
    echo "📂 Ouvrez manuellement: frontend/index.html"
fi

echo ""
echo "✅ Application lancée !"
echo "📍 Backend: http://localhost:5000"
echo "📍 Frontend: frontend/index.html"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Arrêt du serveur...'; kill $BACKEND_PID; exit 0" INT

wait $BACKEND_PID
