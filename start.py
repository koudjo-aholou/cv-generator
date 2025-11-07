#!/usr/bin/env python3
"""
Script de démarrage automatique pour CV Generator
Lance le backend (Flask) et le frontend (serveur HTTP) en parallèle
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# Couleurs pour le terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color):
    print(f"{color}{message}{Colors.END}")

def print_header(message):
    print()
    print_colored(f"{'='*60}", Colors.CYAN)
    print_colored(f"  {message}", Colors.BOLD + Colors.CYAN)
    print_colored(f"{'='*60}", Colors.CYAN)
    print()

def check_python():
    """Vérifier que Python 3 est disponible"""
    version = sys.version_info
    if version.major < 3:
        print_colored("❌ Python 3 est requis", Colors.RED)
        sys.exit(1)
    print_colored(f"✅ Python {version.major}.{version.minor}.{version.micro}", Colors.GREEN)

def setup_venv():
    """Créer et activer l'environnement virtuel"""
    print_header("Configuration de l'environnement virtuel")

    venv_path = Path("backend/venv")

    if not venv_path.exists():
        print_colored("📦 Création de l'environnement virtuel...", Colors.YELLOW)
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        print_colored("✅ Environnement virtuel créé", Colors.GREEN)
    else:
        print_colored("✅ Environnement virtuel déjà existant", Colors.GREEN)

    # Déterminer le chemin de l'exécutable Python dans le venv
    if os.name == 'nt':  # Windows
        python_venv = venv_path / "Scripts" / "python.exe"
        pip_venv = venv_path / "Scripts" / "pip.exe"
    else:  # Unix/Linux/Mac
        python_venv = venv_path / "bin" / "python"
        pip_venv = venv_path / "bin" / "pip"

    return python_venv, pip_venv

def install_backend_dependencies(pip_venv):
    """Installer les dépendances du backend"""
    print_header("Installation des dépendances backend")

    requirements = Path("backend/requirements.txt")
    if not requirements.exists():
        print_colored("⚠️  requirements.txt non trouvé, création...", Colors.YELLOW)
        with open(requirements, "w") as f:
            f.write("Flask==3.0.0\n")
            f.write("Flask-CORS==4.0.0\n")
            f.write("python-dotenv==1.0.0\n")
            f.write("reportlab==4.0.7\n")
            f.write("Pillow==10.1.0\n")

    print_colored("📦 Installation des dépendances...", Colors.YELLOW)
    subprocess.run([str(pip_venv), "install", "-r", "backend/requirements.txt"], check=True)
    print_colored("✅ Dépendances installées", Colors.GREEN)

def start_backend(python_venv):
    """Démarrer le serveur Flask"""
    print_header("Démarrage du Backend (Flask)")

    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'

    backend_process = subprocess.Popen(
        [str(python_venv), "app.py"],
        cwd="backend",
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    print_colored("🚀 Backend démarré sur http://localhost:5000", Colors.GREEN)
    return backend_process

def start_frontend():
    """Démarrer le serveur HTTP pour le frontend"""
    print_header("Démarrage du Frontend (HTTP Server)")

    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "8080"],
        cwd="frontend",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    print_colored("🚀 Frontend démarré sur http://localhost:8080", Colors.GREEN)
    return frontend_process

def monitor_processes(backend_process, frontend_process):
    """Surveiller et afficher les logs des deux processus"""
    print_header("Serveurs en cours d'exécution")
    print_colored("📱 Frontend : http://localhost:8080", Colors.CYAN)
    print_colored("🔧 Backend  : http://localhost:5000", Colors.CYAN)
    print_colored("\n💡 Appuyez sur Ctrl+C pour arrêter les serveurs\n", Colors.YELLOW)

    try:
        while True:
            # Lire les logs du backend
            if backend_process.poll() is None:
                line = backend_process.stdout.readline()
                if line:
                    print(f"{Colors.BLUE}[Backend]{Colors.END} {line.rstrip()}")
            else:
                print_colored("❌ Backend s'est arrêté", Colors.RED)
                break

            # Lire les logs du frontend
            if frontend_process.poll() is None:
                line = frontend_process.stdout.readline()
                if line:
                    print(f"{Colors.CYAN}[Frontend]{Colors.END} {line.rstrip()}")
            else:
                print_colored("❌ Frontend s'est arrêté", Colors.RED)
                break

            time.sleep(0.1)

    except KeyboardInterrupt:
        print_colored("\n\n🛑 Arrêt des serveurs...", Colors.YELLOW)

def cleanup(backend_process, frontend_process):
    """Arrêter proprement les processus"""
    print_colored("🧹 Nettoyage...", Colors.YELLOW)

    if backend_process and backend_process.poll() is None:
        backend_process.terminate()
        try:
            backend_process.wait(timeout=5)
            print_colored("✅ Backend arrêté", Colors.GREEN)
        except subprocess.TimeoutExpired:
            backend_process.kill()
            print_colored("⚠️  Backend forcé à s'arrêter", Colors.YELLOW)

    if frontend_process and frontend_process.poll() is None:
        frontend_process.terminate()
        try:
            frontend_process.wait(timeout=5)
            print_colored("✅ Frontend arrêté", Colors.GREEN)
        except subprocess.TimeoutExpired:
            frontend_process.kill()
            print_colored("⚠️  Frontend forcé à s'arrêter", Colors.YELLOW)

    print_colored("\n👋 Au revoir !\n", Colors.CYAN)

def main():
    """Fonction principale"""
    print_colored("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           🚀 CV GENERATOR - DÉMARRAGE AUTO 🚀            ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """, Colors.BOLD + Colors.HEADER)

    backend_process = None
    frontend_process = None

    try:
        # Vérifier Python
        check_python()

        # Setup venv
        python_venv, pip_venv = setup_venv()

        # Installer dépendances
        install_backend_dependencies(pip_venv)

        # Démarrer les serveurs
        backend_process = start_backend(python_venv)
        time.sleep(2)  # Attendre que le backend démarre

        frontend_process = start_frontend()
        time.sleep(1)  # Attendre que le frontend démarre

        # Surveiller les processus
        monitor_processes(backend_process, frontend_process)

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print_colored(f"\n❌ Erreur : {e}", Colors.RED)
    finally:
        cleanup(backend_process, frontend_process)

if __name__ == "__main__":
    main()
