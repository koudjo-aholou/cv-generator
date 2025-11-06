"""
Tests unitaires pour le système de fusion des missions de consultant

Ces tests valident :
- L'extraction automatique des noms de clients depuis les titres
- La détection des chevauchements de dates
- La fusion automatique des positions dupliquées en structure hiérarchique
"""

import unittest
from linkedin_parser import LinkedInParser
from datetime import datetime
import tempfile
import os


class TestClientNameExtraction(unittest.TestCase):
    """Tests pour l'extraction du nom du client depuis le titre"""

    def setUp(self):
        self.parser = LinkedInParser([])

    def test_extract_client_with_at_symbol(self):
        """Pattern @ : doit extraire le nom du client"""
        test_cases = [
            ("Software Engineer @ Aircall", "Aircall"),
            ("Tech Lead @ Google", "Google"),
            ("Developer @ Microsoft", "Microsoft"),
            ("Consultant @ IBM", "IBM"),
        ]
        for title, expected_client in test_cases:
            with self.subTest(title=title):
                client = self.parser._extract_client_name(title)
                self.assertEqual(client, expected_client)

    def test_extract_client_with_for_keyword(self):
        """Pattern 'for' : doit extraire le nom du client"""
        test_cases = [
            ("Developer for Apple", "Apple"),
            ("Consultant for Amazon", "Amazon"),
            ("Tech Lead for Netflix", "Netflix"),
            ("Engineer for Tesla", "Tesla"),
        ]
        for title, expected_client in test_cases:
            with self.subTest(title=title):
                client = self.parser._extract_client_name(title)
                self.assertEqual(client, expected_client)

    def test_extract_client_with_chez_keyword(self):
        """Pattern 'chez' : doit extraire le nom du client"""
        test_cases = [
            ("Développeur chez Orange", "Orange"),
            ("Consultant chez SFR", "SFR"),
            ("Tech Lead chez Total", "Total"),
            ("Architecte chez Renault", "Renault"),
        ]
        for title, expected_client in test_cases:
            with self.subTest(title=title):
                client = self.parser._extract_client_name(title)
                self.assertEqual(client, expected_client)

    def test_extract_client_with_french_accents(self):
        """Doit extraire les noms avec accents français"""
        test_cases = [
            ("Java Developer for Société Générale", "Société Générale"),
            ("Tech Lead @ Crédit Agricole", "Crédit Agricole"),
            ("Consultant chez Électricité de France", "Électricité de France"),
            ("Developer @ L'Oréal", "L'Oréal"),
            ("Engineer for BNP Paribas", "BNP Paribas"),
        ]
        for title, expected_client in test_cases:
            with self.subTest(title=title):
                client = self.parser._extract_client_name(title)
                self.assertEqual(client, expected_client)

    def test_extract_client_with_special_characters(self):
        """Doit extraire les noms avec caractères spéciaux"""
        test_cases = [
            # Note: Le pattern s'arrête aux tirets en fin de mot
            ("Developer @ SNCF-Connect", "SNCF"),  # S'arrête avant le tiret
            ("Consultant for Air France-KLM", "Air France"),  # S'arrête avant le tiret
            ("Tech Lead @ Pôle Emploi", "Pôle Emploi"),
            ("Engineer chez L'Équipe", "L'Équipe"),
        ]
        for title, expected_client in test_cases:
            with self.subTest(title=title):
                client = self.parser._extract_client_name(title)
                self.assertEqual(client, expected_client)

    def test_no_client_in_title(self):
        """Doit retourner None si pas de client dans le titre"""
        test_cases = [
            "Senior Developer",
            "Tech Lead",
            "Consultant",
            "Software Engineer",
        ]
        for title in test_cases:
            with self.subTest(title=title):
                client = self.parser._extract_client_name(title)
                self.assertIsNone(client)

    def test_empty_or_none_title(self):
        """Doit gérer les titres vides ou None"""
        self.assertIsNone(self.parser._extract_client_name(""))
        self.assertIsNone(self.parser._extract_client_name(None))

    def test_client_name_with_ampersand(self):
        """Doit extraire les noms avec &"""
        test_cases = [
            ("Developer @ Procter & Gamble", "Procter & Gamble"),
            ("Consultant for Johnson & Johnson", "Johnson & Johnson"),
        ]
        for title, expected_client in test_cases:
            with self.subTest(title=title):
                client = self.parser._extract_client_name(title)
                self.assertEqual(client, expected_client)


