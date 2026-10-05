# 🚀 Démarrage Rapide du CV Generator

## Une seule commande pour tout lancer !

```bash
python3 start.py
```

Ou simplement :

```bash
./start.py
```

## 🎯 Ce que fait le script

1. ✅ Vérifie Python 3
2. ✅ Crée/active l'environnement virtuel (venv)
3. ✅ Installe les dépendances backend automatiquement
4. ✅ Lance le backend Flask sur http://localhost:5000
5. ✅ Lance le frontend sur http://localhost:8080
6. ✅ Affiche les logs en temps réel
7. ✅ Arrête proprement tout avec Ctrl+C

## 📱 Accès à l'application

Une fois lancé, ouvrez votre navigateur :

**http://localhost:8080**

## ⌨️ Commandes

- **Ctrl+C** : Arrêter les serveurs proprement

## 🎨 Affichage

Le script affiche :
- Les logs du **Backend** en bleu
- Les logs du **Frontend** en cyan
- Les messages importants en couleur

## 📋 Prérequis

- Python 3.7+
- C'est tout ! Le reste est automatique

## 🔧 En cas de problème

Si le script ne fonctionne pas :

```bash
# Vérifier Python
python3 --version

# Donner les permissions
chmod +x start.py

# Lancer avec python3 explicitement
python3 start.py
```

## 🛠️ Mode Manuel (si vous préférez)

### Option 1 : Avec venv (recommandé)
```bash
# Terminal 1 - Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
python3 app.py

# Terminal 2 - Frontend
cd frontend
python3 -m http.server 8080
```

### Option 2 : Sans venv
```bash
# Terminal 1 - Backend
cd backend
pip install -r requirements.txt
python3 app.py

# Terminal 2 - Frontend
cd frontend
python3 -m http.server 8080
```

## 💡 Astuce

Ajoutez un alias dans votre shell :

```bash
# Dans ~/.bashrc ou ~/.zshrc
alias cv-start="cd /chemin/vers/cv-generator && ./start.py"
```

Puis simplement :
```bash
cv-start
```

---

**C'est tout ! Profitez de votre générateur de CV ! 🎉**
