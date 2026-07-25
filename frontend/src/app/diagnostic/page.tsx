"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import type { Task, AnswerResult } from "@/types"
import { MixedText } from "@/components/Latex"

const STORAGE_KEY = "diagnostic_state"

interface SavedAnswer {
  task_id: number
  answer: string
  is_correct: boolean | null
  result: AnswerResult | null
}

interface DiagnosticState {
  tasks: Task[]
  answers: SavedAnswer[]
  currentIdx: number
  completed: boolean
}

export default function DiagnosticPage() {
  const router = useRouter()
  const [state, setState] = useState<DiagnosticState>(() => {
    if (typeof window === "undefined") return { tasks: [], answers: [], currentIdx: 0, completed: false }
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      try { return JSON.parse(saved) }
      catch { localStorage.removeItem(STORAGE_KEY) }
    }
    return { tasks: [], answers: [], currentIdx: 0, completed: false }
  })
  const [loading, setLoading] = useState(!state.tasks.length)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState("")

  const persist = (s: DiagnosticState) => {
    setState(s)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(s))
  }

  useEffect(() => {
    if (state.tasks.length > 0) return
    api.get<Task[]>("/diagnostic/start")
      .then(tasks => {
        const answers = tasks.map(t => ({ task_id: t.id, answer: "", is_correct: null, result: null }))
        persist({ tasks, answers, currentIdx: 0, completed: false })
      })
      .catch(e => setError("Ошибка загрузки: " + (e.message || "")))
      .finally(() => setLoading(false))
  }, [])

  const tasks = state.tasks
  const answers = state.answers
  const currentIdx = state.currentIdx
  const task = tasks[currentIdx]
  const currentAnswer = answers[currentIdx]

  const setAnswer = (val: string) => {
    const updated = [...answers]
    updated[currentIdx] = { ...updated[currentIdx], answer: val }
    persist({ ...state, answers: updated })
  }

  const submitAnswer = async () => {
    if (!currentAnswer.answer.trim() || !task) return
    setSubmitting(true)
    try {
      const result = await api.post<AnswerResult>("/diagnostic/submit", {
        task_id: task.id,
        answer: currentAnswer.answer.trim(),
        time_spent_seconds: 5,
      })
      const updated = [...answers]
      updated[currentIdx] = {
        ...updated[currentIdx],
        is_correct: result.is_correct,
        result: result,
      }
      persist({ ...state, answers: updated })
    } catch (err: any) {
      setError(err?.message || "Ошибка отправки")
    } finally {
      setSubmitting(false)
    }
  }

  const goTo = (idx: number) => {
    if (idx >= 0 && idx < tasks.length) {
      persist({ ...state, currentIdx: idx })
    }
  }

  const finish = async () => {
    const unanswered = answers.filter(a => a.is_correct === null).length
    if (unanswered > 0) {
      if (!confirm(`Осталось ${unanswered} неотвеченных вопросов. Завершить?`)) return
    }
    const results = answers.map(a => ({ task_id: a.task_id, is_correct: a.is_correct || false }))
    await api.post("/diagnostic/complete", results)
    persist({ ...state, completed: true })
    localStorage.removeItem(STORAGE_KEY)
  }

  if (loading) return <div className="flex items-center justify-center min-h-screen">Загрузка...</div>
  if (error) return <div className="flex items-center justify-center min-h-screen text-red-500">{error}</div>

  if (state.completed) {
    const correct = answers.filter(a => a.is_correct).length
    return (
      <div className="min-h-screen p-4 max-w-lg mx-auto flex flex-col items-center justify-center text-center">
        <div className="text-6xl mb-4">🎉</div>
        <h1 className="text-2xl font-bold mb-2">Диагностика завершена!</h1>
        <p className="text-gray-500 mb-2">Правильно: {correct} из {answers.length}</p>
        <p className="text-gray-500 mb-6">Ваш уровень определён по всем темам ЕГЭ</p>
        <button onClick={() => router.push("/dashboard")} className="bg-primary text-white px-8 py-4 rounded-2xl text-lg font-bold hover:bg-primary-dark transition shadow-lg shadow-primary/25">
          Начать обучение
        </button>
      </div>
    )
  }

  if (!task) return <div className="flex items-center justify-center min-h-screen">Нет задач</div>

  return (
    <div className="min-h-screen p-4 max-w-lg mx-auto flex flex-col">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm text-gray-400">Диагностика</span>
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-primary">{currentIdx + 1} из {tasks.length}</span>
          <button
            onClick={finish}
            className="text-xs bg-gray-200 text-gray-600 px-3 py-1 rounded-full hover:bg-gray-300 transition"
          >
            Завершить
          </button>
        </div>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-1.5 mb-2">
        <div className="bg-primary h-1.5 rounded-full transition-all" style={{ width: `${((currentIdx + 1) / tasks.length) * 100}%` }} />
      </div>

      {/* Question dots */}
      <div className="flex gap-1 mb-4 overflow-x-auto hide-scrollbar py-1">
        {tasks.map((t, i) => (
          <button
            key={t.id}
            onClick={() => goTo(i)}
            className={`w-7 h-7 rounded-full text-xs font-medium flex-shrink-0 transition ${
              i === currentIdx
                ? "bg-primary text-white"
                : answers[i]?.is_correct === true
                  ? "bg-green-100 text-green-700"
                  : answers[i]?.is_correct === false
                    ? "bg-red-100 text-red-700"
                    : "bg-gray-100 text-gray-400"
            }`}
          >
            {i + 1}
          </button>
        ))}
      </div>

      <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 mb-4 flex-1">
        <h2 className="text-lg font-semibold mb-3"><MixedText text={task.content.text} /></h2>
        {task.content.formula && (
          <div className="bg-gray-50 p-3 rounded-lg text-center mb-3">
            <MixedText text={`$$${task.content.formula}$$`} />
          </div>
        )}
      </div>

      {currentAnswer.is_correct !== null ? (
        <div className="mb-3">
          <div className={`p-3 rounded-xl text-sm ${currentAnswer.is_correct ? "bg-green-50 border border-green-200" : "bg-red-50 border border-red-200"}`}>
            <p className="font-medium">{currentAnswer.is_correct ? "✅ Правильно" : "❌ Ошибка"}</p>
            {currentAnswer.result?.correct_answer && (
              <p className="text-gray-600 mt-1">Ответ: {currentAnswer.result.correct_answer}</p>
            )}
            {currentAnswer.result?.explanation && (
              <div className="mt-2 text-gray-600"><MixedText text={currentAnswer.result.explanation} /></div>
            )}
          </div>
        </div>
      ) : (
        <div className="mb-3">
          <input
            type="text"
            value={currentAnswer.answer}
            onChange={(e) => setAnswer(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && submitAnswer()}
            className="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Введите ответ..."
            autoFocus
          />
          <button
            onClick={submitAnswer}
            disabled={!currentAnswer.answer.trim() || submitting}
            className="w-full bg-primary text-white py-3 rounded-xl font-semibold mt-2 hover:bg-primary-dark transition disabled:opacity-50"
          >
            {submitting ? "Проверяем..." : "Ответить"}
          </button>
        </div>
      )}

      <div className="flex gap-2 mb-4">
        <button
          onClick={() => goTo(currentIdx - 1)}
          disabled={currentIdx === 0}
          className="flex-1 border border-gray-300 py-3 rounded-xl font-medium hover:bg-gray-50 transition disabled:opacity-30"
        >
          ← Назад
        </button>
        {currentIdx < tasks.length - 1 ? (
          <button
            onClick={() => goTo(currentIdx + 1)}
            className="flex-1 bg-primary text-white py-3 rounded-xl font-medium hover:bg-primary-dark transition"
          >
            Далее →
          </button>
        ) : (
          <button
            onClick={finish}
            className="flex-1 bg-green-600 text-white py-3 rounded-xl font-bold hover:bg-green-700 transition"
          >
            Завершить диагностику
          </button>
        )}
      </div>
    </div>
  )
}
