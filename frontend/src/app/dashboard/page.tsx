"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth"
import { api } from "@/lib/api"
import type { Task, Mastery } from "@/types"
import Link from "next/link"
import { MixedText } from "@/components/Latex"

interface ProgressData {
  total_answers: number
  accuracy: number
  total_sessions: number
  avg_mastery: number
  topics_mastered: number
  total_topics: number
}

export default function DashboardPage() {
  const { user, loading, logout } = useAuth()
  const router = useRouter()
  const [tasks, setTasks] = useState<Task[]>([])
  const [mastery, setMastery] = useState<Mastery[]>([])
  const [streak, setStreak] = useState(0)
  const [progress, setProgress] = useState<ProgressData | null>(null)
  const [isStarting, setIsStarting] = useState(false)
  const [limit, setLimit] = useState<{ remaining: number; limit: number; is_premium: boolean } | null>(null)

  const loadData = useCallback(() => {
    if (!user) return
    api.get<Mastery[]>("/tasks/mastery")
      .then(d => { setMastery(d); if (d.length === 0) router.push("/diagnostic") })
      .catch(() => {})
    api.get<{ streak: number }>("/progress/streak")
      .then(d => setStreak(d.streak))
      .catch(() => {})
    api.get<ProgressData>("/progress/overview")
      .then(setProgress)
      .catch(() => {})
    api.get<{ remaining: number; limit: number; is_premium: boolean }>("/tasks/limits")
      .then(setLimit)
      .catch(() => {})
  }, [user, router])

  useEffect(() => {
    if (!loading && !user) { router.push("/"); return }
    loadData()
  }, [user, loading, router, loadData])

  const startSession = async () => {
    setIsStarting(true)
    try {
      const data = await api.get<Task[]>("/tasks/session")
      if (data.length === 0) return
      const ids = data.map(t => t.id).join(",")
      router.push(`/solve/${data[0].id}?session=${ids}&idx=0`)
    } catch (err) {
      console.error(err)
    } finally {
      setIsStarting(false)
    }
  }

  if (loading || !user) {
    return <div className="flex items-center justify-center min-h-screen">Загрузка...</div>
  }

  const masteryTop = [...mastery].sort((a, b) => b.score - a.score).slice(0, 8)

  return (
    <div className="min-h-screen p-4 max-w-lg mx-auto pb-24">
      <header className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-xl font-bold">Привет, {user.name}</h1>
          <p className="text-sm text-gray-500">
            {user.grade} класс · {user.subscription === "premium" ? "Premium" : "Free"}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={logout} className="text-sm text-gray-400 hover:text-red-500 transition">Выйти</button>
          <Link href="/profile" className="text-sm text-primary font-medium">Профиль</Link>
        </div>
      </header>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="bg-white p-3 rounded-xl border border-orange-100 flex items-center gap-3">
          <span className="text-2xl">🔥</span>
          <div>
            <p className="text-2xl font-bold">{streak}</p>
            <p className="text-xs text-gray-400">{streak === 1 ? "день" : streak < 5 ? "дня" : "дней"} подряд</p>
          </div>
        </div>
        <div className="bg-white p-3 rounded-xl border border-green-100 flex items-center gap-3">
          <span className="text-2xl">🎯</span>
          <div>
            <p className="text-2xl font-bold">{progress?.accuracy ?? 0}%</p>
            <p className="text-xs text-gray-400">точность</p>
          </div>
        </div>
        <div className="bg-white p-3 rounded-xl border border-blue-100 flex items-center gap-3">
          <span className="text-2xl">📊</span>
          <div>
            <p className="text-2xl font-bold">{progress?.total_answers ?? 0}</p>
            <p className="text-xs text-gray-400">решено задач</p>
          </div>
        </div>
        <div className="bg-white p-3 rounded-xl border border-purple-100 flex items-center gap-3">
          <span className="text-2xl">✅</span>
          <div>
            <p className="text-2xl font-bold">{progress?.topics_mastered ?? 0}/{progress?.total_topics ?? 24}</p>
            <p className="text-xs text-gray-400">тем освоено</p>
          </div>
        </div>
      </div>

      <div className="bg-white p-4 rounded-xl border border-gray-100 mb-4">
        <div className="flex justify-between items-center mb-2">
          <h3 className="font-semibold text-sm">Уровень по темам</h3>
          <span className="text-xs text-gray-400">{Math.round((progress?.avg_mastery ?? 0))}% в среднем</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
          <div className="bg-primary h-2 rounded-full transition-all" style={{ width: `${progress?.avg_mastery ?? 0}%` }} />
        </div>
        <div className="space-y-1.5">
          {masteryTop.map(m => (
            <div key={m.topic_code} className="flex items-center gap-2 text-xs">
              <span className="w-32 truncate text-gray-600">{m.topic_name}</span>
              <div className="flex-1 bg-gray-100 rounded-full h-1.5">
                <div className="bg-green-500 h-1.5 rounded-full" style={{ width: `${m.score * 100}%` }} />
              </div>
              <span className="w-8 text-right text-gray-400">{Math.round(m.score * 100)}%</span>
            </div>
          ))}
        </div>
      </div>

      <div className="text-center">
        {limit && !limit.is_premium && limit.remaining <= 0 ? (
          <div className="bg-orange-50 border border-orange-200 rounded-2xl p-6 mb-4">
            <p className="text-lg font-bold text-orange-700 mb-1">Лимит на сегодня исчерпан</p>
            <p className="text-sm text-orange-600 mb-3">Бесплатно: {limit.limit} задач в день</p>
            <p className="text-sm text-gray-500 mb-4">Premium — безлимит, ИИ-разборы, все пробники</p>
            <button onClick={() => router.push("/premium")} className="bg-yellow-500 text-white px-6 py-3 rounded-xl font-bold hover:bg-yellow-600 transition">
              Premium за 990 ₽/мес
            </button>
          </div>
        ) : (
          <>
            <button
              onClick={startSession}
              disabled={isStarting}
              className="bg-primary text-white px-12 py-5 rounded-2xl text-lg font-bold hover:bg-primary-dark transition disabled:opacity-50 shadow-lg shadow-primary/25 w-full"
            >
              {isStarting ? "Готовим задачи..." : "НАЧАТЬ ТРЕНИРОВКУ"}
            </button>
            {limit && !limit.is_premium && (
              <p className="text-xs text-gray-400 mt-2">Осталось задач сегодня: {limit.remaining}</p>
            )}
          </>
        )}
      </div>

      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 py-3 px-6 flex justify-between max-w-lg mx-auto rounded-t-2xl" style={{ paddingBottom: "max(12px, env(safe-area-inset-bottom))" }}>
        <Link href="/dashboard" className="text-primary font-medium text-sm">Главная</Link>
        <Link href="/errors" className="text-gray-400 text-sm">Ошибки</Link>
        <Link href="/exam-sim" className="text-gray-400 text-sm">Пробник</Link>
        <Link href="/profile" className="text-gray-400 text-sm">Прогресс</Link>
      </nav>
    </div>
  )
}
