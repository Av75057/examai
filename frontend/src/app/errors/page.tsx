"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth"
import { api } from "@/lib/api"
import type { ErrorLog } from "@/types"
import Link from "next/link"

export default function ErrorsPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [errors, setErrors] = useState<ErrorLog[]>([])
  const [filter, setFilter] = useState<"all" | "active" | "mastered">("active")

  useEffect(() => {
    if (!loading && !user) {
      router.push("/")
    }
  }, [user, loading, router])

  useEffect(() => {
    if (!user) return
    api.get<ErrorLog[]>("/errors/")
      .then(setErrors)
      .catch(() => {})
  }, [user])

  const filtered = errors.filter((e) => {
    if (filter === "active") return !e.mastered
    if (filter === "mastered") return e.mastered
    return true
  })

  if (loading || !user) {
    return <div className="flex items-center justify-center min-h-screen">Загрузка...</div>
  }

  return (
    <div className="min-h-screen p-4 max-w-lg mx-auto pb-20">
      <button onClick={() => router.push("/dashboard")} className="text-gray-400 mb-4">
        ← Назад
      </button>

      <h1 className="text-2xl font-bold mb-2">Дневник ошибок</h1>
      <p className="text-gray-500 text-sm mb-4">
        Интервальное повторение: ошибки возвращаются для закрепления
      </p>

      <div className="flex gap-2 mb-4">
        {(["all", "active", "mastered"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium transition ${
              filter === f
                ? "bg-primary text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {f === "all" ? "Все" : f === "active" ? "Активные" : "Освоено"}
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          {filter === "active"
            ? "Нет активных ошибок — отлично!"
            : filter === "mastered"
              ? "Ещё нет освоенных тем"
              : "Список ошибок пуст"}
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((error) => (
            <div
              key={error.id}
              className="bg-white p-4 rounded-xl border border-gray-100 flex items-center justify-between"
            >
              <div>
                <p className="font-medium text-sm">{error.error_type}</p>
                <p className="text-xs text-gray-400">
                  Стадия: {error.review_stage + 1}/5
                  {error.next_review_at &&
                    ` • Повтор: ${new Date(error.next_review_at).toLocaleDateString("ru")}`}
                </p>
              </div>
              <span
                className={`text-xs px-2 py-1 rounded-full ${
                  error.mastered
                    ? "bg-green-100 text-green-700"
                    : "bg-orange-100 text-orange-700"
                }`}
              >
                {error.mastered ? "Освоено" : "В работе"}
              </span>
            </div>
          ))}
        </div>
      )}

      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 py-3 px-6 flex justify-between max-w-lg mx-auto rounded-t-2xl">
        <Link href="/dashboard" className="text-gray-400 text-sm">Главная</Link>
        <Link href="/errors" className="text-primary font-medium text-sm">Ошибки</Link>
        <Link href="/exam" className="text-gray-400 text-sm">Пробник</Link>
        <Link href="/profile" className="text-gray-400 text-sm">Прогресс</Link>
      </nav>
    </div>
  )
}
