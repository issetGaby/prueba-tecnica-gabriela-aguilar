import { LoginCredentials, AuthResponse, RefreshResponse, User } from '@/types/auth';

// Interface para los usuarios del mock (incluye password)
interface MockUser {
  id: string;
  name: string;
  email: string;
  password: string;
  createdAt: string;
}

// Datos mock iniciales
const initialMockUsers: MockUser[] = [
  {
    id: '1',
    name: 'Gabriela Aguilar',
    email: 'gabriela.aguilar@linktic.com',
    password: 'password123',
    createdAt: '2025-09-28T09:37:00-05:00',
  },
  {
    id: '2', 
    name: 'Oury Santacruz',
    email: 'oury.santacruz@linktic.com',
    password: 'password',
    createdAt: '2024-01-15T10:30:00Z',
  },
  {
    id: '3', 
    name: 'Usuario Prueba',
    email: 'prueba@linktic.com',
    password: 'password',
    createdAt: '2024-01-15T10:30:00Z',
  },
];

class AuthService {
  private getUsersDatabase(): MockUser[] {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('mockUsersDatabase');
      if (stored) {
        return JSON.parse(stored) as MockUser[];
      }
    }
    return [...initialMockUsers];
  }

  private saveUsersDatabase(users: MockUser[]): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('mockUsersDatabase', JSON.stringify(users));
    }
  }

  private getCurrentUserFromStorage(): MockUser {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem('mockCurrentUser');
      if (stored) {
        return JSON.parse(stored) as MockUser;
      }
    }
    return { ...initialMockUsers[0] };
  }

  private saveCurrentUserToStorage(user: MockUser): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('mockCurrentUser', JSON.stringify(user));
    }
  }

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const usersDatabase = this.getUsersDatabase();
    const user = usersDatabase.find((u: MockUser) => 
      u.email === credentials.email && u.password === credentials.password
    );
    
    if (user) {
      this.saveCurrentUserToStorage(user);
      
      const response: AuthResponse = {
        accessToken: 'mock-access-token-123',
        refreshToken: 'mock-refresh-token-456',
        user: {
          id: user.id,
          name: user.name,
          email: user.email,
          createdAt: user.createdAt
        },
      };
      
      this.setTokens(response.accessToken, response.refreshToken);
      return response;
    }
    
    throw new Error('Credenciales inválidas');
  }

  async refreshToken(refreshToken: string): Promise<RefreshResponse> {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const response: RefreshResponse = {
      accessToken: 'new-mock-access-token-789',
      refreshToken: 'new-mock-refresh-token-012',
    };
    
    this.setTokens(response.accessToken, response.refreshToken);
    return response;
  }

  async getCurrentUser(accessToken: string): Promise<User> {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    if (!this.isValidToken(accessToken)) {
      throw new Error('Token inválido');
    }
    
    const currentUser = this.getCurrentUserFromStorage();
    
    return {
      id: currentUser.id,
      name: currentUser.name,
      email: currentUser.email,
      createdAt: currentUser.createdAt
    };
  }

  async updateUser(accessToken: string, userData: Partial<User>): Promise<User> {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    if (!this.isValidToken(accessToken)) {
      throw new Error('Token inválido');
    }
    
    const currentUser = this.getCurrentUserFromStorage();
    const usersDatabase = this.getUsersDatabase();
    
    const updatedCurrentUser: MockUser = {
      ...currentUser,
      ...userData
    };
    
    this.saveCurrentUserToStorage(updatedCurrentUser);
    
    const userIndex = usersDatabase.findIndex((u: MockUser) => u.id === currentUser.id);
    if (userIndex !== -1) {
      usersDatabase[userIndex] = {
        ...usersDatabase[userIndex],
        ...userData
      };
      this.saveUsersDatabase(usersDatabase);
    }
    
    return {
      id: updatedCurrentUser.id,
      name: updatedCurrentUser.name,
      email: updatedCurrentUser.email,
      createdAt: updatedCurrentUser.createdAt
    };
  }

  setTokens(accessToken: string, refreshToken: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      localStorage.setItem('tokenExpiry', (Date.now() + (15 * 60 * 1000)).toString());
    }
  }

  getAccessToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('accessToken');
    }
    return null;
  }

  getRefreshToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('refreshToken');
    }
    return null;
  }

  isTokenExpired(): boolean {
    if (typeof window !== 'undefined') {
      const expiry = localStorage.getItem('tokenExpiry');
      return expiry ? Date.now() > parseInt(expiry) : true;
    }
    return true;
  }

  clearTokens(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('tokenExpiry');
      localStorage.removeItem('mockCurrentUser');
    }
  }

  async getValidToken(): Promise<string | null> {
    const accessToken = this.getAccessToken();
    
    if (!accessToken) {
      return null;
    }

    if (!this.isTokenExpired()) {
      return accessToken;
    }

    try {
      const refreshToken = this.getRefreshToken();
      if (!refreshToken) {
        this.clearTokens();
        return null;
      }

      const { accessToken: newAccessToken, refreshToken: newRefreshToken } = await this.refreshToken(refreshToken);
      this.setTokens(newAccessToken, newRefreshToken);
      return newAccessToken;
    } catch (error) {
      this.clearTokens();
      return null;
    }
  }

  private isValidToken(token: string): boolean {
    const validTokens = [
      'mock-access-token-123',
      'new-mock-access-token-789'
    ];
    return validTokens.includes(token);
  }

  resetMockData(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('mockUsersDatabase');
      localStorage.removeItem('mockCurrentUser');
      this.clearTokens();
    }
  }
}

export const authService = new AuthService();