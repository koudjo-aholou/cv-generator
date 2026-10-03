from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    PageBreak,
    HRFlowable,
    Image,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import tempfile
import base64
import re
from io import BytesIO
from PIL import Image as PILImage, ImageDraw
from datetime import datetime
from xml.sax.saxutils import escape as xml_escape


class CVGenerator:
    """Generate PDF CV from parsed LinkedIn data"""

    def __init__(self, data, config=None):
        # Clean emojis from data before storing
        self.data = self._clean_emoji_from_data(data)
        self.config = config or {}
        self.styles = getSampleStyleSheet()

        # Extract colors from config or use defaults
        colors_config = self.config.get("colors", {})
        self.colors = {
            "primary": colors_config.get("primary", "#3498db"),
            "text": colors_config.get("text", "#2c3e50"),
            "secondary_text": colors_config.get("secondary_text", "#7f8c8d"),
        }

        # Extract template from config or use default
        self.template = self.config.get("template", "modern")

        # Language of the generated CV content ("fr" or "en")
        self.language = self.config.get("language", "fr")
        if self.language not in ("fr", "en"):
            self.language = "fr"

        # CV type ("standard" or "swiss") — toggles Swiss-specific conventions:
        # extended personal info (birth date, nationality, civil status, permit),
        # dd.mm.yyyy date format, and a more prominent photo
        self.cv_type = self.config.get("cv_type", "standard")

        # Section titles — language-aware defaults, overridable via config
        default_labels = {
            "fr": {
                "about": "À Propos",
                "experience": "Expériences Professionnelles",
                "education": "Formations",
                "skills": "Compétences",
                "languages": "Langues",
                "certifications": "Certifications",
            },
            "en": {
                "about": "About",
                "experience": "Professional Experience",
                "education": "Education",
                "skills": "Skills",
                "languages": "Languages",
                "certifications": "Certifications",
            },
        }[self.language]
        # A label sent as null/empty by the client falls back to the default
        # rather than rendering an empty (or crashing) section header.
        labels = self.config.get("labels") or {}
        self.labels = {
            key: (labels.get(key) or default_value)
            for key, default_value in default_labels.items()
        }

        self._setup_custom_styles()

    def _clean_emoji_from_data(self, data):
        """Remove all emojis and problematic Unicode characters from data to avoid encoding issues with Helvetica font

        Emojis are treated as bullet point separators - they create new lines that will be formatted as bullet points.
        """

        def remove_emoji(text):
            if not isinstance(text, str):
                return text

            # ÉTAPE 1: Normaliser les apostrophes typographiques en apostrophes ASCII
            # pour préserver les mots comme "d'une", "l'API"
            # U+2019 (') → U+0027 (')
            # U+2018 (') → U+0027 (')
            text = text.replace("\u2019", "'")  # Right single quotation mark
            text = text.replace("\u2018", "'")  # Left single quotation mark
            text = text.replace("\u201b", "'")  # Single high-reversed-9 quotation mark

            # ÉTAPE 2: Pattern exhaustif pour capturer TOUS les emojis et symboles Unicode problématiques
            # Cette approche couvre toutes les plages d'emojis Unicode connues
            emoji_pattern = re.compile(
                "["
                "\U0001f600-\U0001f64f"  # emoticons
                "\U0001f300-\U0001f5ff"  # symbols & pictographs (inclut 🎉 🔄 🗄️)
                "\U0001f680-\U0001f6ff"  # transport & map symbols
                "\U0001f1e0-\U0001f1ff"  # flags (iOS)
                "\U0001f700-\U0001f77f"  # alchemical symbols
                "\U0001f780-\U0001f7ff"  # geometric shapes extended
                "\U0001f800-\U0001f8ff"  # supplemental arrows-C
                "\U0001f900-\U0001f9ff"  # supplemental symbols (inclut 🤖)
                "\U0001fa00-\U0001fa6f"  # extended symbols
                "\U0001fa70-\U0001faff"  # symbols and pictographs extended-A
                "\U00002600-\U000026ff"  # miscellaneous symbols (inclut ⚡)
                "\U00002700-\U000027bf"  # dingbats
                "\U00002300-\U000023ff"  # miscellaneous technical
                "\U00002b00-\U00002bff"  # miscellaneous symbols and arrows
                "\U00003000-\U0000303f"  # CJK symbols and punctuation
                "\U0000fe00-\U0000fe0f"  # variation selectors (modificateurs d'emojis)
                "\U0000ff00-\U0000ffef"  # halfwidth and fullwidth forms
                "\U00002000-\U00002012"  # general punctuation (avant – et —)
                "\U00002015-\U00002021"  # general punctuation (après —, avant •)
                "\U00002023-\U0000206f"  # general punctuation (après •, U+2022 préservé pour bullets)
                "\U00002190-\U000021ff"  # arrows
                "\U00002300-\U000023ff"  # miscellaneous technical
                "\U00002460-\U000024ff"  # enclosed alphanumerics
                "\U00002500-\U000025ff"  # box drawing
                "\U00002600-\U000027bf"  # miscellaneous symbols and dingbats
                "\U00002900-\U000029ff"  # supplemental arrows-B
                "\U00002a00-\U00002aff"  # supplemental mathematical operators
                "\U00003200-\U000032ff"  # enclosed CJK letters and months
                "\U0000e000-\U0000f8ff"  # private use area
                "\u2023"  # triangular bullet ‣
                "\u25e6"  # white bullet ◦
                "\u2043"  # hyphen bullet ⁃
                "\u2219"  # bullet operator ∙
                "\u00a0"  # non-breaking space
                "]+",
                flags=re.UNICODE,
            )

            # IMPORTANT: Remplacer les emojis par des sauts de ligne au lieu de les supprimer
            # Cela permet de traiter chaque emoji comme un séparateur de bullet point
            # Ex: "🎉 Item 1 🤖 Item 2" devient "Item 1\nItem 2"
            cleaned = emoji_pattern.sub("\n", text)

            # Nettoyer les espaces multiples (mais pas les \n)
            # Remplacer plusieurs espaces consécutifs par un seul, sauf les sauts de ligne
            cleaned = re.sub(r"[^\S\n]+", " ", cleaned)

            # Nettoyer les sauts de ligne multiples
            cleaned = re.sub(r"\n+", "\n", cleaned)

            return cleaned.strip()

        def clean_dict(d):
            """Recursively clean emojis from dictionary values"""
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict(item) for item in d]
            elif isinstance(d, str):
                return remove_emoji(d)
            else:
                return d

        return clean_dict(data)

    @staticmethod
    def _escape(value):
        """Escape user-supplied text for ReportLab's mini-HTML parser.

        ReportLab parses a small HTML dialect inside Paragraph, so a stray '<'
        in user data (an address, a job title, a custom section label) aborts
        the whole PDF with "unclosed tags", and '<b>' would inject formatting.
        Everything that originates from the client payload must go through
        here BEFORE any intentional markup (&#8226;, <br/>, <b>) is composed
        around it — escaping the composed string would destroy that markup.
        """
        if value is None:
            return ""
        if not isinstance(value, str):
            value = str(value)
        return xml_escape(value)

    def _format_description(self, text):
        """
        Format description text by handling line breaks, bullet points, and improving readability.

        This function specifically handles LinkedIn export data where 'n' represents line breaks
        (not the letter 'n' in words like 'un', 'on', 'modération', etc.)

        Args:
            text (str): Raw description text

        Returns:
            str: Formatted text with proper line breaks and structure
        """
        if not text or not isinstance(text, str):
            return text

        # Échapper AVANT tout traitement : les &#8226; et <br/> ajoutés plus bas
        # sont du balisage voulu et doivent survivre. Échapper le résultat final
        # les détruirait. L'échappement n'introduit aucun des caractères que les
        # motifs ci-dessous recherchent ('n', '•', '-', '*', espaces).
        text = self._escape(text)

        # IMPORTANT: Détecter UNIQUEMENT les 'n' qui sont des marqueurs de saut de ligne
        # et non pas le 'n' qui fait partie de mots français

        # Pattern 1: " nn " (double n entouré d'espaces) = nouveau paragraphe
        # ATTENTION: Ne pas toucher "nn" dans les mots comme "données", "années"
        text = re.sub(r"\s+nn\s+", "\n\n", text)

        # Pattern 2: " n " (n entouré d'espaces) = saut de ligne
        text = text.replace(" n ", "\n")

        # Pattern 3: Début du texte qui commence par "n "
        if text.startswith("n "):
            text = text[2:]  # Supprimer le "n " du début

        # Pattern 4: Après un point/virgule/deux-points suivi de " n " = début d'une nouvelle ligne
        # Ex: "phrase. n Autre phrase" ou "phrase • n Autre"
        text = re.sub(r"([.,:;•])\s+n\s+", r"\1\n", text)

        # Pattern 5: "n" suivi d'une majuscule et précédé d'un espace = probablement un saut de ligne
        # Ex: "phrase n Développement" (où 'n' sépare deux items)
        text = re.sub(r"\s+n\s+([A-ZÀÂÄÇÈÉÊËÎÏÔÖÙÛÜ])", r"\n\1", text)

        # Nettoyer les espaces multiples (mais garder les \n)
        text = re.sub(r"[^\S\n]+", " ", text)  # Remplace les espaces multiples sauf \n

        # Diviser en lignes
        lines = text.split("\n")
        non_empty_lines = [l.strip() for l in lines if l.strip()]

        # Déterminer si c'est une liste (plusieurs lignes courtes)
        # Si on a 2+ lignes et que la plupart sont courtes (< 250 chars), c'est probablement une liste
        is_list = (
            len(non_empty_lines) >= 2
            and sum(1 for l in non_empty_lines if len(l) < 250)
            >= len(non_empty_lines) * 0.7
        )

        formatted_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                # Garder les lignes vides pour les paragraphes
                if formatted_lines and formatted_lines[-1] != "":
                    formatted_lines.append("")
                continue

            # Si la ligne contient des bullets "•", on les divise en items séparés
            if "•" in line:
                # Diviser la ligne sur les bullets
                parts = line.split("•")
                for i, part in enumerate(parts):
                    part = part.strip()
                    if part:
                        # Le premier item (avant le premier •) peut ne pas être un bullet
                        # Les suivants sont tous des bullets
                        if i == 0 and not line.startswith("•"):
                            formatted_lines.append(f"&#8226; {part}")
                        else:
                            formatted_lines.append(f"&#8226; {part}")
            # Détecter et formater les autres bullet points
            elif line.startswith("-") or line.startswith("*"):
                formatted_lines.append(f"&#8226; {line[1:].strip()}")
            # Si c'est une liste détectée (emojis transformés en sauts de ligne), ajouter des bullets
            elif is_list:
                formatted_lines.append(f"&#8226; {line}")
            else:
                # Ligne normale sans bullet (paragraphe simple)
                formatted_lines.append(line)

        # Joindre avec des balises HTML <br/> pour les sauts de ligne
        # ReportLab supporte les balises HTML basiques dans les Paragraphs
        formatted_text = "<br/>".join(formatted_lines)

        # Les doubles <br/> (paragraphes) deviennent des espacements plus grands
        formatted_text = formatted_text.replace("<br/><br/>", "<br/><br/>")

        return formatted_text

    def _setup_custom_styles(self):
        """Setup custom paragraph styles with template-specific configurations"""

        # Get template-specific style configurations
        if self.template == "modern":
            self._setup_modern_styles()
        elif self.template == "classic":
            self._setup_classic_styles()
        elif self.template == "creative":
            self._setup_creative_styles()
        else:
            # Default to modern
            self._setup_modern_styles()

    def _setup_modern_styles(self):
        """Setup modern template styles"""
        # Name style - Bold and large
        self.styles.add(
            ParagraphStyle(
                name="Name",
                parent=self.styles["Heading1"],
                fontSize=28,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=4,
                spaceBefore=0,
                alignment=TA_LEFT,
                fontName="Helvetica-Bold",
                leading=32,
            )
        )

        # Headline style
        self.styles.add(
            ParagraphStyle(
                name="Headline",
                parent=self.styles["Normal"],
                fontSize=13,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=8,
                fontName="Helvetica",
                leading=16,
            )
        )

        # Contact style
        self.styles.add(
            ParagraphStyle(
                name="Contact",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["secondary_text"]),
                spaceAfter=16,
                fontName="Helvetica",
                leading=14,
            )
        )

        # Section header style - Clean with underline
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading2"],
                fontSize=14,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=10,
                spaceBefore=16,
                fontName="Helvetica-Bold",
                leading=18,
                textTransform="uppercase",
            )
        )

        # Job title style
        self.styles.add(
            ParagraphStyle(
                name="JobTitle",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=3,
                fontName="Helvetica-Bold",
                leading=14,
                keepWithNext=1,
            )
        )

        # Company style
        self.styles.add(
            ParagraphStyle(
                name="Company",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["primary"]),
                spaceAfter=3,
                fontName="Helvetica-Oblique",
                leading=13,
                keepWithNext=1,
            )
        )

        # Date/Location style
        self.styles.add(
            ParagraphStyle(
                name="DateLocation",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor(self.colors["secondary_text"]),
                spaceAfter=6,
                fontName="Helvetica",
                leading=12,
            )
        )

        # Description style
        self.styles.add(
            ParagraphStyle(
                name="Description",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=0,
                fontName="Helvetica",
                leading=14,
                alignment=TA_JUSTIFY,
            )
        )

        # Mission client name style (for consultant missions)
        self.styles.add(
            ParagraphStyle(
                name="MissionClient",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["primary"]),
                spaceAfter=2,
                spaceBefore=2,
                fontName="Helvetica-Bold",
                leading=13,
                leftIndent=10,  # Indent to show it's nested
            )
        )

        # Mission title style (for consultant missions)
        self.styles.add(
            ParagraphStyle(
                name="MissionTitle",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=2,
                fontName="Helvetica-Oblique",
                leading=13,
                leftIndent=10,  # Indent to show it's nested
            )
        )

        # Mission description style (for consultant missions)
        self.styles.add(
            ParagraphStyle(
                name="MissionDescription",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=0,
                fontName="Helvetica",
                leading=13,
                alignment=TA_JUSTIFY,
                leftIndent=10,  # Indent to show it's nested
            )
        )

        # Summary style
        self.styles.add(
            ParagraphStyle(
                name="Summary",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=0,
                fontName="Helvetica",
                leading=15,
                alignment=TA_JUSTIFY,
            )
        )

        # Skill item style
        self.styles.add(
            ParagraphStyle(
                name="SkillItem",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=0,
                fontName="Helvetica",
                leading=13,
            )
        )

    def _setup_classic_styles(self):
        """Setup classic template styles - more traditional and formal"""
        # Name style - Centered, larger
        self.styles.add(
            ParagraphStyle(
                name="Name",
                parent=self.styles["Heading1"],
                fontSize=32,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=6,
                spaceBefore=0,
                alignment=TA_CENTER,
                fontName="Helvetica-Bold",
                leading=36,
            )
        )

        # Headline style - centered
        self.styles.add(
            ParagraphStyle(
                name="Headline",
                parent=self.styles["Normal"],
                fontSize=12,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=8,
                fontName="Helvetica",
                leading=16,
                alignment=TA_CENTER,
            )
        )

        # Contact style - centered
        self.styles.add(
            ParagraphStyle(
                name="Contact",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["secondary_text"]),
                spaceAfter=16,
                fontName="Helvetica",
                leading=14,
                alignment=TA_CENTER,
            )
        )

        # Section header style - Centered with line
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading2"],
                fontSize=13,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=10,
                spaceBefore=16,
                fontName="Helvetica-Bold",
                leading=18,
                alignment=TA_CENTER,
                textTransform="uppercase",
            )
        )

        # Job title style
        self.styles.add(
            ParagraphStyle(
                name="JobTitle",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=3,
                fontName="Helvetica-Bold",
                leading=14,
            )
        )

        # Company style - less emphasis
        self.styles.add(
            ParagraphStyle(
                name="Company",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=3,
                fontName="Helvetica",
                leading=13,
                keepWithNext=1,
            )
        )

        # Date/Location style
        self.styles.add(
            ParagraphStyle(
                name="DateLocation",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor(self.colors["secondary_text"]),
                spaceAfter=6,
                fontName="Helvetica",
                leading=12,
            )
        )

        # Description style
        self.styles.add(
            ParagraphStyle(
                name="Description",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=0,
                fontName="Helvetica",
                leading=14,
                alignment=TA_JUSTIFY,
            )
        )

        # Summary style
        self.styles.add(
            ParagraphStyle(
                name="Summary",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=0,
                fontName="Helvetica",
                leading=15,
                alignment=TA_JUSTIFY,
            )
        )

        # Skill item style
        self.styles.add(
            ParagraphStyle(
                name="SkillItem",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=0,
                fontName="Helvetica",
                leading=13,
            )
        )

        # Mission Client style (for consultant missions)
        self.styles.add(
            ParagraphStyle(
                name="MissionClient",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=2,
                fontName="Helvetica-Bold",
                leading=13,
            )
        )

        # Mission Title style
        self.styles.add(
            ParagraphStyle(
                name="MissionTitle",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=2,
                fontName="Helvetica-Oblique",
                leading=12,
            )
        )

        # Mission Description style
        self.styles.add(
            ParagraphStyle(
                name="MissionDescription",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=0,
                fontName="Helvetica",
                leading=13,
                alignment=TA_JUSTIFY,
            )
        )

    def _setup_creative_styles(self):
        """Setup creative template styles - more colorful and bold"""
        # Name style - Bold and colorful
        self.styles.add(
            ParagraphStyle(
                name="Name",
                parent=self.styles["Heading1"],
                fontSize=30,
                textColor=colors.HexColor(self.colors["primary"]),
                spaceAfter=4,
                spaceBefore=0,
                alignment=TA_LEFT,
                fontName="Helvetica-Bold",
                leading=34,
            )
        )

        # Headline style
        self.styles.add(
            ParagraphStyle(
                name="Headline",
                parent=self.styles["Normal"],
                fontSize=14,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=8,
                fontName="Helvetica-Bold",
                leading=17,
            )
        )

        # Contact style
        self.styles.add(
            ParagraphStyle(
                name="Contact",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["secondary_text"]),
                spaceAfter=16,
                fontName="Helvetica",
                leading=14,
            )
        )

        # Section header style - Colorful
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading2"],
                fontSize=15,
                textColor=colors.HexColor(self.colors["primary"]),
                spaceAfter=10,
                spaceBefore=16,
                fontName="Helvetica-Bold",
                leading=19,
                textTransform="uppercase",
            )
        )

        # Job title style - emphasized
        self.styles.add(
            ParagraphStyle(
                name="JobTitle",
                parent=self.styles["Normal"],
                fontSize=12,
                textColor=colors.HexColor(self.colors["primary"]),
                spaceAfter=3,
                fontName="Helvetica-Bold",
                leading=15,
                keepWithNext=1,
            )
        )

        # Company style
        self.styles.add(
            ParagraphStyle(
                name="Company",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=3,
                fontName="Helvetica",
                leading=14,
                keepWithNext=1,
            )
        )

        # Date/Location style
        self.styles.add(
            ParagraphStyle(
                name="DateLocation",
                parent=self.styles["Normal"],
                fontSize=9,
                textColor=colors.HexColor(self.colors["secondary_text"]),
                spaceAfter=6,
                fontName="Helvetica",
                leading=12,
            )
        )

        # Description style
        self.styles.add(
            ParagraphStyle(
                name="Description",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=0,
                fontName="Helvetica",
                leading=14,
                alignment=TA_JUSTIFY,
            )
        )

        # Summary style
        self.styles.add(
            ParagraphStyle(
                name="Summary",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=0,
                fontName="Helvetica",
                leading=15,
                alignment=TA_JUSTIFY,
            )
        )

        # Skill item style
        self.styles.add(
            ParagraphStyle(
                name="SkillItem",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=0,
                fontName="Helvetica",
                leading=13,
            )
        )

        # Mission Client style (for consultant missions)
        self.styles.add(
            ParagraphStyle(
                name="MissionClient",
                parent=self.styles["Normal"],
                fontSize=11,
                textColor=colors.HexColor(self.colors["primary"]),
                spaceAfter=2,
                fontName="Helvetica-Bold",
                leading=14,
            )
        )

        # Mission Title style
        self.styles.add(
            ParagraphStyle(
                name="MissionTitle",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=2,
                fontName="Helvetica-Oblique",
                leading=13,
            )
        )

        # Mission Description style
        self.styles.add(
            ParagraphStyle(
                name="MissionDescription",
                parent=self.styles["Normal"],
                fontSize=10,
                textColor=colors.HexColor(self.colors["text"]),
                spaceAfter=0,
                fontName="Helvetica",
                leading=14,
                alignment=TA_JUSTIFY,
            )
        )

    def generate(self):
        """Generate the PDF CV"""
        # Create CV folder if it doesn't exist
        cv_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cv")
        os.makedirs(cv_folder, exist_ok=True)

        # Extract name from profile for filename
        profile = self.data.get("profile", {})
        last_name = profile.get("last_name", "Inconnu").strip()
        first_name = profile.get("first_name", "").strip()

        # Clean names for filename (remove special characters)
        import re

        last_name_clean = re.sub(r"[^\w\s-]", "", last_name).replace(" ", "_")
        first_name_clean = re.sub(r"[^\w\s-]", "", first_name).replace(" ", "_")

        # Generate filename with name and timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filename = f"CV_{last_name_clean.upper()}_{first_name_clean.capitalize()}_{timestamp}.pdf"
        pdf_path = os.path.join(cv_folder, filename)

        # Create PDF with better margins
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        # Build content
        story = []

        # Header section (always included)
        story.extend(self._build_header())

        # Get section configuration
        sections_config = self.config.get("sections", {})
        section_order = self.config.get(
            "section_order",
            [
                "summary",
                "experience",
                "education",
                "skills",
                "languages",
                "certifications",
            ],
        )

        # Section builders mapping
        section_builders = {
            "summary": self._build_summary,
            "experience": self._build_experience,
            "education": self._build_education,
            "skills": self._build_skills,
            "languages": self._build_languages,
            "certifications": self._build_certifications,
        }

        # Build sections in configured order
        for section_name in section_order:
            # Check if section is enabled (default to True if not specified)
            is_enabled = sections_config.get(section_name, True)

            if is_enabled and section_name in section_builders:
                # Check if section has data
                has_data = False
                if section_name == "summary":
                    has_data = bool(self.data.get("profile", {}).get("summary"))
                elif section_name in [
                    "experience",
                    "education",
                    "skills",
                    "languages",
                    "certifications",
                ]:
                    data_key = (
                        "positions" if section_name == "experience" else section_name
                    )
                    has_data = bool(self.data.get(data_key))

                if has_data:
                    story.extend(section_builders[section_name]())

        # Build PDF
        doc.build(story)

        return pdf_path

    def _create_section_header(self, title):
        """Create a section header with horizontal line"""
        elements = []
        elements.append(
            Paragraph(self._escape(title).upper(), self.styles["SectionHeader"])
        )
        elements.append(
            HRFlowable(
                width="100%",
                thickness=1,
                color=colors.HexColor(self.colors["primary"]),
                spaceBefore=0,
                spaceAfter=10,
            )
        )
        return elements

    def _build_header(self):
        """Build header section with name, contact info, and photo"""
        elements = []
        profile = self.data.get("profile", {})

        # Build info block (name, headline, contact) shared whether or not a photo is provided
        info_elements = []

        # Full name
        full_name = (
            f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
        )
        if full_name:
            info_elements.append(Paragraph(self._escape(full_name), self.styles["Name"]))

        # Headline
        if profile.get("headline"):
            info_elements.append(
                Paragraph(self._escape(profile["headline"]), self.styles["Headline"])
            )

        # Contact info
        contact_lines = []

        line1_parts = []
        if profile.get("email"):
            line1_parts.append(f"Email: {self._escape(profile['email'])}")
        if profile.get("phone"):
            line1_parts.append(f"Tel: {self._escape(profile['phone'])}")

        if line1_parts:
            contact_lines.append(" | ".join(line1_parts))

        if profile.get("address"):
            contact_lines.append(f"Adresse: {self._escape(profile['address'])}")

        # Swiss CVs conventionally list extended personal information
        # (birth date, nationality, civil status, work permit) in the header
        if self.cv_type == "swiss":
            label_map = (
                {
                    "birth_date": "Date de naissance",
                    "nationality": "Nationalité",
                    "civil_status": "État civil",
                    "permit": "Permis de travail",
                }
                if self.language == "fr"
                else {
                    "birth_date": "Date of birth",
                    "nationality": "Nationality",
                    "civil_status": "Civil status",
                    "permit": "Work permit",
                }
            )
            if profile.get("birth_date"):
                formatted_birth = self._format_swiss_date(profile["birth_date"])
                contact_lines.append(
                    f"{label_map['birth_date']}: {self._escape(formatted_birth)}"
                )
            if profile.get("nationality"):
                contact_lines.append(
                    f"{label_map['nationality']}: {self._escape(profile['nationality'])}"
                )
            if profile.get("civil_status"):
                contact_lines.append(
                    f"{label_map['civil_status']}: {self._escape(profile['civil_status'])}"
                )
            if profile.get("permit"):
                contact_lines.append(
                    f"{label_map['permit']}: {self._escape(profile['permit'])}"
                )

        for line in contact_lines:
            info_elements.append(Paragraph(line, self.styles["Contact"]))

        # Always render a photo column: use the uploaded photo, or a placeholder
        # avatar to keep a consistent layout when no photo was provided.
        # Swiss CVs conventionally feature a larger, more prominent photo.
        photo_img = self._create_photo_image()

        if photo_img is not None:
            photo_col_width = 50 * mm if self.cv_type == "swiss" else 40 * mm
            info_col_width = 170 * mm - photo_col_width
            # Create table with info on left and photo on right
            header_table = Table(
                [[info_elements, photo_img]],
                colWidths=[info_col_width, photo_col_width],
            )
            header_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )

            elements.append(header_table)
        else:
            # Photo failed to load, use regular layout
            elements.extend(info_elements)

        elements.append(Spacer(1, 4 * mm))

        return elements

    def _format_swiss_date(self, date_str):
        """Format a date string as dd.mm.yyyy (Swiss convention)

        Accepts ISO (yyyy-mm-dd) or already-formatted (dd/mm/yyyy) input;
        falls back to returning the original value unchanged if unparsable
        or not a string (the config comes from an untrusted client payload).
        """
        if not date_str or not isinstance(date_str, str):
            return date_str

        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y"):
            try:
                return datetime.strptime(date_str, fmt).strftime("%d.%m.%Y")
            except ValueError:
                continue

        return date_str

    def _create_placeholder_avatar(self):
        """Generate a generic silhouette avatar used when no photo was provided"""
        size = 400
        bg_color = (225, 227, 230)
        fg_color = (165, 170, 178)

        pil_image = PILImage.new("RGB", (size, size), bg_color)
        draw = ImageDraw.Draw(pil_image)

        # Head
        head_r = size * 0.17
        cx, cy = size / 2, size * 0.36
        draw.ellipse(
            [cx - head_r, cy - head_r, cx + head_r, cy + head_r], fill=fg_color
        )

        # Shoulders
        body_w = size * 0.64
        draw.ellipse(
            [size / 2 - body_w / 2, size * 0.62, size / 2 + body_w / 2, size * 1.2],
            fill=fg_color,
        )

        return pil_image

    def _create_photo_image(self):
        """Create photo image from base64 data (or a placeholder) with fixed square dimensions"""
        try:
            photo_data = self.data.get("photo", "")

            if photo_data:
                # Remove data URL prefix if present
                if "base64," in photo_data:
                    photo_data = photo_data.split("base64,")[1]

                # Decode base64
                image_data = base64.b64decode(photo_data)

                # Open image with PIL
                pil_image = PILImage.open(BytesIO(image_data))
            else:
                pil_image = self._create_placeholder_avatar()

            # Convert to RGB if necessary (handles PNG with transparency)
            if pil_image.mode in ("RGBA", "LA", "P"):
                # Convert all transparent/palette modes to RGBA first
                if pil_image.mode == "P":
                    pil_image = pil_image.convert("RGBA")
                elif pil_image.mode == "LA":
                    pil_image = pil_image.convert("RGBA")

                # Create white background
                background = PILImage.new("RGB", pil_image.size, (255, 255, 255))

                # Paste with alpha mask
                if pil_image.mode == "RGBA":
                    background.paste(pil_image, mask=pil_image.split()[-1])
                else:
                    background.paste(pil_image)

                pil_image = background
            elif pil_image.mode != "RGB":
                pil_image = pil_image.convert("RGB")

            # Get dimensions
            width, height = pil_image.size

            # Calculate crop box to make it square (center crop)
            if width > height:
                # Landscape - crop sides
                left = (width - height) // 2
                top = 0
                right = left + height
                bottom = height
            else:
                # Portrait or square - crop top/bottom
                left = 0
                top = (height - width) // 2
                right = width
                bottom = top + width

            # Crop to square
            pil_image = pil_image.crop((left, top, right, bottom))

            # Resize to exact dimensions (35mm = ~138 pixels at 100 DPI)
            target_size = 138
            pil_image = pil_image.resize(
                (target_size, target_size), PILImage.Resampling.LANCZOS
            )

            # Save to BytesIO
            img_buffer = BytesIO()
            pil_image.save(img_buffer, format="JPEG", quality=85)
            img_buffer.seek(0)

            # Create ReportLab Image with exact dimensions
            img = Image(img_buffer, width=35 * mm, height=35 * mm)

            return img

        except Exception as e:
            import logging

            logging.error(f"Error loading photo: {e}")
            # Return None instead of empty Paragraph to avoid breaking table layout
            return None

    def _build_summary(self):
        """Build summary/about section"""
        elements = []
        profile = self.data.get("profile", {})

        elements.extend(self._create_section_header(self.labels["about"]))

        formatted_summary = self._format_description(profile["summary"])
        summary_para = Paragraph(formatted_summary, self.styles["Summary"])
        elements.append(KeepTogether([summary_para, Spacer(1, 4 * mm)]))

        return elements

    def _build_experience(self):
        """Build experience section"""
        elements = []

        elements.extend(self._create_section_header(self.labels["experience"]))

        # Get visible positions configuration
        visible_indices = self.config.get("experience_visible")
        all_positions = self.data.get("positions", [])

        # If visible_indices is specified, filter positions
        if visible_indices is not None:
            positions = [
                all_positions[i] for i in visible_indices if i < len(all_positions)
            ]
        else:
            positions = all_positions

        for i, position in enumerate(positions):
            position_elements = []

            # Job title
            if position.get("title"):
                position_elements.append(
                    Paragraph(self._escape(position["title"]), self.styles["JobTitle"])
                )

            # Company
            if position.get("company"):
                position_elements.append(
                    Paragraph(self._escape(position["company"]), self.styles["Company"])
                )

            # Dates and location
            date_location = []
            if position.get("duration"):
                date_location.append(self._escape(position["duration"]))
            if position.get("location"):
                date_location.append(self._escape(position["location"]))

            if date_location:
                position_elements.append(
                    Paragraph(" | ".join(date_location), self.styles["DateLocation"])
                )

            # Description
            if position.get("description"):
                formatted_desc = self._format_description(position["description"])
                position_elements.append(
                    Paragraph(formatted_desc, self.styles["Description"])
                )

            # Missions (for consultants with nested client missions)
            if position.get("missions"):
                for mission in position["missions"]:
                    # Add spacing before mission
                    position_elements.append(Spacer(1, 2 * mm))

                    # Mission client name (as a sub-header)
                    client_name = self._escape(mission.get("client", "Client"))
                    mission_header = f"→ Mission chez {client_name}"
                    position_elements.append(
                        Paragraph(mission_header, self.styles["MissionClient"])
                    )

                    # Mission title (if different from main title)
                    if mission.get("title"):
                        position_elements.append(
                            Paragraph(
                                self._escape(mission["title"]),
                                self.styles["MissionTitle"],
                            )
                        )

                    # Mission dates and location
                    mission_date_loc = []
                    if mission.get("duration"):
                        mission_date_loc.append(self._escape(mission["duration"]))
                    if mission.get("location"):
                        mission_date_loc.append(self._escape(mission["location"]))

                    if mission_date_loc:
                        position_elements.append(
                            Paragraph(
                                " | ".join(mission_date_loc),
                                self.styles["DateLocation"],
                            )
                        )

                    # Mission description
                    if mission.get("description"):
                        formatted_mission_desc = self._format_description(
                            mission["description"]
                        )
                        position_elements.append(
                            Paragraph(
                                formatted_mission_desc,
                                self.styles["MissionDescription"],
                            )
                        )

            # Add spacing between positions
            if i < len(positions) - 1:
                position_elements.append(Spacer(1, 4 * mm))

            # Flow freely — keepWithNext on header styles keeps title/company/dates together
            for el in position_elements:
                elements.append(el)

        elements.append(Spacer(1, 2 * mm))
        return elements

    def _build_education(self):
        """Build education section"""
        all_elements = []
        section_content = []

        # Add section header
        section_content.extend(self._create_section_header(self.labels["education"]))

        # Get visible education configuration
        visible_indices = self.config.get("education_visible")
        all_education = self.data.get("education", [])

        # If visible_indices is specified, filter education
        if visible_indices is not None:
            education = [
                all_education[i] for i in visible_indices if i < len(all_education)
            ]
        else:
            education = all_education

        for i, edu in enumerate(education):
            edu_elements = []

            # Degree
            degree_text = []
            if edu.get("degree"):
                degree_text.append(self._escape(edu["degree"]))
            if edu.get("field_of_study"):
                degree_text.append(self._escape(edu["field_of_study"]))

            if degree_text:
                edu_elements.append(
                    Paragraph(" - ".join(degree_text), self.styles["JobTitle"])
                )

            # School
            if edu.get("school"):
                edu_elements.append(
                    Paragraph(self._escape(edu["school"]), self.styles["Company"])
                )

            # Dates
            date_range = []
            if edu.get("start_date"):
                date_range.append(self._escape(edu["start_date"]))
            if edu.get("end_date"):
                date_range.append(self._escape(edu["end_date"]))

            if date_range:
                edu_elements.append(
                    Paragraph(" - ".join(date_range), self.styles["DateLocation"])
                )

            # Add spacing between education entries
            if i < len(education) - 1:
                edu_elements.append(Spacer(1, 4 * mm))

            # Add each education entry to section content
            section_content.extend(edu_elements)

        section_content.append(Spacer(1, 2 * mm))

        # Keep entire education section together
        if section_content:
            all_elements.append(KeepTogether(section_content))

        return all_elements

    def _build_skills(self):
        """Build skills section in a grid layout"""
        all_elements = []
        section_content = []

        # Add section header
        section_content.extend(self._create_section_header(self.labels["skills"]))

        skills = self.data.get("skills", [])

        # Create a 2-column or 3-column layout based on number of skills
        num_cols = 3 if len(skills) > 10 else 2

        # Group skills into columns
        skill_rows = []
        for i in range(0, len(skills), num_cols):
            row = []
            for j in range(num_cols):
                if i + j < len(skills):
                    row.append(
                        Paragraph(
                            f"- {self._escape(skills[i + j])}",
                            self.styles["SkillItem"],
                        )
                    )
                else:
                    row.append(Paragraph("", self.styles["SkillItem"]))
            skill_rows.append(row)

        # Create table
        if skill_rows:
            skill_table = Table(skill_rows, colWidths=[170 * mm / num_cols] * num_cols)
            skill_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 1),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                    ]
                )
            )
            section_content.append(skill_table)

        section_content.append(Spacer(1, 2 * mm))

        # Keep entire skills section together
        if section_content:
            all_elements.append(KeepTogether(section_content))

        return all_elements

    def _build_languages(self):
        """Build languages section"""
        all_elements = []
        section_content = []

        # Add section header
        section_content.extend(self._create_section_header(self.labels["languages"]))

        # Build language items
        for lang in self.data.get("languages", []):
            lang_text = f"<b>{self._escape(lang.get('name', ''))}</b>"
            if lang.get("proficiency"):
                lang_text += f" - {self._escape(lang['proficiency'])}"
            section_content.append(Paragraph(lang_text, self.styles["SkillItem"]))

        section_content.append(Spacer(1, 2 * mm))

        # Keep entire languages section together
        if section_content:
            all_elements.append(KeepTogether(section_content))

        return all_elements

    def _build_certifications(self):
        """Build certifications section"""
        all_elements = []
        section_content = []

        # Add section header
        section_content.extend(
            self._create_section_header(self.labels["certifications"])
        )

        # Build all certifications
        for i, cert in enumerate(self.data.get("certifications", [])):
            cert_elements = []

            # Certification name
            if cert.get("name"):
                cert_elements.append(
                    Paragraph(self._escape(cert["name"]), self.styles["JobTitle"])
                )

            # Authority
            if cert.get("authority"):
                cert_elements.append(
                    Paragraph(self._escape(cert["authority"]), self.styles["Company"])
                )

            # Date
            if cert.get("start_date"):
                date_text = self._escape(cert["start_date"])
                if cert.get("end_date"):
                    date_text += f" - {self._escape(cert['end_date'])}"
                cert_elements.append(Paragraph(date_text, self.styles["DateLocation"]))

            # Add spacing between certifications
            if i < len(self.data.get("certifications", [])) - 1:
                cert_elements.append(Spacer(1, 3 * mm))

            # Add certification elements to section
            section_content.extend(cert_elements)

        # Keep entire certifications section together
        if section_content:
            all_elements.append(KeepTogether(section_content))

        return all_elements
