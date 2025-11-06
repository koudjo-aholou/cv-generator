# 📁 Dossier my_data

Ce dossier est destiné à contenir vos **fichiers CSV personnels** exportés depuis LinkedIn.

## 🔒 Confidentialité

Tous les fichiers placés dans ce dossier (sauf ce README) sont **automatiquement ignorés par Git**.
Vous pouvez donc y placer vos données LinkedIn en toute sécurité sans risque de les commiter accidentellement.

## 📥 Comment utiliser ce dossier

1. **Exportez vos données LinkedIn** :
   - Allez sur LinkedIn → *Paramètres et confidentialité*
   - Cliquez sur *Confidentialité des données*
   - Sélectionnez *Obtenir une copie de vos données*
   - Téléchargez et extrayez le fichier ZIP

2. **Copiez les fichiers CSV ici** :
   ```bash
   cp /chemin/vers/export/linkedin/*.csv my_data/
   ```

3. **Testez l'application** :
   - Les fichiers resteront privés et ne seront jamais commités
   - Vous pouvez les utiliser pour tester le générateur de CV

## 📄 Fichiers CSV attendus

### Requis :
- `Profile.csv` - Informations de profil
- `Positions.csv` - Expériences professionnelles
- `Education.csv` - Formation

### Optionnels :
- `Skills.csv` - Compétences
- `Languages.csv` - Langues
- `Certifications.csv` - Certifications
- `Email Addresses.csv` - Adresses email
- `PhoneNumbers.csv` - Numéros de téléphone
- `Whatsapp Phone Numbers.csv` - Numéros WhatsApp

## ⚠️ Important

- **NE PAS** committer vos fichiers CSV personnels
- Ce dossier est déjà configuré dans `.gitignore`
- Vos données restent 100% locales et privées
