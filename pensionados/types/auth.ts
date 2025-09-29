// Tipos principales de autenticación
export interface User {
  id: string;
  name: string;
  email: string;
  createdAt: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  user: User;
}

export interface RefreshResponse {
  accessToken: string;
  refreshToken: string;
}

// Tipos para los mocks
export interface MockUser extends User {
  password: string;
}

export interface UserUpdate {
  name?: string;
  email?: string;
}