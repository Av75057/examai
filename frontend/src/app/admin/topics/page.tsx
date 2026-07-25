"use client"

import { useEffect, useState } from "react"
import { adminApi } from "@/lib/admin-auth"

interface Topic {
  id: number
  code: string
  name: string
  ege_weight: number
}

export default function AdminTopics() {
  const [topics, setTopics] = useState<Topic[]>([])
  const [loading, setLoading] = useState(true)
  const [newTopic, setNewTopic] = useState({ code: "", name: "", ege_weight: 1.0 })
  const [showForm, setShowForm] = useState(false)
  const [error, setError] = useState("")

  const loadTopics = async () => {
    try {
      const data = await adminApi.get<Topic[]>("/admin/topics/")
      setTopics(data)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadTopics() }, [])

  const createTopic = async () => {
    if (!newTopic.code || !newTopic.name) return
    setError("")
    try {
      await adminApi.post("/admin/topics/", newTopic)
      setShowForm(false)
      setNewTopic({ code: "", name: "", ege_weight: 1.0 })
      loadTopics()
    } catch (e: any) {
      setError(e.message)
    }
  }

  const deleteTopic = async (id: number) => {
    try {
      await adminApi.delete(`/admin/topics/${id}`)
      loadTopics()
    } catch (e: any) {
      alert(e.message)
    }
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Темы ЕГЭ</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition"
        >
          + Новая тема
        </button>
      </div>

      {showForm && (
        <div className="bg-gray-800 rounded-xl p-5 border border-gray-700 mb-6">
          <h3 className="text-lg font-semibold mb-4">Создать тему</h3>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Код</label>
              <input
                value={newTopic.code}
                onChange={(e) => setNewTopic({ ...newTopic, code: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm"
                placeholder="linear_equations"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Название</label>
              <input
                value={newTopic.name}
                onChange={(e) => setNewTopic({ ...newTopic, name: e.target.value })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm"
                placeholder="Линейные уравнения"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Вес в ЕГЭ</label>
              <input
                type="number"
                step="0.1"
                value={newTopic.ege_weight}
                onChange={(e) => setNewTopic({ ...newTopic, ege_weight: parseFloat(e.target.value) })}
                className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm"
              />
            </div>
          </div>
          {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
          <div className="flex gap-2 mt-4">
            <button onClick={createTopic} className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700">Сохранить</button>
            <button onClick={() => setShowForm(false)} className="bg-gray-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-gray-700">Отмена</button>
          </div>
        </div>
      )}

      {loading ? (
        <p className="text-gray-400">Загрузка...</p>
      ) : (
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700 text-left text-gray-400">
                <th className="p-3">ID</th>
                <th className="p-3">Код</th>
                <th className="p-3">Название</th>
                <th className="p-3">Вес</th>
                <th className="p-3"></th>
              </tr>
            </thead>
            <tbody>
              {topics.map((t) => (
                <tr key={t.id} className="border-b border-gray-700/50 hover:bg-gray-750">
                  <td className="p-3 text-gray-500">{t.id}</td>
                  <td className="p-3 font-mono text-xs text-gray-300">{t.code}</td>
                  <td className="p-3">{t.name}</td>
                  <td className="p-3">{t.ege_weight}</td>
                  <td className="p-3">
                    <button onClick={() => deleteTopic(t.id)} className="text-red-400 hover:text-red-300 text-xs">Удалить</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
