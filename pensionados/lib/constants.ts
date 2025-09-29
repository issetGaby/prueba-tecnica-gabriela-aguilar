export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '/api';

export const ENDPOINTS = {
  LOGIN: '/users/login',
  REFRESH: '/users/refresh',
  ME: '/users/me',
} as const;

export const TOKEN_EXPIRY_TIME = 15 * 60 * 1000; // 15 minutos