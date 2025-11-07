# Intégration de l'API LinkedIn

Ce document décrit comment configurer et utiliser l'intégration de l'API LinkedIn pour récupérer automatiquement les données de profil au lieu d'utiliser des fichiers CSV.

## Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Configuration](#configuration)
- [Obtenir les credentials LinkedIn](#obtenir-les-credentials-linkedin)
- [Utilisation](#utilisation)
- [Architecture](#architecture)
- [Limitations](#limitations)
- [Dépannage](#dépannage)

---

## Vue d'ensemble

L'intégration LinkedIn API permet aux utilisateurs de :

1. **Se connecter avec LinkedIn** via OAuth 2.0
2. **Récupérer automatiquement** les données de profil (expérience, éducation, compétences, etc.)
3. **Générer un CV** sans avoir à exporter manuellement des fichiers CSV

### Avantages par rapport aux CSV

- ✅ **Données toujours à jour** : récupération directe depuis LinkedIn
- ✅ **Expérience utilisateur simplifiée** : un seul clic pour se connecter
- ✅ **Pas de manipulation de fichiers** : plus besoin d'exporter et uploader des CSV
- ✅ **Sécurisé** : authentification OAuth 2.0 standard

---

## Configuration

### 1. Obtenir les credentials LinkedIn

#### Étape 1 : Créer une application LinkedIn

1. Allez sur [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Cliquez sur **"Create app"**
3. Remplissez les informations requises :
   - **App name** : `CV Generator` (ou le nom de votre choix)
   - **LinkedIn Page** : sélectionnez une page ou créez-en une
   - **Privacy policy URL** : ajoutez l'URL de votre politique de confidentialité
   - **App logo** : téléchargez un logo (optionnel)

#### Étape 2 : Configurer les permissions

1. Dans l'onglet **"Products"**, demandez l'accès aux produits suivants :
   - **Sign In with LinkedIn** (requis)
   - **Share on LinkedIn** (optionnel, pour les permissions étendues)

2. Dans l'onglet **"Auth"**, configurez :
   - **Redirect URLs** : `http://localhost:5000/api/linkedin/callback`
   - Pour production, ajoutez également : `https://votre-domaine.com/api/linkedin/callback`

#### Étape 3 : Récupérer les credentials

1. Dans l'onglet **"Auth"**, copiez :
   - **Client ID**
   - **Client Secret** (cliquez sur "Show" pour le révéler)

### 2. Configurer l'application

#### Créer le fichier .env

Copiez le fichier `.env.example` en `.env` :

```bash
cp .env.example .env
```

#### Remplir les variables d'environnement

Éditez le fichier `.env` et remplissez les valeurs :

```bash
# Flask Secret Key (générez une nouvelle clé)
FLASK_SECRET_KEY=votre-clé-secrète-générée

# LinkedIn API Configuration
LINKEDIN_CLIENT_ID=votre-client-id-linkedin
LINKEDIN_CLIENT_SECRET=votre-client-secret-linkedin
LINKEDIN_REDIRECT_URI=http://localhost:5000/api/linkedin/callback

# Frontend URL
FRONTEND_URL=http://localhost:8080
```

**Important** : Pour générer une clé secrète Flask sécurisée :

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Installer les dépendances

Le service LinkedIn utilise la bibliothèque `requests`. Vérifiez qu'elle est installée :

```bash
pip install requests
```

Ou installez toutes les dépendances :

```bash
pip install -r backend/requirements.txt
```

---

## Utilisation

### Côté Frontend

#### 1. Importer le service LinkedIn

```javascript
import { linkedinService } from './services/api/linkedinService.js';
```

#### 2. Initier la connexion LinkedIn

```javascript
// Bouton de connexion
document.getElementById('linkedin-login-btn').addEventListener('click', async () => {
    try {
        await linkedinService.initiateAuth();
        // L'utilisateur sera redirigé vers LinkedIn
    } catch (error) {
        console.error('Erreur de connexion:', error);
    }
});
```

#### 3. Vérifier l'authentification au chargement de la page

```javascript
// Au chargement de la page (main.js par exemple)
window.addEventListener('DOMContentLoaded', () => {
    // Vérifier si l'utilisateur revient de LinkedIn
    if (linkedinService.checkAuthCallback()) {
        // Authentification réussie, récupérer les données
        loadLinkedInProfile();
    }
});
```

#### 4. Récupérer les données du profil

```javascript
async function loadLinkedInProfile() {
    try {
        const profileData = await linkedinService.getProfile();

        // Les données sont au même format que le parser CSV
        console.log('Profil:', profileData.profile);
        console.log('Expériences:', profileData.positions);
        console.log('Éducation:', profileData.education);
        console.log('Compétences:', profileData.skills);

        // Utiliser les données comme avec les CSV
        cvStateService.setParsedData(profileData);

    } catch (error) {
        console.error('Erreur lors de la récupération du profil:', error);
    }
}
```

#### 5. Déconnexion

```javascript
document.getElementById('linkedin-logout-btn').addEventListener('click', async () => {
    try {
        await linkedinService.logout();
    } catch (error) {
        console.error('Erreur de déconnexion:', error);
    }
});
```

### Côté Backend

Le backend expose les endpoints suivants :

#### GET `/api/linkedin/auth`

Initie le flux OAuth et retourne l'URL d'autorisation LinkedIn.

**Réponse** :
```json
{
    "auth_url": "https://www.linkedin.com/oauth/v2/authorization?...",
    "state": "random-csrf-token"
}
```

#### GET `/api/linkedin/callback`

Callback OAuth après authentification LinkedIn. Gère l'échange du code contre un token.

**Paramètres** :
- `code` : code d'autorisation
- `state` : token CSRF

**Réponse** : Redirection vers le frontend avec paramètre `?linkedin_auth=success`

#### GET `/api/linkedin/profile`

Récupère les données du profil LinkedIn.

**Headers** :
- `Authorization: Bearer {access_token}` (optionnel si le token est en session)

**Réponse** :
```json
{
    "profile": {
        "first_name": "John",
        "last_name": "Doe",
        "headline": "Software Engineer",
        "email": "john@example.com",
        ...
    },
    "positions": [...],
    "education": [...],
    "skills": [...],
    "languages": [],
    "certifications": []
}
```

#### POST `/api/linkedin/logout`

Déconnecte l'utilisateur et nettoie la session.

---

## Architecture

### Structure des fichiers

```
cv-generator/
├── backend/
│   ├── app.py                 # Routes Flask (avec routes LinkedIn)
│   ├── linkedin_api.py        # Service LinkedIn API
│   ├── linkedin_parser.py     # Parser CSV (toujours utilisable)
│   └── cv_generator.py        # Générateur de PDF
│
├── frontend/
│   └── js/
│       └── services/
│           └── api/
│               ├── linkedinService.js  # Service frontend LinkedIn
│               ├── parseService.js     # Service parsing CSV
│               └── pdfService.js       # Service génération PDF
│
└── .env                       # Configuration (ne pas committer!)
```

### Flux d'authentification OAuth 2.0

```
┌─────────┐                ┌──────────┐                ┌──────────┐
│ Frontend│                │  Backend │                │ LinkedIn │
└────┬────┘                └────┬─────┘                └────┬─────┘
     │                          │                           │
     │ 1. Clic "Se connecter"   │                           │
     ├─────────────────────────>│                           │
     │                          │                           │
     │ 2. Retourne auth_url     │                           │
     │<─────────────────────────┤                           │
     │                          │                           │
     │ 3. Redirection vers LinkedIn                         │
     ├──────────────────────────────────────────────────────>│
     │                          │                           │
     │ 4. Utilisateur se connecte et autorise               │
     │                          │                           │
     │ 5. Callback avec code    │                           │
     │<──────────────────────────────────────────────────────┤
     │                          │                           │
     │ 6. Envoie code au backend│                           │
     ├─────────────────────────>│                           │
     │                          │ 7. Échange code → token   │
     │                          ├──────────────────────────>│
     │                          │                           │
     │                          │ 8. Retourne access_token  │
     │                          │<──────────────────────────┤
     │                          │                           │
     │ 9. Redirection succès    │                           │
     │<─────────────────────────┤                           │
     │                          │                           │
     │ 10. Récupère profil      │                           │
     ├─────────────────────────>│                           │
     │                          │ 11. Appel API avec token  │
     │                          ├──────────────────────────>│
     │                          │                           │
     │                          │ 12. Retourne données      │
     │                          │<──────────────────────────┤
     │                          │                           │
     │ 13. Retourne données formatées                       │
     │<─────────────────────────┤                           │
     │                          │                           │
```

### Format des données

Le service LinkedIn API retourne les données dans le **même format** que le parser CSV, garantissant une compatibilité totale avec le reste de l'application.

**Exemple de réponse** :

```json
{
    "profile": {
        "first_name": "John",
        "last_name": "Doe",
        "headline": "Senior Software Engineer",
        "summary": "Experienced developer...",
        "email": "john@example.com",
        "phone": "+33 6 00 00 00 00",
        "address": "Paris, France",
        ...
    },
    "positions": [
        {
            "company": "Tech Corp",
            "title": "Senior Engineer",
            "description": "Leading development...",
            "started_on": "2020-01",
            "finished_on": "Présent",
            "duration": "2020-01 - Présent"
        }
    ],
    "education": [...],
    "skills": ["JavaScript", "Python", "React"],
    "languages": [],
    "certifications": []
}
```

---

## Limitations

### Restrictions de l'API LinkedIn

LinkedIn a des restrictions importantes sur l'accès aux données via leur API :

1. **Permissions limitées** : Par défaut, seules les permissions de base sont disponibles
   - Profil de base (nom, photo, headline)
   - Adresse email

2. **Données étendues** : Pour accéder aux positions, éducation, compétences, etc., vous devez :
   - Être approuvé pour le produit **"Marketing Developer Platform"**
   - Ou utiliser l'API avec des permissions d'entreprise

3. **Processus d'approbation** : LinkedIn examine les demandes d'accès aux données étendues
   - Peut prendre plusieurs jours
   - Nécessite de justifier l'utilisation des données

### Solutions alternatives

Si vous ne pouvez pas obtenir les permissions étendues :

1. **Mode hybride** :
   - Récupérer les données de base via l'API
   - Permettre l'upload de CSV pour les données complémentaires

2. **Continuer avec les CSV** :
   - Le système CSV existant reste pleinement fonctionnel
   - Les deux méthodes peuvent coexister

---

## Dépannage

### Erreur : "LinkedIn credentials not configured"

**Cause** : Les variables d'environnement LinkedIn ne sont pas définies.

**Solution** :
1. Vérifiez que le fichier `.env` existe
2. Vérifiez que `LINKEDIN_CLIENT_ID` et `LINKEDIN_CLIENT_SECRET` sont renseignés
3. Redémarrez le serveur Flask

```bash
python start.py
```

### Erreur : "Invalid redirect URI"

**Cause** : L'URL de callback n'est pas autorisée dans l'application LinkedIn.

**Solution** :
1. Allez dans votre application LinkedIn (https://www.linkedin.com/developers/apps)
2. Onglet "Auth" → "Redirect URLs"
3. Ajoutez : `http://localhost:5000/api/linkedin/callback`
4. Cliquez sur "Update"

### Erreur : "Not authenticated"

**Cause** : Le token d'accès a expiré ou la session a été perdue.

**Solution** :
1. Reconnectez-vous avec LinkedIn
2. Vérifiez que les cookies sont autorisés
3. Vérifiez que `supports_credentials: True` est défini dans CORS

### Erreur : "Could not fetch positions/education/skills"

**Cause** : Votre application n'a pas les permissions nécessaires.

**Solution** :
1. Vérifiez les permissions dans votre application LinkedIn
2. Demandez l'accès au produit "Marketing Developer Platform"
3. Utilisez le mode hybride (API + CSV) en attendant l'approbation

### Problèmes CORS

**Symptôme** : Erreurs CORS dans la console du navigateur.

**Solution** :
1. Vérifiez que `supports_credentials: True` dans la config CORS
2. Utilisez `credentials: 'include'` dans les appels fetch
3. Vérifiez que le frontend et backend sont sur des ports autorisés

---

## Sécurité

### Bonnes pratiques

1. **Ne jamais committer le fichier `.env`** :
   ```bash
   # Vérifiez qu'il est dans .gitignore
   echo ".env" >> .gitignore
   ```

2. **Générer une clé secrète forte** :
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **Utiliser HTTPS en production** :
   - Modifier `LINKEDIN_REDIRECT_URI` pour utiliser `https://`
   - Configurer un certificat SSL

4. **Valider le state CSRF** :
   - Le code vérifie automatiquement le token state
   - Ne jamais désactiver cette vérification

5. **Expiration des tokens** :
   - Les tokens LinkedIn expirent après 60 jours
   - Implémenter un refresh token si nécessaire

---

## Support

Pour toute question ou problème :

1. Consultez la [documentation LinkedIn API](https://docs.microsoft.com/en-us/linkedin/)
2. Vérifiez les logs du serveur Flask
3. Consultez la console du navigateur pour les erreurs frontend
4. Ouvrez une issue sur le repository GitHub du projet

---

## Prochaines étapes

Fonctionnalités à venir :

- [ ] Refresh token automatique
- [ ] Cache des données de profil
- [ ] Support de l'import de photo de profil LinkedIn
- [ ] Export des données en CSV depuis l'API
- [ ] Interface utilisateur pour basculer entre CSV et API

---

## Références

- [LinkedIn OAuth 2.0 Documentation](https://docs.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [LinkedIn API Reference](https://docs.microsoft.com/en-us/linkedin/shared/references/)
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749)
