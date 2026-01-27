import { create } from 'zustand'
import api from '../api/client'

interface User {
  id: string
  email: string
  full_name: string
}

interface AuthState {
  token: string | null
  user: User | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('token'),
  user: null,

  login: async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password })
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refreshToken', data.refresh_token)
    set({ token: data.access_token })
  },

  register: async (email, password, fullName) => {
    const { data } = await api.post('/auth/register', { email, password, full_name: fullName })
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('refreshToken', data.refresh_token)
    set({ token: data.access_token })
  },

  logout: () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    set({ token: null, user: null })
  },

  fetchUser: async () => {
    const { data } = await api.get('/auth/me')
    set({ user: data })
  },
}))
