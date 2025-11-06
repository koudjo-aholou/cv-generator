@echo off
echo 🚀 Démarrage de LinkedIn CV Generator...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installé. Veuillez l'installer d'abord.
    pause
    exit /b 1
)

REM Check if venv exists
if not exist "backend\venv\" (
    echo 📦 Création de l'environnement virtuel...
    cd backend
    python -m venv venv
    call venv\Scripts\activate
    echo 📥 Installation des dépendances...
    pip install -r requirements.txt
    cd ..
) else (
    echo ✅ Environnement virtuel trouvé
)

REM Start backend
echo.
echo 🔧 Démarrage du backend Flask...
cd backend
call venv\Scripts\activate
start /B python app.py
cd ..

REM Wait for backend to start
echo ⏳ Attente du démarrage du serveur...
timeout /t 3 /nobreak >nul

REM Open frontend in browser
echo 🌐 Ouverture du navigateur...
start "" "frontend\index.html"

echo.
echo ✅ Application lancée !
echo 📍 Backend: http://localhost:5000
echo 📍 Frontend: frontend\index.html
echo.
echo Fermez cette fenêtre pour arrêter le serveur
echo.

pause
