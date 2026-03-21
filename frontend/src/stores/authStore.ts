import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  username: string
  email?: string
}

interface AuthState {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,

      login: async (username: string, password: string) => {
        const response = await fetch('/api/v1/auth/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ username, password }),
        })

        if (!response.ok) {
          const data = await response.json().catch(() => ({}))
          throw new Error(data.detail || 'Login failed')
        }

        const data = await response.json()

        if (data.access_token) {
          set({ accessToken: data.access_token, isAuthenticated: true })
          localStorage.setItem('auth_token', data.access_token)
        }
      },

      logout: () => {
        set({ user: null, accessToken: null, isAuthenticated: false })
        localStorage.removeItem('auth_token')
        localStorage.removeItem('user')
      },

      setUser: (user: User) => {
        set({ user })
        localStorage.setItem('user', JSON.stringify(user))
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)