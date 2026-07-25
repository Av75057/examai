"use client"

import { useState } from "react"
import { useAuth } from "@/lib/auth"
import Link from "next/link"

export default function RegisterPage() {
  const { register } = useAuth()
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [grade, setGrade] = useState(11)
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(""); setLoading(true)
    try { await register(email, password, name, grade) }
    catch (err) { setError(err instanceof Error ? err.message : "Ошибка регистрации") }
    finally { setLoading(false) }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="w-full max-w-sm animate-slide-up">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-extrabold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">ExamAI</h1>
          <p className="text-slate-500 mt-1">Создать аккаунт</p>
        </div>
        <form onSubmit={handleSubmit} className="card p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1">Имя</label>
            <input type="text" value={name} onChange={e => setName(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-transparent transition" required />
          </div>
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
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-2">Класс</label>
            <div className="grid grid-cols-7 gap-1.5">
              {[5,6,7,8,9,10,11].map(g => (
                <button key={g} type="button" onClick={() => setGrade(g)}
                  className={`py-2.5 rounded-xl text-sm font-bold transition ${
                    grade === g ? "bg-indigo-500 text-white shadow-lg shadow-indigo-200" : "bg-slate-50 text-slate-500 hover:bg-slate-100"
                  }`}>{g}</button>
              ))}
            </div>
            <p className="text-xs text-slate-400 mt-1.5">
              {grade === 9 ? "🎯 Подготовка к ОГЭ" : grade === 11 ? "🎓 Подготовка к ЕГЭ (профиль)" : `📚 Программа ${grade} класса`}
            </p>
          </div>
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full py-3.5 text-base">
            {loading ? "Создаём аккаунт..." : "Начать бесплатно"}
          </button>
        </form>
        <p className="mt-4 text-center text-sm text-slate-500">
          Уже есть аккаунт? <Link href="/auth/login" className="text-indigo-600 font-semibold">Войти</Link>
        </p>
      </div>
    </div>
  )
}
