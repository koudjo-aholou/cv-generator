# Tests unitaires pour le système de missions consultant

Ce fichier contient des tests automatisés pour valider le système de fusion automatique des missions de consultant.

## 🧪 Exécution des tests

### Avec pytest (recommandé)

```bash
python3 -m pytest tests/business/test_consultant_missions.py -v
```

### Avec unittest

```bash
python3 -m unittest tests.business.test_consultant_missions -v
```

## 📋 Couverture des tests (50 tests)

### 1. **TestClientNameExtraction** (8 tests)

Tests pour l'extraction automatique du nom du client depuis le titre du poste.

| Test | Description |
|------|-------------|
| `test_extract_client_with_at_symbol` | Pattern `@` : "Engineer @ Aircall" → "Aircall" |
| `test_extract_client_with_for_keyword` | Pattern `for` : "Developer for Apple" → "Apple" |
| `test_extract_client_with_chez_keyword` | Pattern `chez` : "Consultant chez Orange" → "Orange" |
| `test_extract_client_with_french_accents` | Noms avec accents : "@ Société Générale" → "Société Générale" |
| `test_extract_client_with_special_characters` | Caractères spéciaux : apostrophes, espaces composés |
| `test_client_name_with_ampersand` | Noms avec & : "@ Procter & Gamble" → "Procter & Gamble" |
| `test_no_client_in_title` | Pas de pattern → retourne `None` |
| `test_empty_or_none_title` | Titre vide/None → retourne `None` |

**Patterns supportés :**
- `@ ClientName` (ex: Software Engineer @ Aircall)
- `for ClientName` (ex: Developer for Google)
- `chez ClientName` (ex: Consultant chez Orange)

**Caractères supportés :**
- ✅ Accents français (À-ÿ)
- ✅ Apostrophes (L'Oréal, D'Artagnan)
- ✅ Esperluette (&)
- ✅ Espaces composés (BNP Paribas, Crédit Agricole)
- ✅ Points (Air France-K.L.M.)

---

### 2. **TestDatesOverlap** (8 tests)

Tests pour la détection automatique de chevauchement de dates entre positions.

| Test | Description | Exemple | Résultat |
|------|-------------|---------|----------|
| `test_dates_completely_overlap` | Dates complètement imbriquées | Jan-Dec 2020 ∩ Mar-Aug 2020 | ✅ Chevauche |
| `test_dates_partially_overlap` | Dates partiellement qui se croisent | Jan-Jun 2020 ∩ Apr-Oct 2020 | ✅ Chevauche |
| `test_dates_no_overlap` | Dates totalement séparées | Jan-Dec 2019 ∩ Jan-Dec 2020 | ❌ Ne chevauche pas |
| `test_dates_touch_exactly` | Dates qui se touchent (même mois) | Jan-Dec 2019 ∩ Dec 2019-Dec 2020 | ✅ Chevauche |
| `test_one_position_still_active` | Position toujours active (pas de fin) | Jan 2020-Present ∩ Jun 2020-Present | ✅ Chevauche |
| `test_missing_start_date` | Dates manquantes | (vide) ∩ Jan-Dec 2020 | ❌ Ne chevauche pas |
| `test_linkedin_date_format_overlap` | **Format LinkedIn "Jan 2020"** | Jan-Oct 2020 ∩ Mar-Aug 2020 | ✅ Chevauche |
| `test_linkedin_date_format_no_overlap` | **Format LinkedIn sans overlap** | Jan-Mar 2020 ∩ Apr-Dec 2020 | ❌ Ne chevauche pas |

**Logique :**
- ✅ Support format LinkedIn : "Jan 2020" → "2020-01"
- ✅ Support format ISO : "2020-01" (inchangé)
- Position active (pas de `finished_on`) = date future (9999-12)
- Dates manquantes = pas de chevauchement

---

### 3. **TestLinkedInDateConversion** (3 tests)

Tests pour la conversion des formats de dates LinkedIn vers format comparable.

| Test | Description | Input | Output |
|------|-------------|-------|--------|
| `test_convert_linkedin_format_to_comparable` | Conversion des 12 mois | "Jan 2020" ... "Dec 2020" | "2020-01" ... "2020-12" |
| `test_convert_iso_format_unchanged` | Format ISO reste inchangé | "2020-01", "2020-12" | "2020-01", "2020-12" |
| `test_convert_empty_date` | Dates vides/None | `""`, `None` | `None` |

**Mapping des mois :**
```python
Jan → 01, Feb → 02, Mar → 03, Apr → 04, May → 05, Jun → 06
Jul → 07, Aug → 08, Sep → 09, Oct → 10, Nov → 11, Dec → 12
```

