# Guide : Gestion automatique des missions de consultant

## 🎯 Comment ça fonctionne

Le système détecte **automatiquement** les positions dupliquées de consultant et les fusionne en structure hiérarchique.

### Critères de détection

Le système fusionne 2 positions si :
1. **Même entreprise** (ex: "Zenika" = "Zenika")
2. **Dates qui se chevauchent** (ex: Jan-Oct 2020 ∩ Mar-Aug 2020)
3. **Descriptions différentes** (l'une courte/vide, l'autre détaillée)

## 📝 Format des données LinkedIn

### Cas 1 : Format recommandé (détecté automatiquement)

Dans votre CSV LinkedIn `Positions.csv` :

```csv
Company Name,Title,Description,Location,Started On,Finished On
Zenika,Consultant Développeur,,Paris,2020-01,2020-12
Zenika,Software Engineer @ Aircall,"[description détaillée]",Remote,2020-03,2020-08
Zenika,Tech Lead @ BNP Paribas,"[description détaillée]",Paris,2020-09,2020-12
```

**Résultat dans le CV :**
```
ZENIKA
Consultant Développeur
Janvier 2020 - Décembre 2020

  → Mission chez Aircall
    Software Engineer @ Aircall
    Mars 2020 - Août 2020
    [description]

  → Mission chez BNP Paribas
    Tech Lead @ BNP Paribas
    Septembre 2020 - Décembre 2020
    [description]
```

---

## 🔍 Patterns de détection du client

Le système extrait automatiquement le nom du client selon ces patterns :

### Pattern 1 : `@ ClientName`
```
Software Engineer @ Aircall
Lead Developer @ Google
Consultant @ Microsoft
```
→ Extrait : **Aircall**, **Google**, **Microsoft**

### Pattern 2 : `for ClientName`
```
Developer for Apple
Consultant for Amazon
Tech Lead for Netflix
```
→ Extrait : **Apple**, **Amazon**, **Netflix**

### Pattern 3 : `chez ClientName`
```
Développeur chez Orange
Consultant chez SFR
Tech Lead chez Total
```
→ Extrait : **Orange**, **SFR**, **Total**

---

## ✅ Exemples fonctionnant automatiquement

### Exemple 1 : Plusieurs clients pour une ESN

**CSV :**
```csv
Company Name,Title,Description,Started On,Finished On
Accenture,Senior Consultant,,2019-01,2021-12
Accenture,Java Developer @ Société Générale,"Migration système bancaire",2019-01,2019-06
Accenture,Tech Lead @ Carrefour,"Refonte e-commerce",2019-07,2020-03
Accenture,Architect for Orange,"Architecture cloud",2020-04,2021-12
```

**Résultat CV :**
```
ACCENTURE
Senior Consultant
Janvier 2019 - Décembre 2021

  → Mission chez Société Générale
    Java Developer
    Janvier 2019 - Juin 2019
    Migration système bancaire

  → Mission chez Carrefour
    Tech Lead
    Juillet 2019 - Mars 2020
    Refonte e-commerce

  → Mission chez Orange
    Architect
    Avril 2020 - Décembre 2021
    Architecture cloud
```

---

### Exemple 2 : Freelance avec plusieurs clients

**CSV :**
```csv
Company Name,Title,Description,Started On,Finished On
Freelance,Développeur Full Stack,,2020-01,2023-12
Freelance,Frontend Developer for Spotify,"App React",2020-01,2020-06
Freelance,Backend Developer @ Netflix,"API Node.js",2020-07,2021-03
Freelance,DevOps chez Deezer,"CI/CD Pipeline",2021-04,2023-12
```

**Résultat CV :**
```
FREELANCE
Développeur Full Stack
Janvier 2020 - Décembre 2023

  → Mission chez Spotify
    Frontend Developer
    Janvier 2020 - Juin 2020
    App React

  → Mission chez Netflix
    Backend Developer
    Juillet 2020 - Mars 2021
    API Node.js

  → Mission chez Deezer
    DevOps
    Avril 2021 - Décembre 2023
    CI/CD Pipeline
```

---

## 🚫 Cas NON détectés (pas fusionnés)

### Cas 1 : Entreprises différentes
```csv
Company Name,Title,Started On,Finished On
Google,Software Engineer,2020-01,2020-12
Microsoft,Developer,2020-06,2021-01
```
→ **2 positions séparées** (pas de fusion, entreprises différentes)

### Cas 2 : Dates qui ne se chevauchent pas
```csv
Company Name,Title,Started On,Finished On
Zenika,Consultant,2019-01,2019-12
Zenika,Developer @ Client,2020-01,2020-12
```
→ **2 positions séparées** (pas de chevauchement de dates)

### Cas 3 : Descriptions identiques (même longueur)
```csv
Company Name,Title,Description,Started On,Finished On
Zenika,Consultant,"Description A (100 chars)",2020-01,2020-12
Zenika,Developer,"Description B (100 chars)",2020-06,2020-12
```
→ **2 positions séparées** (descriptions de même longueur, pas de position "principale")

