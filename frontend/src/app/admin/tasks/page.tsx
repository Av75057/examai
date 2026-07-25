"use client"

import { useEffect, useState } from "react"
import { adminApi } from "@/lib/admin-auth"

interface Template {
  id: number
  topic_id: number
  topic_name: string
  content_template: { text: string }
  solution_template: { steps: string[] }
  difficulty_base: number
  task_count: number
}

export default function AdminTasks() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState<number | null>(null)

  const load = async (p: number) => {
    setLoading(true)
    try {
      const data = await adminApi.get<{ items: Template[]; total: number }>(`/admin/tasks/templates?page=${p}&per_page=10`)
      setTemplates(data.items)
      setTotal(data.total)
      setPage(p)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load(1) }, [])

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Шаблоны задач</h2>
        <span className="text-gray-400 text-sm">Всего: {total}</span>
      </div>

      {loading ? (
        <p className="text-gray-400">Загрузка...</p>
      ) : (
        <div className="space-y-3">
          {templates.map((tmpl) => (
            <div key={tmpl.id} className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
              <div
                className="p-4 flex justify-between items-center cursor-pointer hover:bg-gray-750"
                onClick={() => setExpanded(expanded === tmpl.id ? null : tmpl.id)}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <span className="text-xs bg-indigo-900 text-indigo-300 px-2 py-0.5 rounded">{tmpl.topic_name}</span>
                    <span className="text-sm text-gray-400">ID: {tmpl.id}</span>
                    <span className="text-xs text-gray-500">{tmpl.task_count} задач</span>
                  </div>
                  <p className="text-sm mt-1 line-clamp-1">{tmpl.content_template?.text || "Нет текста"}</p>
                </div>
                <span className="text-xs text-gray-500 ml-4">Сложность: {tmpl.difficulty_base.toFixed(2)}</span>
              </div>
              {expanded === tmpl.id && (
                <div className="border-t border-gray-700 p-4 bg-gray-850">
                  <h4 className="text-sm font-semibold text-gray-300 mb-2">Шаги решения:</h4>
                  <ol className="list-decimal list-inside text-sm text-gray-400 space-y-1">
                    {(tmpl.solution_template?.steps || []).map((step: string, i: number) => (
                      <li key={i}>{step}</li>
                    ))}
                  </ol>
                  <div className="flex gap-2 mt-3">
                    <button className="bg-indigo-600 text-white px-3 py-1 rounded text-xs hover:bg-indigo-700">Сгенерировать вариации</button>
                    <button className="bg-gray-700 text-gray-300 px-3 py-1 rounded text-xs hover:bg-gray-600">Редактировать</button>
                  </div>
                </div>
              )}
            </div>
          ))}

          <div className="flex justify-between items-center mt-4 text-sm text-gray-400">
            <button onClick={() => load(page - 1)} disabled={page <= 1} className="px-3 py-1 bg-gray-800 rounded disabled:opacity-30">Назад</button>
            <span>Стр. {page}</span>
            <button onClick={() => load(page + 1)} disabled={page * 10 >= total} className="px-3 py-1 bg-gray-800 rounded disabled:opacity-30">Вперёд</button>
          </div>
        </div>
      )}
    </div>
  )
}
