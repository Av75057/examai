"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth"
import { api } from "@/lib/api"
import type { Mastery, ExamAttempt } from "@/types"
import Link from "next/link"

export default function ProfilePage() {
  const { user, loading, logout } = useAuth()
  const router = useRouter()
  const [mastery, setMastery] = useState<Mastery[]>([])
  const [exams, setExams] = useState<ExamAttempt[]>([])
  const [editingGrade, setEditingGrade] = useState(false)
  const [newGrade, setNewGrade] = useState(user?.grade || 11)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (!loading && !user) {
      router.push("/")
    }
  }, [user, loading, router])

  useEffect(() => {
    if (!user) return
    setNewGrade(user.grade || 11)
    api.get<Mastery[]>("/tasks/mastery").then(setMastery).catch(() => {})
    api.get<ExamAttempt[]>("/exams/history").then(setExams).catch(() => {})
  }, [user])

  const saveGrade = async () => {
    setSaving(true)
    try {
      await api.patch("/auth/me", { grade: newGrade })
      window.location.reload()
    } catch (e) {
      console.error(e)
    } finally {
      setSaving(false)
    }
  }

  if (loading || !user) {
    return <div className="flex items-center justify-center min-h-screen">Загрузка...</div>
  }

  const avgMastery = mastery.length > 0
    ? mastery.reduce((sum, m) => sum + m.score, 0) / mastery.length
    : 0

  return (
    <div className="min-h-screen p-4 max-w-lg mx-auto pb-20">
      <div className="flex items-center justify-between mb-6">
        <button onClick={() => router.push("/dashboard")} className="text-gray-400">
          ← Назад
        </button>
        <button onClick={logout} className="text-danger text-sm font-medium">
          Выйти
        </button>
      </div>

      <div className="bg-white p-6 rounded-2xl border border-gray-100 mb-6">
        <h2 className="text-xl font-bold">{user.name}</h2>
        <p className="text-gray-500 text-sm">{user.email}</p>
        <div className="flex gap-3 mt-3 flex-wrap">
          <span className="text-xs bg-primary/10 text-primary px-3 py-1 rounded-full font-medium">
            {user.subscription === "premium" ? "Premium" : "Free"}
          </span>
          <span className="text-xs bg-orange-100 text-orange-700 px-3 py-1 rounded-full font-medium">
            Серия: {user.streak_days} дн
          </span>
          {editingGrade ? (
            <div className="flex items-center gap-2">
              <select value={newGrade} onChange={e => setNewGrade(parseInt(e.target.value))} className="text-xs border rounded px-2 py-1">
                {[5,6,7,8,9,10,11].map(g => <option key={g} value={g}>{g} класс</option>)}
              </select>
              <button onClick={saveGrade} disabled={saving} className="text-xs bg-green-500 text-white px-2 py-1 rounded">{saving ? "..." : "✓"}</button>
              <button onClick={() => setEditingGrade(false)} className="text-xs text-gray-400">✕</button>
            </div>
          ) : (
            <button onClick={() => setEditingGrade(true)} className="text-xs bg-gray-100 text-gray-600 px-3 py-1 rounded-full font-medium hover:bg-gray-200">
              {user.grade || 11} класс ✎
            </button>
          )}
        </div>
      </div>

      <div className="bg-white p-4 rounded-2xl border border-gray-100 mb-4">
        <h3 className="font-semibold mb-2">Прогресс по темам</h3>
        <div className="mb-2">
          <div className="flex justify-between text-sm mb-1">
            <span>Общий уровень</span>
            <span>{Math.round(avgMastery * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary h-2 rounded-full transition-all"
              style={{ width: `${avgMastery * 100}%` }}
            />
          </div>
        </div>

        {mastery.slice(0, 10).map((m) => (
          <div key={m.topic_code} className="flex justify-between items-center py-1.5 border-t border-gray-50">
            <span className="text-sm">{m.topic_name}</span>
            <span className="text-sm font-medium">{Math.round(m.score * 100)}%</span>
          </div>
        ))}
      </div>

      <div className="bg-white p-4 rounded-2xl border border-gray-100 mb-4">
        <h3 className="font-semibold mb-2">История пробников</h3>
        {exams.length === 0 ? (
          <p className="text-sm text-gray-400">Ещё не было пробников</p>
        ) : (
          exams.map((exam) => (
            <div key={exam.id} className="flex justify-between py-1.5 border-t border-gray-50 text-sm">
              <span>{new Date(exam.started_at).toLocaleDateString("ru")}</span>
              <span className="font-medium">
                {exam.test_score !== null ? `${exam.test_score} баллов` : "Не завершён"}
              </span>
            </div>
          ))
        )}
      </div>

      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 py-3 px-6 flex justify-between max-w-lg mx-auto rounded-t-2xl">
        <Link href="/dashboard" className="text-gray-400 text-sm">Главная</Link>
        <Link href="/errors" className="text-gray-400 text-sm">Ошибки</Link>
        <Link href="/exam" className="text-gray-400 text-sm">Пробник</Link>
        <Link href="/profile" className="text-primary font-medium text-sm">Прогресс</Link>
      </nav>
    </div>
  )
}