class TestDatesOverlap(unittest.TestCase):
    """Tests pour la détection de chevauchement de dates"""

    def setUp(self):
        self.parser = LinkedInParser([])

    def test_dates_completely_overlap(self):
        """Les dates se chevauchent complètement"""
        pos1 = {'started_on': '2020-01', 'finished_on': '2020-12'}
        pos2 = {'started_on': '2020-03', 'finished_on': '2020-08'}
        self.assertTrue(self.parser._dates_overlap(pos1, pos2))

    def test_dates_partially_overlap(self):
        """Les dates se chevauchent partiellement"""
        pos1 = {'started_on': '2020-01', 'finished_on': '2020-06'}
        pos2 = {'started_on': '2020-04', 'finished_on': '2020-10'}
        self.assertTrue(self.parser._dates_overlap(pos1, pos2))

    def test_dates_no_overlap(self):
        """Les dates ne se chevauchent pas"""
        pos1 = {'started_on': '2019-01', 'finished_on': '2019-12'}
        pos2 = {'started_on': '2020-01', 'finished_on': '2020-12'}
        self.assertFalse(self.parser._dates_overlap(pos1, pos2))

    def test_dates_touch_exactly(self):
        """Les dates se touchent exactement (fin = début)"""
        pos1 = {'started_on': '2019-01', 'finished_on': '2019-12'}
        pos2 = {'started_on': '2019-12', 'finished_on': '2020-12'}
        # Devrait se chevaucher car même mois
        self.assertTrue(self.parser._dates_overlap(pos1, pos2))

    def test_one_position_still_active(self):
        """Une position est toujours active (pas de finished_on)"""
        pos1 = {'started_on': '2020-01', 'finished_on': ''}
        pos2 = {'started_on': '2020-06', 'finished_on': ''}
        self.assertTrue(self.parser._dates_overlap(pos1, pos2))

    def test_missing_start_date(self):
        """Dates manquantes ne doivent pas chevaucher"""
        pos1 = {'started_on': '', 'finished_on': '2020-12'}
        pos2 = {'started_on': '2020-01', 'finished_on': '2020-12'}
        self.assertFalse(self.parser._dates_overlap(pos1, pos2))


