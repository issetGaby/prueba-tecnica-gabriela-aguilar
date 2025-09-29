export interface MockUser {
  id: string;
  name: string;
  email: string;
  password: string;
  createdAt: string;
}

export interface UserUpdate {
  name?: string;
  email?: string;
}