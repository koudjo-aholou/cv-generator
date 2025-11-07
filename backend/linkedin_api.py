"""
LinkedIn API Service
Gère l'authentification OAuth 2.0 et la récupération des données de profil LinkedIn
"""

import os
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LinkedInAPIService:
    """Service pour interagir avec l'API LinkedIn via OAuth 2.0"""

    # LinkedIn API endpoints
    OAUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    API_BASE_URL = "https://api.linkedin.com/v2"

    # Scopes nécessaires pour récupérer les données du profil
    # Note: LinkedIn a des restrictions strictes sur les scopes disponibles
    SCOPES = [
        'openid',
        'profile',
        'email',
        'w_member_social'  # Pour accéder au profil complet
    ]

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None):
        """
        Initialise le service LinkedIn API

        Args:
            client_id: Client ID de l'application LinkedIn
            client_secret: Client Secret de l'application LinkedIn
            redirect_uri: URI de redirection après authentification
        """
        self.client_id = client_id or os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('LINKEDIN_CLIENT_SECRET')
        self.redirect_uri = redirect_uri or os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:5000/api/linkedin/callback')

        if not self.client_id or not self.client_secret:
            logger.warning("LinkedIn credentials not configured. Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET")

    def get_authorization_url(self, state=None):
        """
        Génère l'URL d'autorisation OAuth LinkedIn

        Args:
            state: Token CSRF pour sécuriser la requête

        Returns:
            URL d'autorisation LinkedIn
        """
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.SCOPES)
        }

        if state:
            params['state'] = state

        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{self.OAUTH_URL}?{query_string}"

    def exchange_code_for_token(self, code):
        """
        Échange le code d'autorisation contre un access token

        Args:
            code: Code d'autorisation reçu de LinkedIn

        Returns:
            dict: Informations du token (access_token, expires_in, etc.)
        """
        try:
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }

            response = requests.post(
                self.TOKEN_URL,
                data=data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise

    def get_profile(self, access_token):
        """
        Récupère les informations de profil de l'utilisateur

        Args:
            access_token: Token d'accès LinkedIn

        Returns:
            dict: Données du profil au format standardisé
        """
        try:
            # Récupérer les informations de base du profil
            profile_data = self._get_basic_profile(access_token)

            # Récupérer l'email
            email_data = self._get_email(access_token)

            # Récupérer les positions (expérience professionnelle)
            # Note: Nécessite des permissions spéciales, peut ne pas être disponible
            positions_data = self._get_positions(access_token)

            # Récupérer l'éducation
            education_data = self._get_education(access_token)

            # Récupérer les compétences
            skills_data = self._get_skills(access_token)

            # Combiner toutes les données dans un format compatible avec le parser existant
            return self._format_data(
                profile_data,
                email_data,
                positions_data,
                education_data,
                skills_data
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching profile data: {e}")
            raise

    def _get_basic_profile(self, access_token):
        """Récupère les informations de base du profil"""
        headers = {'Authorization': f'Bearer {access_token}'}

        # API v2 - Profile endpoint
        response = requests.get(
            f"{self.API_BASE_URL}/me",
            headers=headers,
            params={
                'projection': '(id,firstName,lastName,headline,vanityName,profilePicture(displayImage~:playableStreams))'
            }
        )

        response.raise_for_status()
        return response.json()

    def _get_email(self, access_token):
        """Récupère l'adresse email"""
        headers = {'Authorization': f'Bearer {access_token}'}

        response = requests.get(
            f"{self.API_BASE_URL}/emailAddress?q=members&projection=(elements*(handle~))",
            headers=headers
        )

        response.raise_for_status()
        return response.json()

    def _get_positions(self, access_token):
        """
        Récupère les positions professionnelles
        Note: Cette API peut nécessiter des permissions spéciales
        """
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            # Essayer de récupérer les positions via l'API
            # Note: Cet endpoint peut ne pas être disponible pour toutes les applications
            response = requests.get(
                f"{self.API_BASE_URL}/me",
                headers=headers,
                params={
                    'projection': '(positions)'
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Positions endpoint returned {response.status_code}")
                return {'positions': {'values': []}}

        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not fetch positions: {e}")
            return {'positions': {'values': []}}

    def _get_education(self, access_token):
        """
        Récupère les informations d'éducation
        Note: Cette API peut nécessiter des permissions spéciales
        """
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            response = requests.get(
                f"{self.API_BASE_URL}/me",
                headers=headers,
                params={
                    'projection': '(educations)'
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Education endpoint returned {response.status_code}")
                return {'educations': {'values': []}}

        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not fetch education: {e}")
            return {'educations': {'values': []}}

    def _get_skills(self, access_token):
        """
        Récupère les compétences
        Note: Cette API peut nécessiter des permissions spéciales
        """
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            response = requests.get(
                f"{self.API_BASE_URL}/me",
                headers=headers,
                params={
                    'projection': '(skills)'
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Skills endpoint returned {response.status_code}")
                return {'skills': {'values': []}}

        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not fetch skills: {e}")
            return {'skills': {'values': []}}

    def _format_data(self, profile, email, positions, education, skills):
        """
        Formate les données de l'API LinkedIn dans un format compatible
        avec le LinkedInParser existant

        Args:
            profile: Données du profil
            email: Données email
            positions: Données des positions
            education: Données d'éducation
            skills: Données des compétences

        Returns:
            dict: Données formatées
        """
        # Extraire le prénom et nom (LinkedIn API v2 format)
        first_name = profile.get('firstName', {}).get('localized', {}).get('en_US', '') or \
                     profile.get('firstName', {}).get('localized', {}).get('fr_FR', '') or ''

        last_name = profile.get('lastName', {}).get('localized', {}).get('en_US', '') or \
                    profile.get('lastName', {}).get('localized', {}).get('fr_FR', '') or ''

        # Extraire l'email
        email_address = ''
        if email.get('elements') and len(email['elements']) > 0:
            email_handle = email['elements'][0].get('handle~', {})
            email_address = email_handle.get('emailAddress', '')

        # Formater le profil
        formatted_profile = {
            'first_name': first_name,
            'last_name': last_name,
            'maiden_name': '',
            'headline': profile.get('headline', ''),
            'summary': '',  # L'API v2 ne fournit pas le summary directement
            'address': '',
            'geo_location': '',
            'email': email_address,
            'phone': '',
            'birth_date': '',
            'websites': []
        }

        # Formater les positions
        formatted_positions = []
        positions_list = positions.get('positions', {}).get('values', [])
        for pos in positions_list:
            formatted_positions.append({
                'company': pos.get('companyName', ''),
                'title': pos.get('title', ''),
                'description': pos.get('summary', ''),
                'location': pos.get('location', {}).get('name', ''),
                'started_on': self._format_date(pos.get('startDate', {})),
                'finished_on': self._format_date(pos.get('endDate', {})) if pos.get('endDate') else '',
                'duration': self._calculate_duration(pos.get('startDate', {}), pos.get('endDate'))
            })

        # Formater l'éducation
        formatted_education = []
        education_list = education.get('educations', {}).get('values', [])
        for edu in education_list:
            formatted_education.append({
                'school': edu.get('schoolName', ''),
                'degree': edu.get('degreeName', ''),
                'field_of_study': edu.get('fieldOfStudy', ''),
                'start_date': self._format_date(edu.get('startDate', {})),
                'end_date': self._format_date(edu.get('endDate', {})) if edu.get('endDate') else '',
                'activities': ''
            })

        # Formater les compétences
        formatted_skills = []
        skills_list = skills.get('skills', {}).get('values', [])
        for skill in skills_list:
            skill_name = skill.get('name', {}).get('localized', {}).get('en_US', '') or \
                        skill.get('name', {}).get('localized', {}).get('fr_FR', '') or ''
            if skill_name:
                formatted_skills.append(skill_name)

        return {
            'profile': formatted_profile,
            'positions': formatted_positions,
            'education': formatted_education,
            'skills': formatted_skills,
            'languages': [],
            'certifications': []
        }

    def _format_date(self, date_obj):
        """
        Formate un objet date LinkedIn en chaîne

        Args:
            date_obj: Objet date de l'API LinkedIn (ex: {'year': 2020, 'month': 1})

        Returns:
            str: Date formatée (ex: '2020-01')
        """
        if not date_obj:
            return ''

        year = date_obj.get('year', '')
        month = date_obj.get('month', '')

        if year and month:
            return f"{year}-{month:02d}"
        elif year:
            return str(year)

        return ''

    def _calculate_duration(self, start_date, end_date):
        """
        Calcule la durée entre deux dates

        Args:
            start_date: Date de début
            end_date: Date de fin (None si en cours)

        Returns:
            str: Durée formatée
        """
        start = self._format_date(start_date)
        end = self._format_date(end_date) if end_date else 'Présent'

        if start:
            return f"{start} - {end}"

        return ''
