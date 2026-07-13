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

REM Check if venv exists and is valid
set VENV_VALID=0
if exist "backend\venv\Scripts\python.exe" (
    REM Test if venv is working and pip is functional
    backend\venv\Scripts\python.exe --version >nul 2>&1
    if not errorlevel 1 (
        REM Also test if pip works (pip has absolute paths that break when project moves)
        backend\venv\Scripts\python.exe -m pip --version >nul 2>&1
        if not errorlevel 1 (
            set VENV_VALID=1
            echo ✅ Environnement virtuel trouvé et valide
        )
    )
)

if %VENV_VALID%==0 (
    if exist "backend\venv\" (
        echo ⚠️  Environnement virtuel cassé détecté, suppression...
        rmdir /s /q "backend\venv"
    )
    echo 📦 Création de l'environnement virtuel...
    cd backend
    python -m venv venv
    echo 📥 Installation des dépendances...
    REM Use python -m pip instead of pip.exe to avoid shebang path issues
    venv\Scripts\python.exe -m pip install -r requirements.txt
    cd ..
)

REM Start backend
echo.
echo 🔧 Démarrage du backend Flask...
cd backend
call venv\Scripts\activate
start /B python app.py
cd ..

REM Wait for backend to start
echo ⏳ Attente du démarrage du backend...
timeout /t 3 /nobreak >nul

REM Start frontend server
echo 🌐 Démarrage du serveur frontend...
cd frontend
start /B python -m http.server 8080
cd ..

REM Wait for frontend to start
timeout /t 2 /nobreak >nul

REM Open browser
echo 🌐 Ouverture du navigateur...
start "" "http://localhost:8080"

echo.
echo ✅ Application lancée !
echo 📍 Backend API: http://localhost:5000
echo 📍 Frontend: http://localhost:8080
echo.
echo Fermez cette fenêtre pour arrêter les serveurs
echo.

pause
