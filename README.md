# 📄 LinkedIn CV Generator

Application web simple pour générer un CV professionnel à partir de votre export LinkedIn.

## 🎯 Fonctionnalités

- ✅ Import de fichiers CSV LinkedIn
- ✅ Parsing automatique des données (profil, expériences, formation, compétences, etc.)
- ✅ Upload de photo de profil (optionnel)
- ✅ Génération de CV en PDF professionnel
- ✅ **Partage par email** - Envoyez votre CV directement par email
- ✅ Interface simple et intuitive
- ✅ **100% local** - Aucune donnée n'est sauvegardée
- ✅ **Confidentialité garantie** - Tout est traité en mémoire

## 🏗️ Architecture

- **Frontend**: HTML/CSS/JavaScript (vanilla)
- **Backend**: Python Flask
- **PDF**: ReportLab
- **Stockage**: Aucun (traitement en mémoire)

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de packages Python)
- Un navigateur web moderne

## 🔒 Sécurité

Cette application a été durcie contre les vulnérabilités courantes :

- ✅ **Protection Path Traversal** - Noms de fichiers sécurisés avec UUID
- ✅ **Validation des Uploads** - Taille et type de fichier vérifiés
- ✅ **Debug Mode Désactivé** - Par défaut en mode production
- ✅ **CORS Restreint** - Accès localhost uniquement
- ✅ **Nettoyage Garanti** - Fichiers temporaires toujours supprimés
- ✅ **Logging Sécurisé** - Pas de données sensibles dans les logs clients

**⚠️ Important** : Cette application est conçue pour un **usage local uniquement**. Ne l'exposez pas sur internet sans protections supplémentaires (reverse proxy, HTTPS, authentification).

Consultez [SECURITY.md](SECURITY.md) pour plus de détails sur la sécurité.

## 🚀 Installation

### 1. Cloner le projet

```bash
cd cv-generator
```

### 2. Installer les dépendances Python

```bash
cd backend
pip install -r requirements.txt
```

Ou avec un environnement virtuel (recommandé) :

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration de l'envoi par email (optionnel)

Pour activer la fonctionnalité d'envoi de CV par email, configurez les variables d'environnement SMTP :

1. Copiez le fichier `.env.example` en `.env` :
   ```bash
   cp .env.example .env
   ```

2. Modifiez le fichier `.env` avec vos informations SMTP :
   ```env
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   SENDER_EMAIL=your-email@gmail.com
   ```

**Configuration Gmail :**
- Activez l'authentification à deux facteurs sur votre compte Google
- Générez un mot de passe d'application : [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
- Utilisez ce mot de passe dans `SMTP_PASSWORD`

**Autres fournisseurs :**
- **Outlook/Office365** : `smtp.office365.com` (port 587)
- **Yahoo** : `smtp.mail.yahoo.com` (port 587)
- **Custom SMTP** : Contactez votre fournisseur pour les détails

⚠️ **Important** : Ne commitez jamais votre fichier `.env` dans Git. Il est déjà dans `.gitignore`.

## 📦 Exporter vos données LinkedIn

Avant d'utiliser l'application, vous devez exporter vos données LinkedIn :

1. Connectez-vous à **LinkedIn**
2. Allez dans **Paramètres et confidentialité**
3. Cliquez sur **Confidentialité des données**
4. Sélectionnez **Obtenir une copie de vos données**
5. Choisissez les données suivantes :
   - ✅ Profil
   - ✅ Positions
   - ✅ Éducation
   - ✅ Compétences
   - ✅ Langues
   - ✅ Certifications
6. Demandez l'archive
7. Vous recevrez un email avec un lien de téléchargement
8. Téléchargez et **extrayez le fichier ZIP**

Les fichiers CSV seront dans le dossier extrait.

## 🎬 Lancement de l'application

### Méthode 1 : Script de démarrage (Recommandé)

Le script démarre automatiquement le backend et le frontend :

```bash
# Sur Linux/Mac
./start.sh

# Sur Windows
start.bat
```

L'application s'ouvrira automatiquement dans votre navigateur sur `http://localhost:8080`.

### Méthode 2 : Démarrage manuel

#### 1. Démarrer le backend

