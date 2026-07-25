"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import Link from "next/link"

export default function ExamPage() {
  const router = useRouter()
  const [starting, setStarting] = useState(false)

  const startExam = async () => {
    setStarting(true)
    try {
      const data = await api.post<{ attempt_id: number }>("/exams/start")
      router.push(`/exam/${data.attempt_id}`)
    } catch (err) {
      console.error(err)
    } finally {
      setStarting(false)
    }
  }

  return (
    <div className="min-h-screen p-4 max-w-lg mx-auto pb-20">
      <div className="text-center py-12">
        <div className="text-5xl mb-4">🎓</div>
        <h1 className="text-2xl font-bold mb-2">Пробный экзамен</h1>
        <p className="text-gray-500 mb-2">
          Полная структура ФИПИ: 18 заданий
        </p>
        <p className="text-sm text-gray-400 mb-6">
          12 кратких + 6 развёрнутых &bull; 3 часа 55 минут
        </p>

        <div className="bg-white p-6 rounded-2xl border border-gray-100 mb-6 text-left space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Формат</span>
            <span>ФИПИ 2025</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Время</span>
            <span>235 минут</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Блокировка</span>
            <span>Имитация реального ЕГЭ</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">Бесплатно</span>
            <span>1 пробник в месяц</span>
          </div>
        </div>

        <button
          onClick={startExam}
          disabled={starting}
          className="bg-primary text-white px-8 py-4 rounded-2xl text-lg font-bold hover:bg-primary-dark transition disabled:opacity-50 shadow-lg shadow-primary/25"
        >
          {starting ? "Подготовка..." : "НАЧАТЬ ПРОБНИК"}
        </button>
      </div>

      <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 py-3 px-6 flex justify-between max-w-lg mx-auto rounded-t-2xl">
        <Link href="/dashboard" className="text-gray-400 text-sm">Главная</Link>
        <Link href="/errors" className="text-gray-400 text-sm">Ошибки</Link>
        <Link href="/exam" className="text-primary font-medium text-sm">Пробник</Link>
        <Link href="/profile" className="text-gray-400 text-sm">Прогресс</Link>
      </nav>
    </div>
  )
}
