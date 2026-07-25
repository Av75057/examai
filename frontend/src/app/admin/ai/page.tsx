"use client"

import { useEffect, useState } from "react"
import { adminApi } from "@/lib/admin-auth"

interface ErrorPattern {
  id: number
  topic_id: number
  name: string
  explanation_template: string
  is_active: boolean
  hit_count: number
}

export default function AdminAI() {
  const [patterns, setPatterns] = useState<ErrorPattern[]>([])
  const [queue, setQueue] = useState<any>(null)
  const [tab, setTab] = useState<"patterns" | "moderation" | "prompts">("patterns")
  const [newPattern, setNewPattern] = useState({ topic_id: 1, name: "", explanation_template: "", detection_rule: {} })

  useEffect(() => {
    adminApi.get<{ items: ErrorPattern[] }>("/admin/ai/error-patterns").then(d => setPatterns(d.items))
    adminApi.get("/admin/ai/moderation/queue").then(setQueue)
  }, [])

  const createPattern = async () => {
    try {
      await adminApi.post("/admin/ai/error-patterns", newPattern)
      const data = await adminApi.get<{ items: ErrorPattern[] }>("/admin/ai/error-patterns")
      setPatterns(data.items)
      setNewPattern({ topic_id: 1, name: "", explanation_template: "", detection_rule: {} })
    } catch (e) {
      console.error(e)
    }
  }

  const tabs = [
    { key: "patterns", label: "Паттерны ошибок" },
    { key: "moderation", label: "Модерация" },
    { key: "prompts", label: "LLM-промпты" },
  ]

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">ИИ-модерация</h2>

      <div className="flex gap-2 mb-6">
        {tabs.map(t => (
          <button
            key={t.key}
            onClick={() => setTab(t.key as typeof tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${tab === t.key ? "bg-indigo-600 text-white" : "bg-gray-800 text-gray-400 hover:bg-gray-700"}`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "patterns" && (
        <div>
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-4 mb-6">
            <h3 className="text-lg font-semibold mb-3">Новый паттерн</h3>
            <div className="grid grid-cols-2 gap-3">
              <input
                value={newPattern.name}
                onChange={e => setNewPattern({ ...newPattern, name: e.target.value })}
                placeholder="Название паттерна"
                className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm"
              />
              <input
                type="number"
                value={newPattern.topic_id}
                onChange={e => setNewPattern({ ...newPattern, topic_id: parseInt(e.target.value) })}
                placeholder="ID темы"
                className="bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm"
              />
            </div>
            <textarea
              value={newPattern.explanation_template}
              onChange={e => setNewPattern({ ...newPattern, explanation_template: e.target.value })}
              placeholder="Шаблон объяснения"
              rows={2}
              className="w-full mt-3 bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm"
            />
            <button onClick={createPattern} className="mt-3 bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700">Добавить</button>
          </div>

          <div className="space-y-2">
            {patterns.map(p => (
              <div key={p.id} className="bg-gray-800 rounded-xl border border-gray-700 p-4 flex justify-between items-center">
                <div>
                  <p className="font-medium">{p.name}</p>
                  <p className="text-sm text-gray-400">{p.explanation_template}</p>
                </div>
                <div className="text-right">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${p.is_active ? "bg-green-900 text-green-300" : "bg-gray-700 text-gray-400"}`}>
                    {p.is_active ? "Активен" : "Отключён"}
                  </span>
                  <p className="text-xs text-gray-500 mt-1">Сработал: {p.hit_count} раз</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {tab === "moderation" && (
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6 text-center">
          <p className="text-gray-400 text-lg mb-2">Очередь модерации пуста</p>
          <p className="text-gray-500 text-sm">Нет ответов, требующих проверки</p>
          <div className="grid grid-cols-3 gap-4 mt-6">
            <div className="bg-gray-700 rounded-lg p-4">
              <p className="text-2xl font-bold">0</p>
              <p className="text-xs text-gray-400">Ожидают</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <p className="text-2xl font-bold">0</p>
              <p className="text-xs text-gray-400">Одобрено сегодня</p>
            </div>
            <div className="bg-gray-700 rounded-lg p-4">
              <p className="text-2xl font-bold">0</p>
              <p className="text-xs text-gray-400">Отклонено</p>
            </div>
          </div>
        </div>
      )}

      {tab === "prompts" && (
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <h3 className="text-lg font-semibold mb-4">Системные промпты</h3>
          <div className="bg-gray-700 rounded-lg p-4 mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="font-medium">Разбор ошибки по алгебре</span>
              <span className="text-xs bg-green-900 text-green-300 px-2 py-0.5 rounded">gpt-4o · v1</span>
            </div>
            <p className="text-sm text-gray-400">Temperature: 0.7 · Max tokens: 500</p>
          </div>
          <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700">+ Новый промпт</button>
        </div>
      )}
    </div>
  )
}
