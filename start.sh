#!/bin/bash

echo "🚀 Démarrage de LinkedIn CV Generator..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Check if venv exists and is valid
VENV_VALID=0
if [ -f "backend/venv/bin/python" ]; then
    # Test if venv is working
    if backend/venv/bin/python --version &> /dev/null; then
        VENV_VALID=1
        echo "✅ Environnement virtuel trouvé et valide"
    fi
fi

if [ $VENV_VALID -eq 0 ]; then
    if [ -d "backend/venv" ]; then
        echo "⚠️  Environnement virtuel cassé détecté, suppression..."
        rm -rf backend/venv
    fi
    echo "📦 Création de l'environnement virtuel..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    echo "📥 Installation des dépendances..."
    pip install -r requirements.txt
    cd ..
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
echo "⏳ Attente du démarrage du backend..."
sleep 3

# Start frontend server
echo "🌐 Démarrage du serveur frontend..."
cd frontend
python3 -m http.server 8080 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 2

# Open browser
echo "🌐 Ouverture du navigateur..."
if command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:8080"
elif command -v open &> /dev/null; then
    open "http://localhost:8080"
else
    echo "📂 Ouvrez manuellement: http://localhost:8080"
fi

echo ""
echo "✅ Application lancée !"
echo "📍 Backend API: http://localhost:5000"
echo "📍 Frontend: http://localhost:8080"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter les serveurs"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Arrêt des serveurs...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

wait $BACKEND_PID
