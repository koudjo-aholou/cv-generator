from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, HRFlowable, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import tempfile
import base64
from io import BytesIO

class CVGenerator:
    """Generate PDF CV from parsed LinkedIn data"""

    def __init__(self, data):
        self.data = data
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""

        # Name style - Bold and large
        self.styles.add(ParagraphStyle(
            name='Name',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=4,
            spaceBefore=0,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            leading=32
        ))

        # Headline style
        self.styles.add(ParagraphStyle(
            name='Headline',
            parent=self.styles['Normal'],
            fontSize=13,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            fontName='Helvetica',
            leading=16
        ))

        # Contact style
        self.styles.add(ParagraphStyle(
            name='Contact',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=16,
            fontName='Helvetica',
            leading=14
        ))

        # Section header style - Clean with underline
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            spaceBefore=16,
            fontName='Helvetica-Bold',
            leading=18,
            textTransform='uppercase'
        ))

        # Job title style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=3,
            fontName='Helvetica-Bold',
            leading=14
        ))

        # Company style
        self.styles.add(ParagraphStyle(
            name='Company',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#3498db'),
            spaceAfter=3,
            fontName='Helvetica-Oblique',
            leading=13
        ))

        # Date/Location style
        self.styles.add(ParagraphStyle(
            name='DateLocation',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#95a5a6'),
            spaceAfter=6,
            fontName='Helvetica',
            leading=12
        ))

        # Description style
        self.styles.add(ParagraphStyle(
            name='Description',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=0,
            fontName='Helvetica',
            leading=14,
            alignment=TA_JUSTIFY
        ))

        # Summary style
        self.styles.add(ParagraphStyle(
            name='Summary',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=0,
            fontName='Helvetica',
            leading=15,
            alignment=TA_JUSTIFY
        ))

        # Skill item style
        self.styles.add(ParagraphStyle(
            name='SkillItem',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=0,
            fontName='Helvetica',
            leading=13
        ))

    def generate(self):
        """Generate the PDF CV"""
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf_path = temp_file.name
        temp_file.close()

        # Create PDF with better margins
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
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

    def _create_section_header(self, title):
        """Create a section header with horizontal line"""
        elements = []
        elements.append(Paragraph(title.upper(), self.styles['SectionHeader']))
        elements.append(HRFlowable(
            width="100%",
            thickness=1,
            color=colors.HexColor('#3498db'),
            spaceBefore=0,
            spaceAfter=10
        ))
        return elements

    def _build_header(self):
        """Build header section with name, contact info, and photo"""
        elements = []
        profile = self.data.get('profile', {})

        # Check if we have a photo
        has_photo = self.data.get('photo') is not None

        if has_photo:
            # Build header with photo using table layout
            info_elements = []

            # Full name
            full_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
            if full_name:
                info_elements.append(Paragraph(full_name, self.styles['Name']))

            # Headline
            if profile.get('headline'):
                info_elements.append(Paragraph(profile['headline'], self.styles['Headline']))

            # Contact info
            contact_lines = []

            line1_parts = []
            if profile.get('email'):
                line1_parts.append(f"✉ {profile['email']}")
            if profile.get('phone'):
                line1_parts.append(f"☎ {profile['phone']}")

            if line1_parts:
                contact_lines.append(' • '.join(line1_parts))

            if profile.get('address'):
                contact_lines.append(f"📍 {profile['address']}")

            for line in contact_lines:
                info_elements.append(Paragraph(line, self.styles['Contact']))

            # Create photo image
            photo_img = self._create_photo_image()

            # Create table with info on left and photo on right
            header_table = Table([[info_elements, photo_img]], colWidths=[130*mm, 40*mm])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('TOPPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
            ]))

            elements.append(header_table)

        else:
            # Build header without photo (original layout)
            # Full name
            full_name = f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
            if full_name:
                elements.append(Paragraph(full_name, self.styles['Name']))

            # Headline
            if profile.get('headline'):
                elements.append(Paragraph(profile['headline'], self.styles['Headline']))

            # Contact info on multiple lines for better readability
            contact_lines = []

            line1_parts = []
            if profile.get('email'):
                line1_parts.append(f"✉ {profile['email']}")
            if profile.get('phone'):
                line1_parts.append(f"☎ {profile['phone']}")

            if line1_parts:
                contact_lines.append(' • '.join(line1_parts))

            if profile.get('address'):
                contact_lines.append(f"📍 {profile['address']}")

            for line in contact_lines:
                elements.append(Paragraph(line, self.styles['Contact']))

        elements.append(Spacer(1, 4*mm))

        return elements

    def _create_photo_image(self):
        """Create photo image from base64 data"""
        try:
            photo_data = self.data.get('photo', '')

            # Remove data URL prefix if present
            if 'base64,' in photo_data:
                photo_data = photo_data.split('base64,')[1]

            # Decode base64
            image_data = base64.b64decode(photo_data)

            # Create image from bytes
            img = Image(BytesIO(image_data), width=35*mm, height=35*mm)

            return img

        except Exception as e:
            print(f"Error loading photo: {e}")
            return Paragraph("", self.styles['Normal'])

    def _build_summary(self):
        """Build summary/about section"""
        elements = []
        profile = self.data.get('profile', {})

        elements.extend(self._create_section_header("À Propos"))

        summary_para = Paragraph(profile['summary'], self.styles['Summary'])
        elements.append(KeepTogether([summary_para, Spacer(1, 4*mm)]))

        return elements

    def _build_experience(self):
        """Build experience section"""
        elements = []

        elements.extend(self._create_section_header("Expérience Professionnelle"))

        for i, position in enumerate(self.data.get('positions', [])):
            position_elements = []

            # Job title
            if position.get('title'):
                position_elements.append(Paragraph(position['title'], self.styles['JobTitle']))

            # Company
            if position.get('company'):
                position_elements.append(Paragraph(position['company'], self.styles['Company']))

            # Dates and location
            date_location = []
            if position.get('duration'):
                date_location.append(position['duration'])
            if position.get('location'):
                date_location.append(position['location'])

            if date_location:
                position_elements.append(Paragraph(' • '.join(date_location), self.styles['DateLocation']))

            # Description
            if position.get('description'):
                position_elements.append(Paragraph(position['description'], self.styles['Description']))

            # Add spacing between positions
            if i < len(self.data.get('positions', [])) - 1:
                position_elements.append(Spacer(1, 4*mm))

            # Keep each position together
            elements.append(KeepTogether(position_elements))

        elements.append(Spacer(1, 2*mm))
        return elements

    def _build_education(self):
        """Build education section"""
        elements = []

        elements.extend(self._create_section_header("Formation"))

        for i, edu in enumerate(self.data.get('education', [])):
            edu_elements = []

            # Degree
            degree_text = []
            if edu.get('degree'):
                degree_text.append(edu['degree'])
            if edu.get('field_of_study'):
                degree_text.append(edu['field_of_study'])

            if degree_text:
                edu_elements.append(Paragraph(' - '.join(degree_text), self.styles['JobTitle']))

            # School
            if edu.get('school'):
                edu_elements.append(Paragraph(edu['school'], self.styles['Company']))

            # Dates
            date_range = []
            if edu.get('start_date'):
                date_range.append(edu['start_date'])
            if edu.get('end_date'):
                date_range.append(edu['end_date'])

            if date_range:
                edu_elements.append(Paragraph(' - '.join(date_range), self.styles['DateLocation']))

            # Add spacing between education entries
            if i < len(self.data.get('education', [])) - 1:
                edu_elements.append(Spacer(1, 4*mm))

            # Keep each education entry together
            elements.append(KeepTogether(edu_elements))

        elements.append(Spacer(1, 2*mm))
        return elements

    def _build_skills(self):
        """Build skills section in a grid layout"""
        all_elements = []
        section_content = []

        # Add section header
        section_content.extend(self._create_section_header("Compétences"))

        skills = self.data.get('skills', [])

        # Create a 2-column or 3-column layout based on number of skills
        num_cols = 3 if len(skills) > 10 else 2

        # Group skills into columns
        skill_rows = []
        for i in range(0, len(skills), num_cols):
            row = []
            for j in range(num_cols):
                if i + j < len(skills):
                    row.append(Paragraph(f"• {skills[i + j]}", self.styles['SkillItem']))
                else:
                    row.append(Paragraph("", self.styles['SkillItem']))
            skill_rows.append(row)

        # Create table
        if skill_rows:
            skill_table = Table(skill_rows, colWidths=[170*mm/num_cols]*num_cols)
            skill_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 1),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ]))
            section_content.append(skill_table)

        section_content.append(Spacer(1, 2*mm))

        # Keep entire skills section together
        if section_content:
            all_elements.append(KeepTogether(section_content))

        return all_elements

    def _build_languages(self):
        """Build languages section"""
        all_elements = []
        section_content = []

        # Add section header
        section_content.extend(self._create_section_header("Langues"))

        # Build language items
        for lang in self.data.get('languages', []):
            lang_text = f"<b>{lang.get('name', '')}</b>"
            if lang.get('proficiency'):
                lang_text += f" - {lang['proficiency']}"
            section_content.append(Paragraph(lang_text, self.styles['SkillItem']))

        section_content.append(Spacer(1, 2*mm))

        # Keep entire languages section together
        if section_content:
            all_elements.append(KeepTogether(section_content))

        return all_elements

    def _build_certifications(self):
        """Build certifications section"""
        all_elements = []
        section_content = []

        # Add section header
        section_content.extend(self._create_section_header("Certifications"))

        # Build all certifications
        for i, cert in enumerate(self.data.get('certifications', [])):
            cert_elements = []

            # Certification name
            if cert.get('name'):
                cert_elements.append(Paragraph(cert['name'], self.styles['JobTitle']))

            # Authority
            if cert.get('authority'):
                cert_elements.append(Paragraph(cert['authority'], self.styles['Company']))

            # Date
            if cert.get('start_date'):
                date_text = cert['start_date']
                if cert.get('end_date'):
                    date_text += f" - {cert['end_date']}"
                cert_elements.append(Paragraph(date_text, self.styles['DateLocation']))

            # Add spacing between certifications
            if i < len(self.data.get('certifications', [])) - 1:
                cert_elements.append(Spacer(1, 3*mm))

            # Add certification elements to section
            section_content.extend(cert_elements)

        # Keep entire certifications section together
        if section_content:
            all_elements.append(KeepTogether(section_content))

        return all_elements
