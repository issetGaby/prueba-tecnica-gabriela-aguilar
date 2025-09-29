import { MockUser, UserUpdate } from '@/types/mock';

export const usersDatabase: MockUser[] = [
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

export const mockTokens = {
  accessToken: 'mock-access-token-123',
  refreshToken: 'mock-refresh-token-456',
};

// Función para actualizar usuario en la "base de datos"
export const updateUserInDatabase = (userId: string, updates: UserUpdate): MockUser | null => {
  const userIndex = usersDatabase.findIndex(user => user.id === userId);
  if (userIndex !== -1) {
    usersDatabase[userIndex] = {
      ...usersDatabase[userIndex],
      ...updates
    };
    console.log('✅ Usuario actualizado en la base de datos:', usersDatabase[userIndex]);
    console.log('📊 Estado actual de usersDatabase:', usersDatabase);
    return usersDatabase[userIndex];
  }
  return null;
};
// Función para obtener usuario por email (para login)
export const getUserByEmail = (email: string): MockUser | undefined => {
  return usersDatabase.find(user => user.email === email);
};