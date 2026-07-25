"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth"
import { api } from "@/lib/api"

export default function PremiumPage() {
  const { user } = useAuth()
  const router = useRouter()
  const [activating, setActivating] = useState(false)
  const [message, setMessage] = useState("")

  const activate = async () => {
    setActivating(true)
    try {
      const result = await api.post<{ status: string }>("/auth/activate-premium")
      setMessage(result.status === "already_premium" ? "У вас уже Premium!" : "Premium активирован!")
    } catch (e: any) {
      setMessage(e.message || "Ошибка")
    } finally {
      setActivating(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 max-w-lg mx-auto pb-20">
      <button onClick={() => router.push("/dashboard")} className="text-gray-400 mb-4">← Назад</button>

      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">ExamAI Premium</h1>
        <p className="text-gray-500">Серьёзная подготовка к ЕГЭ</p>
      </div>

      <div className="bg-white rounded-2xl p-6 shadow-sm border border-indigo-100 mb-4">
        <div className="text-center mb-4">
          <span className="text-4xl font-bold text-indigo-600">990 ₽</span>
          <span className="text-gray-400">/мес</span>
        </div>

        <ul className="space-y-3 mb-6">
          {[
            "Безлимит задач каждый день",
            "ИИ-разборы ошибок (DeepSeek)",
            "Все пробные экзамены",
            "Полная аналитика прогресса",
            "Интервальное повторение",
          ].map((f, i) => (
            <li key={i} className="flex items-center gap-2 text-sm">
              <span className="text-green-500">✓</span> {f}
            </li>
          ))}
        </ul>

        <button
          onClick={activate}
          disabled={activating}
          className="w-full bg-indigo-600 text-white py-4 rounded-xl font-bold text-lg hover:bg-indigo-700 transition disabled:opacity-50"
        >
          {activating ? "Активируем..." : "Активировать Premium"}
        </button>

        {message && (
          <p className={`text-center mt-3 text-sm ${message.includes("уже") ? "text-green-600" : "text-red-500"}`}>
            {message}
          </p>
        )}
      </div>

      <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h3 className="font-semibold mb-2">Оплата через Telegram</h3>
        <p className="text-sm text-gray-500 mb-3">
          Для оплаты напишите нашему боту <strong>@examai_pay_bot</strong> и следуйте инструкциям.
        </p>
        <a
          href="https://t.me/examai_pay_bot"
          target="_blank"
          className="block w-full bg-blue-500 text-white py-3 rounded-xl font-semibold text-center hover:bg-blue-600 transition"
        >
          Открыть бот в Telegram
        </a>
      </div>
    </div>
  )
}
