import csv
import os
from datetime import datetime

class LinkedInParser:
    """Parser for LinkedIn data export files"""

    def __init__(self, file_paths):
        self.file_paths = file_paths
        self.data = {
            'profile': {},
            'positions': [],
            'education': [],
            'skills': [],
            'languages': [],
            'certifications': []
        }

    def parse(self):
        """Parse all LinkedIn export files"""
        for filepath in self.file_paths:
            filename = os.path.basename(filepath).lower()

            if 'profile' in filename:
                self._parse_profile(filepath)
            elif 'position' in filename:
                self._parse_positions(filepath)
            elif 'education' in filename:
                self._parse_education(filepath)
            elif 'skill' in filename:
                self._parse_skills(filepath)
            elif 'language' in filename:
                self._parse_languages(filepath)
            elif 'certification' in filename:
                self._parse_certifications(filepath)
            elif 'email' in filename:
                self._parse_email_addresses(filepath)
            elif 'phone' in filename:
                self._parse_phone_numbers(filepath)

        return self.data

    def _parse_profile(self, filepath):
        """Parse Profile.csv"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    profile_data = {
                        'first_name': row.get('First Name', ''),
                        'last_name': row.get('Last Name', ''),
                        'maiden_name': row.get('Maiden Name', ''),
                        'headline': row.get('Headline', ''),
                        'summary': row.get('Summary', ''),
                        'address': row.get('Address', ''),
                        'geo_location': row.get('Geo Location', ''),
                        'email': row.get('Email Address', ''),
                        'phone': row.get('Phone Number', ''),
                        'birth_date': row.get('Birth Date', ''),
                        'websites': row.get('Websites', '').split(',') if row.get('Websites') else []
                    }

                    # Preserve existing email/phone if already set from Email Addresses.csv or PhoneNumbers.csv
                    if self.data['profile'].get('email'):
                        profile_data['email'] = self.data['profile']['email']
                    if self.data['profile'].get('phone'):
                        profile_data['phone'] = self.data['profile']['phone']

                    self.data['profile'] = profile_data
                    break  # Only first row
        except Exception as e:
            print(f"Error parsing profile: {e}")

    def _parse_positions(self, filepath):
        """Parse Positions.csv"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    position = {
                        'company': row.get('Company Name', ''),
                        'title': row.get('Title', ''),
                        'description': row.get('Description', ''),
                        'location': row.get('Location', ''),
                        'started_on': row.get('Started On', ''),
                        'finished_on': row.get('Finished On', ''),
                        'duration': self._format_date_range(
                            row.get('Started On', ''),
                            row.get('Finished On', '')
                        )
                    }
                    self.data['positions'].append(position)
        except Exception as e:
            print(f"Error parsing positions: {e}")

    def _parse_education(self, filepath):
        """Parse Education.csv"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    education = {
                        'school': row.get('School Name', ''),
                        'degree': row.get('Degree Name', ''),
                        'field_of_study': row.get('Notes', ''),
                        'start_date': row.get('Start Date', ''),
                        'end_date': row.get('End Date', ''),
                        'activities': row.get('Activities', '')
                    }
                    self.data['education'].append(education)
        except Exception as e:
            print(f"Error parsing education: {e}")

    def _parse_skills(self, filepath):
        """Parse Skills.csv"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    skill = row.get('Name', '')
                    if skill:
                        self.data['skills'].append(skill)
        except Exception as e:
            print(f"Error parsing skills: {e}")

    def _parse_languages(self, filepath):
        """Parse Languages.csv"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    language = {
                        'name': row.get('Name', ''),
                        'proficiency': row.get('Proficiency', '')
                    }
                    self.data['languages'].append(language)
        except Exception as e:
            print(f"Error parsing languages: {e}")

    def _parse_certifications(self, filepath):
        """Parse Certifications.csv"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cert = {
                        'name': row.get('Name', ''),
                        'authority': row.get('Authority', ''),
                        'start_date': row.get('Started On', ''),
                        'end_date': row.get('Finished On', ''),
                        'url': row.get('Url', '')
                    }
                    self.data['certifications'].append(cert)
        except Exception as e:
            print(f"Error parsing certifications: {e}")

    def _parse_email_addresses(self, filepath):
        """Parse Email Addresses.csv
        Format: Email Address,Confirmed,Primary,Updated On
        Example: ah.kouxxx@gmail.com,Yes,Yes,"4/9/18, 2:05 AM"
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                emails = []
                primary_email = None

                for row in reader:
                    email = row.get('Email Address', '').strip()
                    if email:
                        # Prioritize primary email
                        if row.get('Primary', '').lower() == 'yes':
                            primary_email = email
                        emails.append(email)

                # Use primary email first, otherwise first email
                # Always override existing email from Profile.csv if we have one from Email Addresses.csv
                if primary_email:
                    self.data['profile']['email'] = primary_email
                elif emails:
                    self.data['profile']['email'] = emails[0]

        except Exception as e:
            print(f"Error parsing email addresses: {e}")

    def _parse_phone_numbers(self, filepath):
        """Parse PhoneNumbers.csv and Whatsapp Phone Numbers.csv
        Format: Extension,Number,Type
        Example: , +33 6 00 00 06 02,
                 ,06*********,Mobile
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                phones = []
                mobile_phone = None

                for row in reader:
                    # Try different possible column names
                    phone = row.get('Number', '') or row.get('Phone Number', '') or row.get('PhoneNumber', '')
                    phone = phone.strip()

                    # Skip empty lines and masked numbers (with asterisks)
                    if phone and '*' not in phone:
                        # Prioritize mobile phone
                        phone_type = row.get('Type', '').strip().lower()
                        if phone_type == 'mobile':
                            mobile_phone = phone
                        phones.append(phone)

                # Use mobile phone first, otherwise first phone
                # Always override existing phone from Profile.csv if we have one from PhoneNumbers.csv
                if mobile_phone:
                    self.data['profile']['phone'] = mobile_phone
                elif phones:
                    self.data['profile']['phone'] = phones[0]

        except Exception as e:
            print(f"Error parsing phone numbers: {e}")

    def _format_date_range(self, start_date, end_date):
        """Format date range for display (e.g., '2020-01-01 - 2023-12-31' or '2020-01-01 - Présent')"""
        try:
            if not start_date:
                return ""

            # Format date range from LinkedIn date format (e.g., "2020-01-01")
            if end_date and end_date.lower() != 'present':
                return f"{start_date} - {end_date}"
            else:
                return f"{start_date} - Présent"
        except Exception:
            return ""
