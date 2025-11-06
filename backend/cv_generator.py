from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
import os
import tempfile

class CVGenerator:
    """Generate PDF CV from parsed LinkedIn data"""

    def __init__(self, data):
        self.data = data
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_CENTER
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#666666'),
            spaceAfter=12,
            alignment=TA_CENTER
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0073b1'),
            spaceAfter=8,
            spaceBefore=12,
            borderWidth=1,
            borderColor=colors.HexColor('#0073b1'),
            borderPadding=5,
            backColor=colors.HexColor('#f3f6f8')
        ))

        # Job title style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=2,
            fontName='Helvetica-Bold'
        ))

        # Company style
        self.styles.add(ParagraphStyle(
            name='Company',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#0073b1'),
            spaceAfter=2
        ))

        # Date style
        self.styles.add(ParagraphStyle(
            name='DateStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            spaceAfter=4
        ))

    def generate(self):
        """Generate the PDF CV"""
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf_path = temp_file.name
        temp_file.close()

        # Create PDF
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )

        # Build content
        story = []

        # Header section
        story.extend(self._build_header())

        # Summary section
        if self.data.get('profile', {}).get('summary'):
            story.extend(self._build_summary())

        # Experience section
        if self.data.get('positions'):
            story.extend(self._build_experience())

        # Education section
        if self.data.get('education'):
            story.extend(self._build_education())

        # Skills section
        if self.data.get('skills'):
            story.extend(self._build_skills())

        # Languages section
        if self.data.get('languages'):
            story.extend(self._build_languages())

        # Certifications section
        if self.data.get('certifications'):
            story.extend(self._build_certifications())

        # Build PDF
        doc.build(story)

        return pdf_path

    def _build_header(self):
        """Build header section with name and contact info"""
        elements = []
        profile = self.data.get('profile', {})

        # Full name
        full_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
        if full_name:
            elements.append(Paragraph(full_name, self.styles['CustomTitle']))

        # Headline
        if profile.get('headline'):
            elements.append(Paragraph(profile['headline'], self.styles['CustomSubtitle']))

        # Contact info
        contact_parts = []
        if profile.get('email'):
            contact_parts.append(profile['email'])
        if profile.get('phone'):
            contact_parts.append(profile['phone'])
        if profile.get('address'):
            contact_parts.append(profile['address'])

        if contact_parts:
            contact_text = ' | '.join(contact_parts)
            elements.append(Paragraph(contact_text, self.styles['CustomSubtitle']))

        elements.append(Spacer(1, 0.5*cm))

        return elements

    def _build_summary(self):
        """Build summary/about section"""
        elements = []
        profile = self.data.get('profile', {})

        elements.append(Paragraph("À PROPOS", self.styles['SectionHeader']))
        elements.append(Paragraph(profile['summary'], self.styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))

        return elements

    def _build_experience(self):
        """Build experience section"""
        elements = []

        elements.append(Paragraph("EXPÉRIENCE PROFESSIONNELLE", self.styles['SectionHeader']))

        for position in self.data.get('positions', []):
            # Job title
            if position.get('title'):
                elements.append(Paragraph(position['title'], self.styles['JobTitle']))

            # Company
            if position.get('company'):
                elements.append(Paragraph(position['company'], self.styles['Company']))

            # Dates and location
            date_location = []
            if position.get('duration'):
                date_location.append(position['duration'])
            if position.get('location'):
                date_location.append(position['location'])

            if date_location:
                elements.append(Paragraph(' | '.join(date_location), self.styles['DateStyle']))

            # Description
            if position.get('description'):
                elements.append(Paragraph(position['description'], self.styles['Normal']))

            elements.append(Spacer(1, 0.3*cm))

        return elements

    def _build_education(self):
        """Build education section"""
        elements = []

        elements.append(Paragraph("FORMATION", self.styles['SectionHeader']))

        for edu in self.data.get('education', []):
            # Degree
            degree_text = []
            if edu.get('degree'):
                degree_text.append(edu['degree'])
            if edu.get('field_of_study'):
                degree_text.append(edu['field_of_study'])

            if degree_text:
                elements.append(Paragraph(' - '.join(degree_text), self.styles['JobTitle']))

            # School
            if edu.get('school'):
                elements.append(Paragraph(edu['school'], self.styles['Company']))

            # Dates
            date_range = []
            if edu.get('start_date'):
                date_range.append(edu['start_date'])
            if edu.get('end_date'):
                date_range.append(edu['end_date'])

            if date_range:
                elements.append(Paragraph(' - '.join(date_range), self.styles['DateStyle']))

            elements.append(Spacer(1, 0.3*cm))

        return elements

    def _build_skills(self):
        """Build skills section"""
        elements = []

        elements.append(Paragraph("COMPÉTENCES", self.styles['SectionHeader']))

        skills = self.data.get('skills', [])
        skills_text = ' • '.join(skills)
        elements.append(Paragraph(skills_text, self.styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))

        return elements

    def _build_languages(self):
        """Build languages section"""
        elements = []

        elements.append(Paragraph("LANGUES", self.styles['SectionHeader']))

        for lang in self.data.get('languages', []):
            lang_text = lang.get('name', '')
            if lang.get('proficiency'):
                lang_text += f" - {lang['proficiency']}"
            elements.append(Paragraph(lang_text, self.styles['Normal']))

        elements.append(Spacer(1, 0.3*cm))

        return elements

    def _build_certifications(self):
        """Build certifications section"""
        elements = []

        elements.append(Paragraph("CERTIFICATIONS", self.styles['SectionHeader']))

        for cert in self.data.get('certifications', []):
            # Certification name
            if cert.get('name'):
                elements.append(Paragraph(cert['name'], self.styles['JobTitle']))

            # Authority
            if cert.get('authority'):
                elements.append(Paragraph(cert['authority'], self.styles['Company']))

            # Date
            if cert.get('start_date'):
                date_text = cert['start_date']
                if cert.get('end_date'):
                    date_text += f" - {cert['end_date']}"
                elements.append(Paragraph(date_text, self.styles['DateStyle']))

            elements.append(Spacer(1, 0.2*cm))

        return elements
