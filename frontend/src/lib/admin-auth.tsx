"use client"

import { createContext, useContext, useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"

interface AdminUser {
  id: number
  email: string
  name: string
  role: string
}

interface AdminContextType {
  admin: AdminUser | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AdminContext = createContext<AdminContextType>({
  admin: null,
  loading: true,
  login: async () => {},
  logout: () => {},
})

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

async function apiCall<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("admin_token")
  const res = await fetch(`${API}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }))
    throw new Error(err.detail || "Request failed")
  }
  return res.json()
}

export const adminApi = {
  get: <T extends unknown>(e: string) => apiCall<T>(e),
  post: <T extends unknown>(e: string, d?: unknown) => apiCall<T>(e, { method: "POST", body: d ? JSON.stringify(d) : undefined }),
  put: <T extends unknown>(e: string, d?: unknown) => apiCall<T>(e, { method: "PUT", body: d ? JSON.stringify(d) : undefined }),
  delete: <T extends unknown>(e: string) => apiCall<T>(e, { method: "DELETE" }),
}

export function AdminAuthProvider({ children }: { children: React.ReactNode }) {
  const [admin, setAdmin] = useState<AdminUser | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem("admin_token")
    if (token) {
      apiCall<AdminUser>("/admin/auth/me")
        .then(setAdmin)
        .catch(() => localStorage.removeItem("admin_token"))
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const data = await apiCall<{ access_token: string; admin: AdminUser }>("/admin/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    })
    localStorage.setItem("admin_token", data.access_token)
    setAdmin(data.admin)
    router.push("/admin/dashboard")
  }, [router])

  const logout = useCallback(() => {
    localStorage.removeItem("admin_token")
    setAdmin(null)
    router.push("/admin/login")
  }, [router])

  return (
    <AdminContext.Provider value={{ admin, loading, login, logout }}>
      {children}
    </AdminContext.Provider>
  )
}

export const useAdmin = () => useContext(AdminContext)