class TestConsultantPositionsMerging(unittest.TestCase):
    """Tests pour la fusion automatique des positions consultant"""

    def test_simple_merge_two_positions(self):
        """Fusion simple : 2 positions même entreprise qui se chevauchent"""
        temp_dir = tempfile.mkdtemp()
        positions_csv = """Company Name,Title,Description,Location,Started On,Finished On
Zenika,Consultant Développeur,,Paris,2020-01,2020-12
Zenika,Software Engineer @ Aircall,"Description détaillée de la mission",Remote,2020-03,2020-08
"""
        positions_path = os.path.join(temp_dir, 'Positions.csv')
        with open(positions_path, 'w') as f:
            f.write(positions_csv)

        parser = LinkedInParser([positions_path])
        data = parser.parse()

        # Vérifier qu'on a 1 seule position
        self.assertEqual(len(data['positions']), 1)

        # Vérifier que c'est la position principale
        main_pos = data['positions'][0]
        self.assertEqual(main_pos['company'], 'Zenika')
        self.assertEqual(main_pos['title'], 'Consultant Développeur')

        # Vérifier qu'on a 1 mission
        self.assertIn('missions', main_pos)
        self.assertEqual(len(main_pos['missions']), 1)

        # Vérifier la mission
        mission = main_pos['missions'][0]
        self.assertEqual(mission['client'], 'Aircall')
        self.assertIn('Aircall', mission['title'])

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)

    def test_merge_multiple_missions(self):
        """Fusion avec plusieurs missions pour la même entreprise"""
        temp_dir = tempfile.mkdtemp()
        positions_csv = """Company Name,Title,Description,Location,Started On,Finished On
Accenture,Senior Consultant,,Paris,2019-01,2021-12
Accenture,Java Developer @ Société Générale,"Mission bancaire",Paris,2019-01,2019-06
Accenture,Tech Lead for Carrefour,"Refonte e-commerce",Lyon,2019-07,2020-03
Accenture,Architect chez Orange,"Architecture cloud",Paris,2020-04,2021-12
"""
        positions_path = os.path.join(temp_dir, 'Positions.csv')
        with open(positions_path, 'w') as f:
            f.write(positions_csv)

        parser = LinkedInParser([positions_path])
        data = parser.parse()

        # Vérifier qu'on a 1 seule position
        self.assertEqual(len(data['positions']), 1)

        # Vérifier qu'on a 3 missions
        main_pos = data['positions'][0]
        self.assertEqual(len(main_pos['missions']), 3)

        # Vérifier les noms des clients
        clients = [m['client'] for m in main_pos['missions']]
        self.assertIn('Société Générale', clients)
        self.assertIn('Carrefour', clients)
        self.assertIn('Orange', clients)

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)

    def test_no_merge_different_companies(self):
        """Pas de fusion : entreprises différentes"""
        temp_dir = tempfile.mkdtemp()
        positions_csv = """Company Name,Title,Description,Location,Started On,Finished On
Zenika,Consultant,,Paris,2020-01,2020-12
Accenture,Developer @ Client,"Description",Paris,2020-03,2020-08
"""
        positions_path = os.path.join(temp_dir, 'Positions.csv')
        with open(positions_path, 'w') as f:
            f.write(positions_csv)

        parser = LinkedInParser([positions_path])
        data = parser.parse()

        # Vérifier qu'on a 2 positions séparées
        self.assertEqual(len(data['positions']), 2)

        # Vérifier qu'aucune n'a de missions
        for pos in data['positions']:
            self.assertNotIn('missions', pos)

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)

    def test_no_merge_no_overlap(self):
        """Pas de fusion : dates ne se chevauchent pas"""
        temp_dir = tempfile.mkdtemp()
        positions_csv = """Company Name,Title,Description,Location,Started On,Finished On
Zenika,Consultant,,Paris,2019-01,2019-12
Zenika,Developer @ Client,"Description",Paris,2020-01,2020-12
"""
        positions_path = os.path.join(temp_dir, 'Positions.csv')
        with open(positions_path, 'w') as f:
            f.write(positions_csv)

        parser = LinkedInParser([positions_path])
        data = parser.parse()

        # Vérifier qu'on a 2 positions séparées
        self.assertEqual(len(data['positions']), 2)

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)

    def test_merge_keeps_longer_description(self):
        """La fusion garde la position avec la description la plus longue comme mission"""
        temp_dir = tempfile.mkdtemp()
        positions_csv = """Company Name,Title,Description,Location,Started On,Finished On
Zenika,Consultant,Short description here,Paris,2020-01,2020-12
Zenika,Developer @ Aircall,"Very very very very very very long detailed description of the mission with lots of information about the work done",Remote,2020-03,2020-08
"""
        positions_path = os.path.join(temp_dir, 'Positions.csv')
        with open(positions_path, 'w') as f:
            f.write(positions_csv)

        parser = LinkedInParser([positions_path])
        data = parser.parse()

        # La mission doit contenir la longue description
        mission = data['positions'][0]['missions'][0]
        self.assertIn('Very very very', mission['description'])
        self.assertGreater(len(mission['description']), 50)

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)

    def test_multiple_companies_with_missions(self):
        """Plusieurs entreprises, chacune avec ses missions"""
        temp_dir = tempfile.mkdtemp()
        positions_csv = """Company Name,Title,Description,Location,Started On,Finished On
Zenika,Consultant Développeur,,Paris,2020-01,2020-12
Zenika,Developer @ Aircall,"Mission Aircall",Remote,2020-03,2020-08
Accenture,Senior Consultant,,Paris,2019-01,2019-06
Accenture,Tech Lead for Google,"Mission Google",Paris,2019-01,2019-06
Freelance,Full Stack Developer,,Remote,2021-01,2023-12
Freelance,Backend @ Netflix,"Mission Netflix",Remote,2021-01,2021-06
Freelance,Frontend chez Spotify,"Mission Spotify",Remote,2021-07,2023-12
"""
        positions_path = os.path.join(temp_dir, 'Positions.csv')
        with open(positions_path, 'w') as f:
            f.write(positions_csv)

        parser = LinkedInParser([positions_path])
        data = parser.parse()

        # Vérifier qu'on a 3 positions (une par entreprise)
        self.assertEqual(len(data['positions']), 3)

        # Vérifier que chaque position a des missions
        for pos in data['positions']:
            self.assertIn('missions', pos)
            self.assertGreater(len(pos['missions']), 0)

        # Vérifier le nombre total de missions
        total_missions = sum(len(pos['missions']) for pos in data['positions'])
        self.assertEqual(total_missions, 4)  # Zenika:1 + Accenture:1 + Freelance:2 = 4

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


