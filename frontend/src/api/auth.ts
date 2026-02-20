import client from './client'
import type { User } from '../types'

export interface LoginPayload { email: string; password: string }
export interface RegisterPayload { email: string; name: string; password: string }
export interface AuthResponse { token: string; user: User }

export const authApi = {
  login: (payload: LoginPayload) =>
    client.post<AuthResponse>('/auth/login', payload).then((r) => r.data),

  register: (payload: RegisterPayload) =>
    client.post<AuthResponse>('/auth/register', payload).then((r) => r.data),

  me: () => client.get<User>('/auth/me').then((r) => r.data),
}
