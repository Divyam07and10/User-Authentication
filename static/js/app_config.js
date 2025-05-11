// static/js/app_config.js

// This file defines frontend-specific configurations.
// It's included in google_login.html before other scripts that need these values.

window.APP_CONFIG = {
    // API_BASE_URL: The base URL of your FastAPI backend.
    // Change this value for different environments (development, staging, production).

    // For local development:
    API_BASE_URL: 'http://localhost:8000'

    // For a production environment, it might look like:
    // API_BASE_URL: 'https://your-production-domain.com'

    // For a staging environment, it might look like:
    // API_BASE_URL: 'https://staging.your-production-domain.com'
};

// You can add other frontend configurations here if needed, for example:
// window.APP_CONFIG.GOOGLE_ANALYTICS_ID = 'UA-XXXXX-Y';
