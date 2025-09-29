import { http, HttpResponse } from 'msw';
import { usersDatabase, mockTokens, updateUserInDatabase, getUserByEmail } from './data';

// Variable para trackear el usuario actualmente logueado
let currentUserId: string | null = usersDatabase[0].id;

export const handlers = [
  // POST /api/users/login
  http.post('*/api/users/login', async ({ request }) => {
    const credentials = await request.json() as { email: string; password: string };
    
    // Buscar usuario por email y password
    const user = getUserByEmail(credentials.email);
    
    if (user && user.password === credentials.password) {
      // Establecer como usuario actual
      currentUserId = user.id;
      
      return HttpResponse.json({
        accessToken: mockTokens.accessToken,
        refreshToken: mockTokens.refreshToken,
        user: {
          id: user.id,
          name: user.name,
          email: user.email,
          createdAt: user.createdAt
        },
      });
    }
    
    return HttpResponse.json(
      { error: 'Credenciales inválidas' },
      { status: 401 }
    );
  }),

  // POST /api/users/refresh
  http.post('*/api/users/refresh', async () => {
    return HttpResponse.json({
      accessToken: 'new-mock-access-token-789',
      refreshToken: 'new-mock-refresh-token-012',
    });
  }),

  // GET /api/users/me
  http.get('*/api/users/me', async ({ request }) => {
    const authHeader = request.headers.get('Authorization');
    
    if ((authHeader === `Bearer ${mockTokens.accessToken}` || authHeader === 'Bearer new-mock-access-token-789') && currentUserId) {
      const user = usersDatabase.find(u => u.id === currentUserId);
      if (user) {
        return HttpResponse.json({
          id: user.id,
          name: user.name,
          email: user.email,
          createdAt: user.createdAt
        });
      }
    }
    
    return HttpResponse.json(
      { error: 'No autorizado' },
      { status: 401 }
    );
  }),

  http.put('*/api/users/me', async ({ request }) => {
    const authHeader = request.headers.get('Authorization');
    const updateData = await request.json() as { name: string };
    
    if ((authHeader === `Bearer ${mockTokens.accessToken}` || authHeader === 'Bearer new-mock-access-token-789') && currentUserId) {
      const updatedUser = updateUserInDatabase(currentUserId, { name: updateData.name });
      
      if (updatedUser) {
        return HttpResponse.json({
          id: updatedUser.id,
          name: updatedUser.name,
          email: updatedUser.email,
          createdAt: updatedUser.createdAt
        });
      }
    }
    
    return HttpResponse.json(
      { error: 'No autorizado' },
      { status: 401 }
    );
  }),
];