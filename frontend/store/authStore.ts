import { create } from 'zustand'
import Cookies from 'js-cookie'
import api from '@/lib/api'

interface User {
  id: number
  email: string
  full_name: string
  role: string
  is_active: boolean
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,

  login: async (email: string, password: string) => {
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)

    const response = await api.post('/auth/login', params.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })

    const { access_token } = response.data
    Cookies.set('access_token', access_token, { expires: 1 })

    const userResponse = await api.get('/auth/me')
    set({ user: userResponse.data, isAuthenticated: true })
  },

  logout: () => {
    Cookies.remove('access_token')
    set({ user: null, isAuthenticated: false })
  },

  checkAuth: async () => {
    const token = Cookies.get('access_token')
    if (!token) {
      set({ isAuthenticated: false, user: null })
      return
    }

    try {
      const response = await api.get('/auth/me')
      set({ user: response.data, isAuthenticated: true })
    } catch (error) {
      Cookies.remove('access_token')
      set({ isAuthenticated: false, user: null })
    }
  },
}))
