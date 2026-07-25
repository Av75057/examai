"use client"

import { useEffect, useState } from "react"
import { adminApi } from "@/lib/admin-auth"

interface Student {
  id: number
  email: string
  name: string
  subscription: string
  created_at: string
}

interface StudentDetail extends Student {
  mastery: { topic_code: string; topic_name: string; score: number }[]
  total_sessions: number
  total_answers: number
  exams: { id: number; test_score: number | null; started_at: string }[]
}

export default function AdminUsers() {
  const [students, setStudents] = useState<Student[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<StudentDetail | null>(null)
  const [search, setSearch] = useState("")

  const loadStudents = async (p: number) => {
    setLoading(true)
    try {
      const data = await adminApi.get<{ items: Student[]; total: number }>(
        `/admin/users/students?page=${p}&per_page=10&search=${search}`
      )
      setStudents(data.items)
      setTotal(data.total)
      setPage(p)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadStudents(1) }, [])

  const viewStudent = async (id: number) => {
    try {
      const data = await adminApi.get<StudentDetail>(`/admin/users/students/${id}`)
      setSelected(data)
    } catch (e) {
      console.error(e)
    }
  }

  const deleteStudent = async (id: number, name: string) => {
    if (!confirm(`Удалить пользователя «${name}»? Все данные будут удалены безвозвратно.`)) return
    try {
      await adminApi.delete(`/admin/users/students/${id}`)
      setSelected(null)
      loadStudents(page)
    } catch (e: any) {
      alert(e.message)
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Пользователи</h2>

      <div className="flex gap-2 mb-4">
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && loadStudents(1)}
          className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-sm text-white w-64"
          placeholder="Поиск по email или имени..."
        />
        <button
          onClick={() => loadStudents(1)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-indigo-700"
        >
          Найти
        </button>
      </div>

      {selected ? (
        <div>
          <button onClick={() => setSelected(null)} className="text-indigo-400 text-sm mb-4 block">← Назад к списку</button>
          <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
            <h3 className="text-xl font-bold mb-2">{selected.name}</h3>
            <p className="text-gray-400 text-sm mb-4">{selected.email} · {selected.subscription} · Зарегистрирован: {new Date(selected.created_at).toLocaleDateString("ru")}</p>

            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-gray-700 rounded-lg p-4">
                <p className="text-gray-400 text-xs">Решено задач</p>
                <p className="text-2xl font-bold">{selected.total_answers}</p>
              </div>
              <div className="bg-gray-700 rounded-lg p-4">
                <p className="text-gray-400 text-xs">Сессий</p>
                <p className="text-2xl font-bold">{selected.total_sessions}</p>
              </div>
              <div className="bg-gray-700 rounded-lg p-4">
                <p className="text-gray-400 text-xs">Пробников</p>
                <p className="text-2xl font-bold">{selected.exams.length}</p>
              </div>
            </div>

            <h4 className="font-semibold mb-2">Прогресс по темам</h4>
            <div className="space-y-2">
              {selected.mastery.slice(0, 10).map((m) => (
                <div key={m.topic_code} className="flex items-center gap-3">
                  <span className="text-sm w-40 truncate text-gray-400">{m.topic_name}</span>
                  <div className="flex-1 bg-gray-700 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full transition-all"
                      style={{ width: `${m.score * 100}%` }}
                    />
                  </div>
                  <span className="text-sm w-12 text-right">{Math.round(m.score * 100)}%</span>
                </div>
              ))}
            </div>
            <button
              onClick={() => deleteStudent(selected.id, selected.name)}
              className="mt-4 bg-red-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-red-700 transition"
            >
              Удалить пользователя
            </button>
          </div>
        </div>
      ) : (
        <>
          <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-700 text-left text-gray-400">
                  <th className="p-3">ID</th>
                  <th className="p-3">Имя</th>
                  <th className="p-3">Email</th>
                  <th className="p-3">Тариф</th>
                  <th className="p-3">Дата регистрации</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s) => (
                  <tr
                    key={s.id}
                    onClick={() => viewStudent(s.id)}
                    className="border-b border-gray-700/50 hover:bg-gray-750 cursor-pointer"
                  >
                    <td className="p-3 text-gray-500">{s.id}</td>
                    <td className="p-3">{s.name}</td>
                    <td className="p-3 text-gray-400">{s.email}</td>
                    <td className="p-3">
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        s.subscription === "premium" ? "bg-yellow-900 text-yellow-300" : "bg-gray-700 text-gray-400"
                      }`}>
                        {s.subscription}
                      </span>
                    </td>
                    <td className="p-3 text-gray-500">{new Date(s.created_at).toLocaleDateString("ru")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex justify-between items-center mt-4 text-sm text-gray-400">
            <span>Всего: {total}</span>
            <div className="flex gap-2">
              <button onClick={() => loadStudents(page - 1)} disabled={page <= 1} className="px-3 py-1 bg-gray-800 rounded disabled:opacity-30">Назад</button>
              <span className="px-3 py-1">Стр. {page}</span>
              <button onClick={() => loadStudents(page + 1)} disabled={page * 10 >= total} className="px-3 py-1 bg-gray-800 rounded disabled:opacity-30">Вперёд</button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
