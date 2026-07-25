"use client"

import { useEffect, useState } from "react"
import { adminApi } from "@/lib/admin-auth"

interface DashboardData {
  total_users: number
  total_tasks: number
  total_topics: number
  dau: number
  mrr: number
  moderation_queue: number
}

export default function AdminDashboard() {
  const [data, setData] = useState<DashboardData | null>(null)

  useEffect(() => {
    adminApi.get<DashboardData>("/admin/dashboard").then(setData).catch(console.error)
  }, [])

  const cards = [
    { label: "Пользователей", value: data?.total_users ?? "-", color: "bg-blue-500" },
    { label: "Задач в банке", value: data?.total_tasks ?? "-", color: "bg-green-500" },
    { label: "Тем", value: data?.total_topics ?? "-", color: "bg-purple-500" },
    { label: "DAU", value: data?.dau ?? "-", color: "bg-orange-500" },
    { label: "MRR (₽)", value: data?.mrr ?? "-", color: "bg-pink-500" },
    { label: "Очередь модерации", value: data?.moderation_queue ?? "-", color: "bg-red-500" },
  ]

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Дашборд</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {cards.map((card) => (
          <div key={card.label} className="bg-gray-800 rounded-xl p-5 border border-gray-700">
            <p className="text-gray-400 text-sm mb-1">{card.label}</p>
            <p className={`text-3xl font-bold text-white`}>{card.value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