**Comportement :**
- LinkedIn "Jan 2020" → Comparable "2020-01" ✅
- ISO "2020-01" → Inchangé "2020-01" ✅
- Date vide → `None` ✅

---

### 4. **TestConsultantPositionsMerging** (7 tests)

Tests pour la fusion automatique des positions consultant en structure hiérarchique.

| Test | Description | Input | Output |
|------|-------------|-------|--------|
| `test_simple_merge_two_positions` | Fusion simple 2 positions | Zenika × 2 (chevauchement) | 1 position + 1 mission |
| `test_merge_multiple_missions` | Plusieurs missions pour une ESN | Accenture × 4 (3 missions) | 1 position + 3 missions |
| `test_no_merge_different_companies` | Pas de fusion si entreprises ≠ | Zenika + Accenture | 2 positions séparées |
| `test_no_merge_no_overlap` | Pas de fusion si dates disjointes | Zenika 2019 + Zenika 2020 | 2 positions séparées |
| `test_merge_keeps_longer_description` | Garde la description longue | Courte + Longue | Mission = longue |
| `test_merge_with_linkedin_date_format` | **Fusion avec format LinkedIn** | "Jan 2020" + "Mar 2020" | ✅ Fusionne correctement |
| `test_multiple_companies_with_missions` | Plusieurs ESN avec missions | 3 ESN × missions | 3 positions + 4 missions |

**Critères de fusion :**
1. ✅ **Même entreprise** (nom identique)
2. ✅ **Dates qui se chevauchent**
3. ✅ **Descriptions différentes** (une courte = générique, une longue = mission)

**Résultat :**
```
Position principale (description courte/vide)
└── missions[] (descriptions longues/détaillées)
    ├── Mission 1 (client extrait du titre)
    ├── Mission 2
    └── Mission 3
```

---

### 5. **TestConsultantMissionsEdgeCases** (4 tests)

Tests pour les cas limites et scénarios edge.

| Test | Description | Comportement |
|------|-------------|--------------|
| `test_empty_positions_list` | Liste vide | Ne crash pas, retourne [] |
| `test_single_position_no_merge` | Une seule position | Pas de fusion, pas de missions |
| `test_mission_without_client_pattern` | Mission sans pattern @ / for / chez | Client = "Client" (générique) |
| `test_three_positions_same_company` | 3 positions même ESN | 1 principale + 2 missions |

---

---

### 6. **TestAdvancedDateEdgeCases** (5 tests)

Tests avancés pour les edge cases de dates.

| Test | Description |
|------|-------------|
| `test_same_start_and_end_date` | Position d'un seul mois |
| `test_very_old_positions` | Positions années 1990 |
| `test_future_positions` | Positions futures (2025+) |
| `test_all_positions_active_present` | Plusieurs positions actives simultanément |
| `test_consecutive_months_no_gap` | Mois consécutifs (Jan-Feb, Feb-Mar) |

---

### 7. **TestCompanyNameEdgeCases** (3 tests)

Tests pour les noms d'entreprises complexes.

