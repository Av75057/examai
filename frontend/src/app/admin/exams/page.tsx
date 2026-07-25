"use client"

import { useEffect, useState } from "react"
import { adminApi } from "@/lib/admin-auth"

export default function AdminExams() {
  const [exams, setExams] = useState<any[]>([])
  const [results, setResults] = useState<any>(null)
  const [newExam, setNewExam] = useState({ title: "", duration_min: 235 })
  const [showForm, setShowForm] = useState(false)

  const load = async () => {
    const data = await adminApi.get<{ items: any[] }>("/admin/exams/")
    setExams(data.items)
  }

  useEffect(() => { load() }, [])

  const createExam = async () => {
    await adminApi.post("/admin/exams/", newExam)
    setShowForm(false)
    setNewExam({ title: "", duration_min: 235 })
    load()
  }

  const publish = async (id: number) => {
    await adminApi.post(`/admin/exams/${id}/publish`)
    load()
  }

  const viewResults = async (id: number) => {
    const data = await adminApi.get(`/admin/exams/${id}/results`)
    setResults(data)
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Пробные экзамены</h2>
        <button onClick={() => setShowForm(!showForm)} className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700">
          + Новый экзамен
        </button>
      </div>

      {showForm && (
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-4 mb-6">
          <h3 className="text-lg font-semibold mb-3">Создать экзамен</h3>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Название</label>
              <input
                value={newExam.title}
                onChange={e => setNewExam({ ...newExam, title: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm"
                placeholder="Пробник №1, 2026"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Длительность (мин)</label>
              <input
                type="number"
                value={newExam.duration_min}
                onChange={e => setNewExam({ ...newExam, duration_min: parseInt(e.target.value) })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm"
              />
            </div>
          </div>
          <div className="flex gap-2 mt-3">
            <button onClick={createExam} className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700">Создать</button>
            <button onClick={() => setShowForm(false)} className="bg-gray-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-gray-700">Отмена</button>
          </div>
        </div>
      )}

      {results ? (
        <div>
          <button onClick={() => setResults(null)} className="text-indigo-400 text-sm mb-4 block">← К списку</button>
          <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
            <h3 className="text-xl font-bold mb-4">Результаты экзамена</h3>
            <p className="text-gray-400 mb-4">Всего попыток: {results.total_attempts}</p>
            <div className="space-y-2">
              {results.items?.slice(0, 20).map((a: any) => (
                <div key={a.id} className="flex justify-between text-sm py-1 border-b border-gray-700/50">
                  <span>User {a.user_id}</span>
                  <span className={a.completed ? "text-green-400" : "text-yellow-400"}>
                    {a.test_score !== null ? `${a.test_score} баллов` : "Не завершён"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {exams.length === 0 && <p className="text-gray-500 text-center py-8">Нет созданных экзаменов</p>}
          {exams.map(exam => (
            <div key={exam.id} className="bg-gray-800 rounded-xl border border-gray-700 p-4 flex justify-between items-center">
              <div>
                <p className="font-medium">{exam.title}</p>
                <p className="text-sm text-gray-400">{exam.duration_min} мин · {exam.structure?.part1 || 12}+{exam.structure?.part2 || 6} заданий</p>
                <span className={`text-xs px-2 py-0.5 rounded-full mt-1 inline-block ${exam.status === "active" ? "bg-green-900 text-green-300" : "bg-gray-700 text-gray-400"}`}>
                  {exam.status}
                </span>
              </div>
              <div className="flex gap-2">
                <button onClick={() => viewResults(exam.id)} className="text-indigo-400 text-sm hover:text-indigo-300">Результаты</button>
                {exam.status !== "active" && (
                  <button onClick={() => publish(exam.id)} className="bg-green-600 text-white px-3 py-1 rounded text-xs hover:bg-green-700">Опубликовать</button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
