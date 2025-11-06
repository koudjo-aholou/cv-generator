"""
Tests unitaires pour le générateur de CV

Ces tests valident le comportement de nettoyage des emojis,
la normalisation des apostrophes et le formatage des descriptions.
"""

import unittest
from cv_generator import CVGenerator


class TestEmojiCleaning(unittest.TestCase):
    """Tests pour le nettoyage des emojis"""

    def test_emoji_removed_and_replaced_with_newline(self):
        """Les emojis doivent être remplacés par des sauts de ligne"""
        data = {
            'profile': {'summary': '🎉 Expert en IA 🤖 Développement'},
            'positions': []
        }
        cv = CVGenerator(data)
        self.assertIn('\n', cv.data['profile']['summary'])
        self.assertNotIn('🎉', cv.data['profile']['summary'])
        self.assertNotIn('🤖', cv.data['profile']['summary'])

    def test_multiple_emojis_create_list(self):
        """Plusieurs emojis doivent créer une liste de lignes"""
        data = {
            'profile': {'summary': '🚀 Item 1 💡 Item 2 ⚡ Item 3'},
            'positions': []
        }
        cv = CVGenerator(data)
        lines = cv.data['profile']['summary'].split('\n')
        # Vérifier qu'on a bien 3 lignes (les emojis créent des sauts de ligne)
        self.assertEqual(len([l for l in lines if l.strip()]), 3)

    def test_common_emojis_removed(self):
        """Les emojis courants doivent être nettoyés"""
        emojis = '🎉🤖💻🚀🔥💡⚡✨🌟✅'
        data = {
            'profile': {'summary': f'{emojis} Test {emojis}'},
            'positions': []
        }
        cv = CVGenerator(data)
        summary = cv.data['profile']['summary']
        # Vérifier qu'aucun emoji n'est présent
        for emoji in emojis:
            self.assertNotIn(emoji, summary)

    def test_bullet_characters_removed(self):
        """Les caractères bullet Unicode doivent être supprimés"""
        bullets = '•‣◦⁃∙'
        data = {
            'profile': {'summary': f'Test {bullets} avec bullets'},
            'positions': []
        }
        cv = CVGenerator(data)
        summary = cv.data['profile']['summary']
        for bullet in bullets:
            self.assertNotIn(bullet, summary)


class TestApostropheNormalization(unittest.TestCase):
    """Tests pour la normalisation des apostrophes typographiques"""

    def test_right_single_quotation_normalized(self):
        """L'apostrophe typographique droite (') doit être normalisée en '"""
        data = {
            'profile': {'summary': 'Réalisation d\u2019une étude'},  # U+2019
            'positions': []
        }
        cv = CVGenerator(data)
        self.assertIn("d'une", cv.data['profile']['summary'])
        self.assertNotIn('\u2019', cv.data['profile']['summary'])

    def test_left_single_quotation_normalized(self):
        """L'apostrophe typographique gauche (') doit être normalisée en '"""
        data = {
            'profile': {'summary': 'L\u2018API est rapide'},  # U+2018
            'positions': []
        }
        cv = CVGenerator(data)
        self.assertIn("L'API", cv.data['profile']['summary'])
        self.assertNotIn('\u2018', cv.data['profile']['summary'])

    def test_multiple_apostrophes_in_text(self):
        """Plusieurs apostrophes dans un texte doivent toutes être normalisées"""
        data = {
            'profile': {'summary': 'Réalisation d\u2019une étude sur l\u2019API d\u2019Hubspot'},
            'positions': []
        }
        cv = CVGenerator(data)
        summary = cv.data['profile']['summary']
        self.assertIn("d'une", summary)
        self.assertIn("l'API", summary)
        self.assertIn("d'Hubspot", summary)
        self.assertNotIn('\u2019', summary)

    def test_apostrophe_not_creating_line_breaks(self):
        """Les apostrophes ne doivent PAS créer de sauts de ligne"""
        data = {
            'profile': {'summary': 'Développement d\u2019une application web'},
            'positions': []
        }
        cv = CVGenerator(data)
        summary = cv.data['profile']['summary']
        # Le texte ne doit pas contenir de sauts de ligne
        self.assertNotIn('\n', summary)
        # Les mots doivent rester intacts
        self.assertIn("d'une", summary)


