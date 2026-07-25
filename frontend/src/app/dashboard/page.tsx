"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth"
import { api } from "@/lib/api"
import type { Task, Mastery } from "@/types"
import Link from "next/link"
import { MixedText } from "@/components/Latex"

interface ProgressData {
  total_answers: number; accuracy: number; total_sessions: number
  avg_mastery: number; topics_mastered: number; total_topics: number
}

export default function DashboardPage() {
  const { user, loading, logout } = useAuth()
  const router = useRouter()
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
    api.get<{ streak: number }>("/progress/streak").then(d => setStreak(d.streak)).catch(() => {})
    api.get<ProgressData>("/progress/overview").then(setProgress).catch(() => {})
    api.get<{ remaining: number; limit: number; is_premium: boolean }>("/tasks/limits").then(setLimit).catch(() => {})
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
      router.push(`/solve/${data[0].id}?session=${data.map(t => t.id).join(",")}&idx=0`)
    } catch { } finally { setIsStarting(false) }
  }

  if (loading || !user) {
    return <div className="flex items-center justify-center min-h-screen">
      <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
    </div>
  }

  const masteryTop = [...mastery].sort((a, b) => b.score - a.score).slice(0, 6)

  return (
    <div className="min-h-screen pb-24 animate-fade-in">
      <div className="max-w-lg mx-auto px-4 pt-4">
        <div className="glass rounded-2xl p-4 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-lg">
                {user.name[0]}
              </div>
              <div>
                <h1 className="font-bold text-slate-800">{user.name}</h1>
                <p className="text-xs text-slate-500">{user.grade} класс · {user.subscription === "premium" ? "Premium" : "Free"}</p>
              </div>
            </div>
            <div className="flex gap-2">
              <button onClick={logout} className="text-xs text-slate-400 hover:text-red-500 transition px-2">Выйти</button>
              <Link href="/profile" className="text-xs text-indigo-500 font-medium px-2">Профиль</Link>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="card p-3 flex items-center gap-3">
            <span className="text-2xl">🔥</span>
            <div><p className="text-xl font-bold text-slate-800">{streak}</p><p className="text-xs text-slate-400">дней подряд</p></div>
          </div>
          <div className="card p-3 flex items-center gap-3">
            <span className="text-2xl">🎯</span>
            <div><p className="text-xl font-bold text-slate-800">{progress?.accuracy ?? 0}%</p><p className="text-xs text-slate-400">точность</p></div>
          </div>
          <div className="card p-3 flex items-center gap-3">
            <span className="text-2xl">📊</span>
            <div><p className="text-xl font-bold text-slate-800">{progress?.total_answers ?? 0}</p><p className="text-xs text-slate-400">задач решено</p></div>
          </div>
          <div className="card p-3 flex items-center gap-3">
            <span className="text-2xl">✅</span>
            <div><p className="text-xl font-bold text-slate-800">{progress?.topics_mastered ?? 0}/{progress?.total_topics ?? 24}</p><p className="text-xs text-slate-400">тем освоено</p></div>
          </div>
        </div>

        {progress && (
          <div className="card p-4 mb-4">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-sm font-semibold text-slate-700">Прогресс по темам</h3>
              <span className="text-xs text-slate-400">{Math.round(progress.avg_mastery)}%</span>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2 mb-3 overflow-hidden">
              <div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-700" style={{ width: `${progress.avg_mastery}%` }} />
            </div>
            <div className="space-y-2">
              {masteryTop.map(m => (
                <div key={m.topic_code} className="flex items-center gap-2 text-xs">
                  <span className="w-28 truncate text-slate-600">{m.topic_name}</span>
                  <div className="flex-1 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                    <div className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-emerald-500 transition-all duration-500" style={{ width: `${m.score * 100}%` }} />
                  </div>
                  <span className="w-8 text-right text-slate-400 font-medium">{Math.round(m.score * 100)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {limit && !limit.is_premium && limit.remaining <= 0 ? (
          <div className="card p-6 text-center border-2 border-amber-200 bg-amber-50/50 mb-4">
            <p className="text-lg font-bold text-amber-700 mb-1">Лимит на сегодня исчерпан</p>
            <p className="text-sm text-amber-600 mb-3">Бесплатно: {limit.limit} задач в день</p>
            <button onClick={() => router.push("/premium")} className="btn-primary px-8 py-3 text-sm w-full">
              Premium за 990 ₽/мес
            </button>
          </div>
        ) : (
          <button
            onClick={startSession}
            disabled={isStarting}
            className="btn-primary w-full py-5 text-lg font-bold relative overflow-hidden"
          >
            <span className="relative z-10">
              {isStarting ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Готовим задачи...
                </span>
              ) : "НАЧАТЬ ТРЕНИРОВКУ"}
            </span>
          </button>
        )}

        {limit && !limit.is_premium && limit.remaining > 0 && (
          <p className="text-center text-xs text-slate-400 mt-2">Осталось задач сегодня: {limit.remaining}</p>
        )}
      </div>

      <nav className="fixed bottom-0 left-0 right-0 glass rounded-t-3xl py-3 px-6 flex justify-between max-w-lg mx-auto" style={{ paddingBottom: "max(12px, env(safe-area-inset-bottom))" }}>
        <Link href="/dashboard" className="text-indigo-600 font-medium text-sm">Главная</Link>
        <Link href="/errors" className="text-slate-400 text-sm hover:text-slate-600 transition">Ошибки</Link>
        <Link href="/exam-sim" className="text-slate-400 text-sm hover:text-slate-600 transition">Пробник</Link>
        <Link href="/profile" className="text-slate-400 text-sm hover:text-slate-600 transition">Прогресс</Link>
      </nav>
    </div>
  )
}
