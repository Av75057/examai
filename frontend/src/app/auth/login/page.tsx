"use client"

import { useState } from "react"
import { useAuth } from "@/lib/auth"
import Link from "next/link"

export default function LoginPage() {
  const { login } = useAuth()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(""); setLoading(true)
    try { await login(email, password) }
    catch (err) { setError(err instanceof Error ? err.message : "Ошибка входа") }
    finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm animate-slide-up">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">ExamAI</h1>
          <p className="text-slate-500 mt-1">Вход в аккаунт</p>
        </div>
        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-transparent transition" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">Пароль</label>
            <input type="password" value={password} onChange={e => setPassword(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-transparent transition" required />
          </div>
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full py-3.5 text-base">
            {loading ? "Входим..." : "Войти"}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-slate-500">
          Нет аккаунта? <Link href="/auth/register" className="text-indigo-600 font-semibold">Регистрация</Link>
        </p>
      </div>
    </div>
  )
}
