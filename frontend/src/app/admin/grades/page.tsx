"use client"

import { useEffect, useState } from "react"
import { adminApi } from "@/lib/admin-auth"

interface TopicGrade {
  id: number
  code: string
  name: string
  grades: number[]
}

const ALL_GRADES = [5, 6, 7, 8, 9, 10, 11]
const GRADE_LABELS: Record<number, string> = {
  5: "5 кл", 6: "6 кл", 7: "7 кл", 8: "8 кл", 9: "9 🔥 ОГЭ", 10: "10 кл", 11: "11 🔥 ЕГЭ"
}

export default function AdminGrades() {
  const [topics, setTopics] = useState<TopicGrade[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState<number | null>(null)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editGrades, setEditGrades] = useState<number[]>([])

  const load = async () => {
    try {
      const data = await adminApi.get<{ items: TopicGrade[]; available_grades: number[] }>("/admin/grades/topics")
      setTopics(data.items)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const startEdit = (topic: TopicGrade) => {
    setEditingId(topic.id)
    setEditGrades([...topic.grades])
  }

  const toggleGrade = (g: number) => {
    setEditGrades(prev => prev.includes(g) ? prev.filter(x => x !== g) : [...prev, g].sort())
  }

  const save = async (topicId: number) => {
    setSaving(topicId)
    try {
      await adminApi.put(`/admin/grades/topics/${topicId}/grades`, { grades: editGrades })
      setTopics(prev => prev.map(t => t.id === topicId ? { ...t, grades: [...editGrades] } : t))
      setEditingId(null)
    } catch (e) {
      console.error(e)
    } finally {
      setSaving(null)
    }
  }

  const stats = ALL_GRADES.map(g => ({
    grade: g,
    total: topics.filter(t => t.grades.includes(g)).length,
  }))

  if (loading) return <div className="text-gray-400">Загрузка...</div>

  return (
    <div>
      <h2 className="text-2xl font-bold mb-2">Классы и программы</h2>
      <p className="text-gray-400 text-sm mb-6">Привязка тем к классам обучения</p>

      <div className="grid grid-cols-7 gap-3 mb-8">
        {stats.map(s => (
          <div key={s.grade} className="bg-gray-800 rounded-xl p-4 text-center border border-gray-700">
            <p className="text-xs text-gray-400">{GRADE_LABELS[s.grade]}</p>
            <p className="text-2xl font-bold mt-1">{s.total}</p>
            <p className="text-xs text-gray-500">тем</p>
          </div>
        ))}
      </div>

      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-700 text-left text-gray-400">
              <th className="p-3 w-16">ID</th>
              <th className="p-3">Тема</th>
              <th className="p-3">Код</th>
              <th className="p-3">Классы</th>
              <th className="p-3 w-20"></th>
            </tr>
          </thead>
          <tbody>
            {topics.map(t => (
              <tr key={t.id} className="border-b border-gray-700/50 hover:bg-gray-750">
                <td className="p-3 text-gray-500">{t.id}</td>
                <td className="p-3">{t.name}</td>
                <td className="p-3 font-mono text-xs text-gray-400">{t.code}</td>
                <td className="p-3">
                  {editingId === t.id ? (
                    <div className="flex gap-1">
                      {ALL_GRADES.map(g => (
                        <button
                          key={g}
                          onClick={() => toggleGrade(g)}
                          className={`w-8 h-8 rounded text-xs font-bold transition ${
                            editGrades.includes(g)
                              ? "bg-indigo-600 text-white"
                              : "bg-gray-700 text-gray-500 hover:bg-gray-600"
                          }`}
                        >
                          {g}
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="flex gap-1">
                      {ALL_GRADES.map(g => (
                        <span
                          key={g}
                          className={`w-7 h-7 rounded text-xs flex items-center justify-center font-medium ${
                            t.grades.includes(g)
                              ? "bg-indigo-900 text-indigo-300"
                              : "bg-gray-700/30 text-gray-600"
                          }`}
                        >
                          {g}
                        </span>
                      ))}
                    </div>
                  )}
                </td>
                <td className="p-3">
                  {editingId === t.id ? (
                    <div className="flex gap-1">
                      <button
                        onClick={() => save(t.id)}
                        disabled={saving === t.id}
                        className="bg-green-600 text-white px-2 py-1 rounded text-xs hover:bg-green-700"
                      >
                        ✓
                      </button>
                      <button
                        onClick={() => setEditingId(null)}
                        className="bg-gray-600 text-white px-2 py-1 rounded text-xs hover:bg-gray-700"
                      >
                        ✕
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => startEdit(t)}
                      className="text-indigo-400 hover:text-indigo-300 text-xs"
                    >
                      Изменить
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
