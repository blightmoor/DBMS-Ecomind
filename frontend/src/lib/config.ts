// API Configuration

// For local development:
export const API_BASE_URL = 'http://localhost:8000/api';

// For production (requires tunnel to be public/anonymous):
// export const API_BASE_URL = 'https://06g9527r-8000.inc1.devtunnels.ms/api';
// export const API_BASE_URL = 'https://uncheerfully-unfulfilled-arlene.ngrok-free.dev/api';

// You can also add other configuration values here
export const config = {
    apiUrl: API_BASE_URL,
    appName: 'CarbonTrack',
    version: '1.0.0'
};