| Test | Description |
|------|-------------|
| `test_company_with_multiple_spaces` | Espaces multiples dans le nom |
| `test_company_with_special_chars` | Caractères spéciaux (L'Oréal S.A.) |
| `test_company_name_empty_or_whitespace` | Noms vides/whitespace |

---

### 8. **TestDescriptionEdgeCases** (3 tests)

Tests pour les descriptions de positions.

| Test | Description |
|------|-------------|
| `test_descriptions_equal_length` | Descriptions de longueur égale |
| `test_both_descriptions_empty` | Les deux descriptions vides |
| `test_very_long_description` | Description >10000 caractères |

---

### 9. **TestMultipleOverlappingPositions** (2 tests)

Tests pour plusieurs positions qui se chevauchent.

| Test | Description |
|------|-------------|
| `test_five_positions_same_company` | 5 positions même ESN (1 + 4 missions) |
| `test_cascading_overlaps` | Chevauchements en cascade (non-transitif) |

---

### 10. **TestClientNameAdvancedPatterns** (7 tests)

Tests avancés pour l'extraction de noms de clients.

| Test | Description | Comportement |
|------|-------------|--------------|
| `test_multiple_patterns_in_title` | Plusieurs keywords | Extrait jusqu'au séparateur |
| `test_pattern_at_end_of_title` | Pattern en fin de titre | ✅ Supporte |
| `test_pattern_with_lowercase` | Minuscules (airbnb, stripe) | ✅ Maintenant supporté |
| `test_client_name_with_numbers` | Noms avec chiffres | ✅ Orange 5G, ✅ 3M France, ✅ 42 |
| `test_client_name_very_long` | Noms très longs (>30 chars) | ✅ Supporte |
| `test_special_bullet_separators` | Séparateurs •, -, , | ✅ S'arrête correctement |
| `test_potential_false_positives` | Faux positifs (home, remote) | ⚠️ Acceptés (rares) |

---

## 📊 Résultats

```
============================== 50 passed ==============================
✅ TestClientNameExtraction: 8/8 tests passés
✅ TestDatesOverlap: 8/8 tests passés
✅ TestLinkedInDateConversion: 3/3 tests passés
✅ TestConsultantPositionsMerging: 7/7 tests passés
✅ TestConsultantMissionsEdgeCases: 4/4 tests passés
✅ TestAdvancedDateEdgeCases: 5/5 tests passés
✅ TestCompanyNameEdgeCases: 3/3 tests passés
✅ TestDescriptionEdgeCases: 3/3 tests passés
✅ TestMultipleOverlappingPositions: 2/2 tests passés
✅ TestClientNameAdvancedPatterns: 7/7 tests passés (1 nouveau)
```

**Note importante:** Le support des minuscules peut créer des faux positifs rares comme "@ home" ou "@ remote". Ces cas sont documentés et acceptés car le support des noms en minuscules (airbnb, stripe, etc.) est plus important.

---

## 🔍 Exemples de cas testés

### Cas 1 : Fusion simple (2 positions → 1)

**Input CSV :**
```csv
Zenika,Consultant Développeur,,Paris,Jan 2020,Oct 2020
Zenika,Software Engineer @ Aircall,"Description longue",Remote,Mar 2020,Aug 2020
```

**Note:** Le format de dates LinkedIn réel ("Jan 2020", "Mar 2020") est maintenant correctement supporté!

**Output :**
```python
{
  'company': 'Zenika',
  'title': 'Consultant Développeur',
  'started_on': 'Jan 2020',
  'finished_on': 'Oct 2020',
  'missions': [{
    'client': 'Aircall',
    'title': 'Software Engineer @ Aircall',
    'started_on': 'Mar 2020',
    'finished_on': 'Aug 2020',
    'description': 'Description longue'
  }]
}
```

---

### Cas 2 : Plusieurs missions (4 positions → 1 + 3 missions)

**Input CSV :**
```csv
Accenture,Senior Consultant,,2019-01,2021-12
Accenture,Java Developer @ Société Générale,"Mission 1",2019-01,2019-06
Accenture,Tech Lead for Carrefour,"Mission 2",2019-07,2020-03
Accenture,Architect chez Orange,"Mission 3",2020-04,2021-12
```

**Output :**
- 1 position Accenture
- 3 missions imbriquées (Société Générale, Carrefour, Orange)

---

### Cas 3 : Pas de fusion (entreprises différentes)

**Input CSV :**
```csv
Zenika,Consultant,,2020-01,2020-12
Accenture,Developer @ Client,"Description",2020-03,2020-08
```

**Output :**
- 2 positions séparées (pas de fusion car entreprises ≠)

---

### Cas 4 : Extraction avec accents français

**Tests :**
```python
"Java Developer for Société Générale"  → ✅ "Société Générale"
"Tech Lead @ Crédit Agricole"          → ✅ "Crédit Agricole"
"Consultant chez L'Oréal"              → ✅ "L'Oréal"
"Engineer @ BNP Paribas"               → ✅ "BNP Paribas"
```

---

## 🚀 Ajout de nouveaux tests

Pour ajouter un test :

```python
def test_mon_nouveau_cas(self):
    """Description du test"""
    # Créer CSV de test
    temp_dir = tempfile.mkdtemp()
    positions_csv = """Company Name,Title,Description,Started On,Finished On
MonESN,Consultant,,2020-01,2020-12
MonESN,Developer @ MonClient,"Description",2020-03,2020-08
"""

    # Parser
    positions_path = os.path.join(temp_dir, 'Positions.csv')
    with open(positions_path, 'w') as f:
        f.write(positions_csv)

    parser = LinkedInParser([positions_path])
    data = parser.parse()

    # Assertions
    self.assertEqual(len(data['positions']), 1)
    self.assertEqual(len(data['positions'][0]['missions']), 1)

    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
```

---

## 📝 Maintenance

Les tests doivent être exécutés :
- ✅ Avant chaque commit modifiant `linkedin_parser.py`
- ✅ Avant chaque merge dans `main`
- ✅ Lors de l'ajout de nouveaux patterns de client
- ✅ Lors de modifications de la logique de fusion

---

## 🔗 Fichiers liés

- `linkedin_parser.py` : Code source du parser
- `tests/business/test_consultant_missions.py` : Tests unitaires
- `GUIDE_MISSIONS_CONSULTANT.md` : Guide utilisateur complet
- `tests/business/test_cv_generator.py` : Tests pour le générateur de CV