class TestConsultantMissionsEdgeCases(unittest.TestCase):
    """Tests pour les cas limites"""

    def test_empty_positions_list(self):
        """Liste de positions vide ne doit pas crasher"""
        parser = LinkedInParser([])
        parser.data['positions'] = []
        parser._merge_consultant_positions()
        self.assertEqual(len(parser.data['positions']), 0)

    def test_single_position_no_merge(self):
        """Une seule position ne doit pas être modifiée"""
        temp_dir = tempfile.mkdtemp()
        positions_csv = """Company Name,Title,Description,Location,Started On,Finished On
Zenika,Consultant Développeur,Some description,Paris,2020-01,2020-12
"""
        positions_path = os.path.join(temp_dir, 'Positions.csv')
        with open(positions_path, 'w') as f:
            f.write(positions_csv)

        parser = LinkedInParser([positions_path])
        data = parser.parse()

        # Vérifier qu'on a toujours 1 position
        self.assertEqual(len(data['positions']), 1)
        # Vérifier qu'elle n'a pas de missions
        self.assertNotIn('missions', data['positions'][0])

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)

    def test_mission_without_client_pattern(self):
        """Mission sans pattern de client devrait utiliser 'Client' générique"""
        temp_dir = tempfile.mkdtemp()
        positions_csv = """Company Name,Title,Description,Location,Started On,Finished On
Zenika,Consultant,,Paris,2020-01,2020-12
Zenika,Software Engineer,"Detailed mission description without client pattern",Remote,2020-03,2020-08
"""
        positions_path = os.path.join(temp_dir, 'Positions.csv')
        with open(positions_path, 'w') as f:
            f.write(positions_csv)

        parser = LinkedInParser([positions_path])
        data = parser.parse()

        # Vérifier que la mission existe
        mission = data['positions'][0]['missions'][0]
        # Le client devrait être "Client" par défaut
        self.assertEqual(mission['client'], 'Client')

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)

    def test_three_positions_same_company(self):
        """3 positions pour la même entreprise : 1 principale + 2 missions"""
        temp_dir = tempfile.mkdtemp()
        positions_csv = """Company Name,Title,Description,Location,Started On,Finished On
Zenika,Consultant,,Paris,2020-01,2020-12
Zenika,Developer @ Aircall,"Mission 1",Remote,2020-03,2020-06
Zenika,Tech Lead @ BNP,"Mission 2",Paris,2020-07,2020-12
"""
        positions_path = os.path.join(temp_dir, 'Positions.csv')
        with open(positions_path, 'w') as f:
            f.write(positions_csv)

        parser = LinkedInParser([positions_path])
        data = parser.parse()

        # Vérifier qu'on a 1 position avec 2 missions
        self.assertEqual(len(data['positions']), 1)
        self.assertEqual(len(data['positions'][0]['missions']), 2)

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    # Exécuter les tests avec un output verbeux
    unittest.main(verbosity=2)
