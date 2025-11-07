/**
 * LinkedIn OAuth Service
 * Gère l'authentification LinkedIn et la récupération des données du profil
 */

import { API_URL } from '../../config/constants.js';
import { notifications } from '../../core/ui/notifications.js';

class LinkedInService {
    constructor() {
        this.accessToken = null;
        this.profileData = null;
    }

    /**
     * Vérifie si l'utilisateur est connecté à LinkedIn
     */
    isAuthenticated() {
        return this.accessToken !== null;
    }

    /**
     * Initie le flux d'authentification OAuth LinkedIn
     */
    async initiateAuth() {
        try {
            const response = await fetch(`${API_URL}/api/linkedin/auth`, {
                method: 'GET',
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Impossible d\'initier l\'authentification LinkedIn');
            }

            const data = await response.json();

            // Stocker le state pour validation
            sessionStorage.setItem('linkedin_oauth_state', data.state);

            // Rediriger vers l'URL d'autorisation LinkedIn
            window.location.href = data.auth_url;

        } catch (error) {
            console.error('Erreur lors de l\'initiation de l\'authentification:', error);
            notifications.showError('Impossible de se connecter à LinkedIn. Vérifiez votre configuration.');
            throw error;
        }
    }

    /**
     * Vérifie si l'authentification a réussi après redirection
     * À appeler au chargement de la page
     */
    checkAuthCallback() {
        const urlParams = new URLSearchParams(window.location.search);
        const authStatus = urlParams.get('linkedin_auth');

        if (authStatus === 'success') {
            notifications.showSuccess('Connexion LinkedIn réussie !');

            // Nettoyer l'URL
            window.history.replaceState({}, document.title, window.location.pathname);

            return true;
        }

        return false;
    }

    /**
     * Récupère les données du profil LinkedIn
     * @param {string} accessToken - Token d'accès (optionnel si déjà stocké)
     */
    async getProfile(accessToken = null) {
        try {
            const token = accessToken || this.accessToken;

            const headers = {
                'Content-Type': 'application/json'
            };

            // Si on a un token, l'envoyer dans le header
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(`${API_URL}/api/linkedin/profile`, {
                method: 'GET',
                headers: headers,
                credentials: 'include'
            });

            if (!response.ok) {
                if (response.status === 401) {
                    throw new Error('Non authentifié. Veuillez vous connecter à LinkedIn.');
                }
                throw new Error('Impossible de récupérer les données du profil');
            }

            const profileData = await response.json();

            // Stocker les données
            this.profileData = profileData;
            if (token) {
                this.accessToken = token;
            }

            return profileData;

        } catch (error) {
            console.error('Erreur lors de la récupération du profil:', error);
            notifications.showError(error.message || 'Impossible de récupérer les données LinkedIn');
            throw error;
        }
    }

    /**
     * Déconnecte l'utilisateur LinkedIn
     */
    async logout() {
        try {
            const response = await fetch(`${API_URL}/api/linkedin/logout`, {
                method: 'POST',
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Erreur lors de la déconnexion');
            }

            // Nettoyer les données locales
            this.accessToken = null;
            this.profileData = null;
            sessionStorage.removeItem('linkedin_oauth_state');

            notifications.showSuccess('Déconnexion réussie');

        } catch (error) {
            console.error('Erreur lors de la déconnexion:', error);
            notifications.showError('Erreur lors de la déconnexion');
            throw error;
        }
    }

    /**
     * Récupère les données du profil stockées localement
     */
    getCachedProfile() {
        return this.profileData;
    }

    /**
     * Vérifie si les credentials LinkedIn sont configurés
     */
    async checkConfiguration() {
        try {
            const response = await fetch(`${API_URL}/api/linkedin/auth`, {
                method: 'GET',
                credentials: 'include'
            });

            return response.ok;

        } catch (error) {
            console.error('LinkedIn API non configurée:', error);
            return false;
        }
    }
}

export const linkedinService = new LinkedInService();
