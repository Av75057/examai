"use client"

import { createContext, useContext, useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { api, setToken, clearToken, getToken } from "@/lib/api"
import type { User } from "@/types"

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string, grade?: number) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  login: async () => {},
  register: async () => {},
  logout: () => {},
})

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const token = getToken()
    if (token) {
      api.get<User>("/auth/me")
        .then(setUser)
        .catch(() => clearToken())
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const data = await api.post<{ access_token: string }>("/auth/login", { email, password })
    setToken(data.access_token)
    const userData = await api.get<User>("/auth/me")
    setUser(userData)
    const mastery = await api.get<any[]>("/tasks/mastery").catch(() => [])
    router.push(mastery.length > 0 ? "/dashboard" : "/diagnostic")
  }, [router])

  const register = useCallback(async (email: string, password: string, name: string, grade: number = 11) => {
    const data = await api.post<{ access_token: string }>("/auth/register", { email, password, name, grade })
    setToken(data.access_token)
    const userData = await api.get<User>("/auth/me")
    setUser(userData)
    router.push("/diagnostic")
  }, [router])

  const logout = useCallback(() => {
    clearToken()
    setUser(null)
    router.push("/")
  }, [router])

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