```bash
cd backend
python app.py
```

Vous devriez voir :

```
* Running on http://127.0.0.1:5000
```

#### 2. Démarrer le serveur frontend

Dans un nouveau terminal :

```bash
cd frontend
python3 -m http.server 8080
```

#### 3. Ouvrir l'application

Ouvrez votre navigateur et allez à `http://localhost:8080`

> **Note** : Il est important de servir le frontend via un serveur HTTP plutôt que d'ouvrir le fichier HTML directement pour éviter les problèmes CORS.

## 📖 Utilisation

1. **Téléversez vos fichiers CSV** LinkedIn dans l'interface
2. **Ajoutez une photo de profil** (optionnel) - JPG ou PNG, max 5MB
3. **Personnalisez votre CV** - Choisissez les sections à inclure et les couleurs
4. **Prévisualisez** votre CV en temps réel
5. **Téléchargez** votre CV en PDF - Votre CV sera téléchargé automatiquement ! 🎉
6. **Partagez par email** (optionnel) - Envoyez votre CV directement par email en renseignant l'adresse du destinataire

## 📁 Structure du projet

```
cv-generator/
├── backend/
│   ├── app.py                 # Application Flask principale
│   ├── linkedin_parser.py     # Parser pour fichiers LinkedIn
│   ├── cv_generator.py        # Générateur de PDF
│   └── requirements.txt       # Dépendances Python
├── frontend/
│   ├── index.html            # Interface utilisateur
│   ├── style.css             # Styles CSS
│   └── script.js             # Logique JavaScript
└── README.md                 # Ce fichier
```

## 🎨 Personnalisation

### Modifier le template de CV

Éditez le fichier `backend/cv_generator.py` pour personnaliser :
- Couleurs
- Polices
- Mise en page
- Sections à inclure

### Ajouter des templates

Vous pouvez créer plusieurs templates et permettre à l'utilisateur de choisir :

1. Créez de nouvelles classes dans `cv_generator.py` (ex: `ModernCVGenerator`, `ClassicCVGenerator`)
2. Ajoutez un sélecteur dans le frontend
3. Passez le choix du template au backend

## 🔧 Dépannage

### Le backend ne démarre pas

Vérifiez que toutes les dépendances sont installées :

```bash
pip install -r backend/requirements.txt
```

### Erreur CORS

Si vous rencontrez des erreurs CORS, vérifiez que :
- Le backend tourne sur `http://localhost:5000`
- Flask-CORS est correctement installé

### Le PDF n'est pas généré

Assurez-vous que :
- ReportLab est installé : `pip install reportlab`
- Vos fichiers CSV sont valides
- Les données ont été correctement parsées

## 🔒 Sécurité et confidentialité

- ✅ **Aucune donnée n'est sauvegardée** sur le serveur
- ✅ Tous les fichiers sont traités en mémoire
- ✅ Les fichiers temporaires sont supprimés immédiatement après traitement
- ✅ L'application fonctionne 100% en local
- ✅ Aucune connexion à internet nécessaire (sauf export LinkedIn)

## 📝 Fichiers LinkedIn supportés

| Fichier | Description |
|---------|-------------|
| `Profile.csv` | Informations personnelles |
| `Positions.csv` | Expériences professionnelles |
| `Education.csv` | Formation académique |
| `Skills.csv` | Compétences |
| `Languages.csv` | Langues parlées |
| `Certifications.csv` | Certifications obtenues |

## 🚀 Améliorations futures

- [ ] Choix de templates multiples
- [ ] Personnalisation des couleurs dans l'UI
- [ ] Sélection des sections à inclure
- [ ] Réorganisation drag & drop des sections
- [ ] Export en DOCX
- [ ] Support multilingue (FR/EN)
- [ ] Aperçu PDF dans le navigateur

## 🤝 Contribution

N'hésitez pas à proposer des améliorations !

## 📄 Licence

MIT License - Libre d'utilisation

## 💡 Support

Si vous rencontrez des problèmes :
1. Vérifiez que Python 3.8+ est installé
2. Vérifiez que toutes les dépendances sont installées
3. Consultez la section Dépannage ci-dessus

---

**Développé avec ❤️ | Vos données restent privées et locales**
