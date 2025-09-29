import { authService } from '@/services/auth-service';

export async function refreshAuthToken(): Promise<boolean> {
  try {
    const refreshToken = authService.getRefreshToken();
    if (!refreshToken) {
      return false;
    }

    const { accessToken, refreshToken: newRefreshToken } = await authService.refreshToken(refreshToken);
    authService.setTokens(accessToken, newRefreshToken);
    return true;
  } catch (error) {
    authService.clearTokens();
    return false;
  }
}

export async function getValidToken(): Promise<string | null> {
  return authService.getValidToken();
}

export function isAuthenticated(): boolean {
  const accessToken = authService.getAccessToken();
  return !!accessToken && !authService.isTokenExpired();
}