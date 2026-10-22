import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { TokenData } from '../types/auth'
import { api } from '../api/client'

interface AuthContextType {
  user: TokenData | null
  loading: boolean
  login: () => Promise<void>
  logout: () => Promise<void>
  demoLogin: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<TokenData | null>(null)
  const [loading, setLoading] = useState(false)

  const refreshUser = async () => {
    try {
      const response = await api.get<TokenData>('/auth/me')
      setUser(response.data)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refreshUser()
  }, [])

  const login = async () => {
    window.location.href = '/auth/login'
  }

  const demoLogin = async () => {
    await api.post('/auth/demo-login')
    await refreshUser()
  }

  const logout = async () => {
    await api.post('/auth/logout')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, demoLogin, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}