class TestDescriptionFormatting(unittest.TestCase):
    """Tests pour le formatage des descriptions"""

    def test_simple_paragraph_no_bullets(self):
        """Un paragraphe simple ne doit pas avoir de bullets"""
        data = {
            'profile': {'summary': 'Ceci est un paragraphe simple sans liste'},
            'positions': []
        }
        cv = CVGenerator(data)
        formatted = cv._format_description(cv.data['profile']['summary'])
        self.assertNotIn('•', formatted)

    def test_emojis_create_bullet_list(self):
        """Les emojis doivent créer automatiquement une liste à puces"""
        data = {
            'profile': {'summary': '🎉 Item 1 🤖 Item 2 💻 Item 3'},
            'positions': []
        }
        cv = CVGenerator(data)
        formatted = cv._format_description(cv.data['profile']['summary'])
        # Doit contenir des bullets
        self.assertIn('•', formatted)
        # Doit avoir 3 bullets (un par item)
        bullet_count = formatted.count('•')
        self.assertEqual(bullet_count, 3)

    def test_native_bullets_preserved(self):
        """Les bullets natifs (•) doivent être préservés et formatés"""
        data = {
            'profile': {'summary': 'Item 1 • Item 2 • Item 3'},
            'positions': []
        }
        cv = CVGenerator(data)
        formatted = cv._format_description(cv.data['profile']['summary'])
        # Doit contenir des bullets
        self.assertIn('•', formatted)
        # Chaque item doit être sur sa propre ligne avec un bullet
        self.assertIn('• Item 1', formatted)
        self.assertIn('• Item 2', formatted)
        self.assertIn('• Item 3', formatted)

    def test_line_break_markers_converted(self):
        """Les marqueurs 'n' doivent être convertis en sauts de ligne"""
        data = {
            'profile': {'summary': 'n Item 1 n Item 2 n Item 3'},
            'positions': []
        }
        cv = CVGenerator(data)
        formatted = cv._format_description(cv.data['profile']['summary'])
        # Les items doivent être séparés par <br/>
        self.assertIn('<br/>', formatted)

    def test_double_line_break_markers(self):
        """Les marqueurs 'nn' doivent créer des paragraphes"""
        data = {
            'profile': {'summary': 'Paragraphe 1 nn Paragraphe 2'},
            'positions': []
        }
        cv = CVGenerator(data)
        formatted = cv._format_description(cv.data['profile']['summary'])
        # Doit contenir un double saut de ligne
        self.assertIn('<br/><br/>', formatted)

    def test_dash_and_asterisk_bullets(self):
        """Les tirets (-) et astérisques (*) doivent être convertis en bullets"""
        data = {
            'profile': {'summary': '- Item 1\n* Item 2\n- Item 3'},
            'positions': []
        }
        cv = CVGenerator(data)
        formatted = cv._format_description(cv.data['profile']['summary'])
        # Tous doivent être convertis en •
        self.assertIn('• Item 1', formatted)
        self.assertIn('• Item 2', formatted)
        self.assertIn('• Item 3', formatted)


