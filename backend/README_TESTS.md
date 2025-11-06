# Tests unitaires du générateur de CV

Ce fichier contient des tests automatisés pour valider le comportement du générateur de CV, notamment :
- Le nettoyage des emojis
- La normalisation des apostrophes typographiques
- Le formatage des descriptions avec bullet points

## 🧪 Exécution des tests

### Avec pytest (recommandé)

```bash
cd backend
python3 -m pytest test_cv_generator.py -v
```

### Avec unittest

```bash
cd backend
python3 test_cv_generator.py
```

## 📋 Couverture des tests

### 1. **TestEmojiCleaning** (4 tests)
- ✅ Remplacement des emojis par des sauts de ligne
- ✅ Création de listes à partir d'emojis multiples
- ✅ Suppression des emojis courants (🎉🤖💻🚀🔥💡⚡✨🌟✅)
- ✅ Suppression des caractères bullet Unicode (•‣◦⁃∙)

### 2. **TestApostropheNormalization** (4 tests)
- ✅ Normalisation de l'apostrophe droite (') → (')
- ✅ Normalisation de l'apostrophe gauche (') → (')
- ✅ Normalisation de multiples apostrophes dans un texte
- ✅ Vérification que les apostrophes ne créent pas de sauts de ligne

### 3. **TestDescriptionFormatting** (6 tests)
- ✅ Paragraphe simple sans bullets
- ✅ Emojis créant automatiquement des bullets
- ✅ Préservation des bullets natifs (•)
- ✅ Conversion des marqueurs 'n' en sauts de ligne
- ✅ Conversion des marqueurs 'nn' en paragraphes
- ✅ Conversion des tirets (-) et astérisques (*) en bullets

### 4. **TestComplexScenarios** (4 tests)
- ✅ Emojis et apostrophes fonctionnant ensemble
- ✅ Mix de bullets (emojis + natifs)
- ✅ Description LinkedIn réelle complexe
- ✅ Cas reporté : "Réalisation d'une étude sur l'API"

### 5. **TestEdgeCases** (5 tests)
- ✅ Chaîne vide
- ✅ Valeur None
- ✅ Texte avec seulement des espaces
- ✅ Ligne très longue (>250 chars) sans bullet
- ✅ Préservation des caractères spéciaux français (àéèêçô)

## 📊 Résultats

```
============================== 23 passed ==============================
```

**Tous les tests passent avec succès** ✅

## 🔍 Exemples de cas testés

### Cas 1 : Apostrophes typographiques
```python
Input:  "Réalisation d'une étude sur l'API d'Hubspot"  # Avec ' (U+2019)
Output: "Réalisation d'une étude sur l'API d'Hubspot"  # Avec ' (U+0027)
```

### Cas 2 : Emojis comme séparateurs
```python
Input:  "🎉 Expert en IA 🤖 Développement Python 💻 Machine Learning"
Output: • Expert en IA
        • Développement Python
        • Machine Learning
```

### Cas 3 : Mix emojis + apostrophes
```python
Input:  "🚀 Réalisation d'une étude 🔥 Optimisation de l'API"
Output: • Réalisation d'une étude
        • Optimisation de l'API
```

### Cas 4 : Description LinkedIn réelle
```python
Input:  "n Développement d'un système • Conception et déploiement nn Optimisation"
Output: • Développement d'un système
        • Conception et déploiement

        • Optimisation
```

## 🐛 Bugs couverts

1. **Bug des apostrophes** (bbfcc5d)
   - Problème : Les apostrophes typographiques (') créaient des sauts de ligne
   - Solution : Normalisation en apostrophes ASCII avant nettoyage
   - Tests : `TestApostropheNormalization` (4 tests)

2. **Bug du nettoyage des emojis** (cb09c1e)
   - Problème : Fonction définie mais jamais appelée
   - Solution : Appel dans `__init__()`
   - Tests : `TestEmojiCleaning` (4 tests)

3. **Comportement des emojis** (bca783e)
   - Amélioration : Emojis comme séparateurs de bullets
   - Tests : `TestDescriptionFormatting` + `TestComplexScenarios` (10 tests)

## 🚀 Ajout de nouveaux tests

Pour ajouter un nouveau test :

```python
def test_mon_nouveau_cas(self):
    """Description du test"""
    data = {
        'profile': {'summary': 'Mon texte de test'},
        'positions': []
    }
    cv = CVGenerator(data)
    formatted = cv._format_description(cv.data['profile']['summary'])

    # Assertions
    self.assertIn('résultat attendu', formatted)
```

## 📝 Maintenance

Les tests doivent être exécutés :
- ✅ Avant chaque commit modifiant `cv_generator.py`
- ✅ Avant chaque merge dans `main`
- ✅ Lors de l'ajout de nouvelles fonctionnalités de formatage

## 🔗 Fichiers liés

- `cv_generator.py` : Code source du générateur
- `test_cv_generator.py` : Tests unitaires
- `linkedin_parser.py` : Parser des exports LinkedIn