---

## 🔧 Personnalisation

### Ajouter d'autres patterns de client

Si vous utilisez d'autres formats, vous pouvez les ajouter dans `backend/linkedin_parser.py`, ligne 320 :

```python
patterns = [
    r'@\s*([A-Z][A-Za-z0-9\s&.-]+?)(?:\s*[-•,]|$)',  # @ Aircall
    r'for\s+([A-Z][A-Za-z0-9\s&.-]+?)(?:\s*[-•,]|$)',  # for Aircall
    r'chez\s+([A-Z][A-Za-z0-9\s&.-]+?)(?:\s*[-•,]|$)',  # chez Aircall
    # Ajoutez vos patterns ici :
    r'at\s+([A-Z][A-Za-z0-9\s&.-]+?)(?:\s*[-•,]|$)',  # at Aircall
    r'pour\s+([A-Z][A-Za-z0-9\s&.-]+?)(?:\s*[-•,]|$)',  # pour Aircall
]
```

---

## 🧪 Comment tester

### Test rapide avec Python

```python
from backend.linkedin_parser import LinkedInParser

# Créer un fichier Positions.csv de test
positions_csv = """Company Name,Title,Description,Started On,Finished On
VotreESN,Consultant,,2020-01,2020-12
VotreESN,Developer @ VotreClient,"Description longue",2020-03,2020-08
"""

# Parser et afficher
parser = LinkedInParser(['Positions.csv'])
data = parser.parse()

# Vérifier la structure
for pos in data['positions']:
    print(f"Entreprise: {pos['company']}")
    if pos.get('missions'):
        print(f"  → {len(pos['missions'])} mission(s)")
        for mission in pos['missions']:
            print(f"    - {mission['client']}")
```

---

## 📊 Résumé

| Situation | Résultat |
|-----------|----------|
| 2+ positions même ESN + dates chevauchantes | ✅ Fusionné en hiérarchie |
| Pattern `@ Client` dans le titre | ✅ Client extrait automatiquement |
| Pattern `for Client` dans le titre | ✅ Client extrait automatiquement |
| Pattern `chez Client` dans le titre | ✅ Client extrait automatiquement |
| Entreprises différentes | ❌ Pas de fusion |
| Dates sans chevauchement | ❌ Pas de fusion |
| Pas de pattern client dans titre | ⚠️ Mission affichée comme "Client" (générique) |

---

## 💡 Conseils

### 1. Structurer vos données LinkedIn

Pour chaque mission de consultant, créez 2 lignes :
1. **Ligne générique** : `Nom ESN, Votre titre, [pas de description]`
2. **Ligne mission** : `Nom ESN, Titre spécifique @ Client, [description détaillée]`

### 2. Utiliser les patterns

Dans le titre de la mission, utilisez toujours :
- `Titre @ NomClient` (recommandé)
- `Titre for NomClient`
- `Titre chez NomClient`

### 3. Vérifier les dates

Assurez-vous que la période de la mission est **incluse** dans la période globale de l'ESN.

Exemple correct :
```
ESN : 2020-01 → 2020-12
Mission : 2020-03 → 2020-08  ✅ (incluse dans ESN)
```

Exemple incorrect :
```
ESN : 2020-01 → 2020-06
Mission : 2020-07 → 2020-12  ❌ (pas de chevauchement)
```

---

## 🆘 Dépannage

### Problème : Mes missions ne se fusionnent pas

**Vérifiez :**
1. ✅ Le nom de l'entreprise est **exactement identique** (majuscules/minuscules)
2. ✅ Les dates se **chevauchent**
3. ✅ Une position a une description **plus longue** que l'autre

### Problème : Le client n'est pas extrait

**Vérifiez :**
1. ✅ Le pattern utilisé (`@`, `for`, `chez`)
2. ✅ Le nom du client commence par une **majuscule**
3. ✅ Le format : `Titre @ Client` (avec espace avant et après @)

---

## 🎓 Exemple complet

Voici un exemple complet pour une carrière de consultant :

```csv
Company Name,Title,Description,Location,Started On,Finished On
Sopra Steria,Consultant Développeur,,Paris,2018-01,2021-12
Sopra Steria,Java Developer @ Air France,"Migration système réservation",Paris,2018-01,2018-09
Sopra Steria,Tech Lead for SNCF,"Refonte application mobile",Lyon,2018-10,2019-06
Sopra Steria,Solution Architect chez Renault,"Architecture microservices",Paris,2019-07,2021-12
Capgemini,Senior Consultant,,Paris,2022-01,Present
Capgemini,Cloud Architect @ Total,"Migration Azure",La Défense,2022-01,2022-08
Capgemini,DevOps Lead for Orange,"Infrastructure Kubernetes",Paris,2022-09,Present
```

Ce CSV générera automatiquement un CV avec 2 entreprises et leurs missions respectives ! ✨