class TestComplexScenarios(unittest.TestCase):
    """Tests pour des scénarios complexes combinant plusieurs fonctionnalités"""

    def test_emojis_and_apostrophes_together(self):
        """Emojis et apostrophes typographiques doivent fonctionner ensemble"""
        data = {
            'profile': {
                'summary': '🚀 Réalisation d\u2019une étude 🔥 Optimisation de l\u2019API'
            },
            'positions': []
        }
        cv = CVGenerator(data)
        formatted = cv._format_description(cv.data['profile']['summary'])

        # Les apostrophes doivent être normalisées
        self.assertIn("d'une", formatted)
        self.assertIn("l'API", formatted)

        # Les emojis doivent créer des bullets
        self.assertIn('•', formatted)
        bullet_count = formatted.count('•')
        self.assertEqual(bullet_count, 2)

        # Pas de mots cassés
        self.assertNotIn('d<br/>', formatted)
        self.assertNotIn('l<br/>', formatted)

    def test_mixed_bullets_emojis_and_native(self):
        """Mix d'emojis et de bullets natifs (•)"""
        data = {
            'profile': {
                'summary': '🎉 Item 1 • Item 2 🚀 Item 3 • Item 4'
            },
            'positions': []
        }
        cv = CVGenerator(data)
        formatted = cv._format_description(cv.data['profile']['summary'])

        # Tous les items doivent avoir des bullets
        bullet_count = formatted.count('•')
        self.assertGreaterEqual(bullet_count, 4)

    def test_real_world_linkedin_description(self):
        """Test avec une vraie description LinkedIn"""
        data = {
            'profile': {},
            'positions': [{
                'description': (
                    'n Développement d\u2019un système de modération IA hybride • '
                    'Conception et déploiement d\u2019une solution de modération '
                    'automatisée • Impact : Traitement de 50 000 photos par mois '
                    'nn Optimisation des performances IA • Analyse approfondie des '
                    'modèles d\u2019IA et optimisation des prompts'
                )
            }]
        }
        cv = CVGenerator(data)
        formatted = cv._format_description(cv.data['positions'][0]['description'])

        # Doit contenir des bullets
        self.assertIn('•', formatted)

        # Les apostrophes doivent être préservées
        self.assertIn("d'un", formatted)
        self.assertIn("d'une", formatted)
        self.assertIn("d'IA", formatted)

        # Pas de mots cassés
        self.assertNotIn('d<br/>un', formatted)
        self.assertNotIn('d<br/>une', formatted)

        # Doit avoir une séparation de paragraphe (nn)
        self.assertIn('<br/><br/>', formatted)

    def test_position_description_with_apostrophes(self):
        """Test du cas reporté : 'Réalisation d'une étude sur l'API'"""
        data = {
            'profile': {},
            'positions': [{
                'description': 'Réalisation d\u2019une étude technique (TDR) sur l\u2019API v2 d\u2019Hubspot avant déploiement'
            }]
        }
        cv = CVGenerator(data)
        desc = cv.data['positions'][0]['description']
        formatted = cv._format_description(desc)

        # Vérifier que les mots sont intacts
        self.assertIn("d'une", desc)
        self.assertIn("l'API", desc)
        self.assertIn("d'Hubspot", desc)

        # Vérifier qu'il n'y a pas de sauts de ligne inappropriés
        self.assertNotIn('d\n', desc)
        self.assertNotIn('l\n', desc)

        # Dans le formaté, pas de bullets erronés comme "• une" ou "• API"
        self.assertNotIn('• une étude', formatted)
        self.assertNotIn('• API', formatted)


class TestEdgeCases(unittest.TestCase):
    """Tests pour les cas limites"""

    def test_empty_string(self):
        """Une chaîne vide doit rester vide"""
        data = {
            'profile': {'summary': ''},
            'positions': []
        }
        cv = CVGenerator(data)
        formatted = cv._format_description('')
        self.assertEqual(formatted, '')

    def test_none_value(self):
        """Une valeur None doit retourner None"""
        data = {
            'profile': {},
            'positions': []
        }
        cv = CVGenerator(data)
        formatted = cv._format_description(None)
        self.assertIsNone(formatted)

    def test_only_whitespace(self):
        """Un texte avec seulement des espaces doit être nettoyé"""
        data = {
            'profile': {'summary': '    '},
            'positions': []
        }
        cv = CVGenerator(data)
        formatted = cv._format_description(cv.data['profile']['summary'])
        self.assertEqual(formatted, '')

    def test_very_long_line(self):
        """Une ligne très longue (>250 chars) ne doit pas devenir un bullet"""
        long_text = 'A' * 300  # 300 caractères
        data = {
            'profile': {'summary': long_text},
            'positions': []
        }
        cv = CVGenerator(data)
        formatted = cv._format_description(cv.data['profile']['summary'])
        # Ne doit pas avoir de bullet car c'est un long paragraphe
        self.assertNotIn('•', formatted)

    def test_special_characters_preserved(self):
        """Les caractères spéciaux français doivent être préservés"""
        data = {
            'profile': {'summary': 'Développement d\u2019applications avec éléments français : à, é, è, ê, ç, ô'},
            'positions': []
        }
        cv = CVGenerator(data)
        summary = cv.data['profile']['summary']
        # Tous les accents doivent être préservés
        for char in ['à', 'é', 'è', 'ê', 'ç', 'ô']:
            self.assertIn(char, summary)


if __name__ == '__main__':
    # Exécuter les tests avec un output verbeux
    unittest.main(verbosity=2)
