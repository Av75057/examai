"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import type { Task, AnswerResult } from "@/types"
import { MixedText } from "@/components/Latex"

export default function DiagnosticPage() {
  const router = useRouter()
  const [tasks, setTasks] = useState<Task[]>([])
  const [currentIdx, setCurrentIdx] = useState(0)
  const [answer, setAnswer] = useState("")
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [results, setResults] = useState<{ task_id: number; is_correct: boolean }[]>([])
  const [showResult, setShowResult] = useState<AnswerResult | null>(null)
  const [completed, setCompleted] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    api.get<Task[]>("/diagnostic/start")
      .then(t => { setTasks(t); console.log("loaded", t.length, "tasks") })
      .catch(e => { console.error(e); setError("Ошибка загрузки: " + (e.message || "")) })
      .finally(() => setLoading(false))
  }, [])

  const task = tasks[currentIdx]

  const submitAnswer = async () => {
    if (!answer.trim() || !task) return
    setSubmitting(true)
    try {
      const result = await api.post<AnswerResult>("/diagnostic/submit", {
        task_id: task.id,
        answer: answer.trim(),
        time_spent_seconds: 5,
      })
      setShowResult(result)
      setResults(prev => [...prev, { task_id: task.id, is_correct: result.is_correct }])
    } catch (err: any) {
      console.error(err)
      setError(err?.message || "Ошибка отправки")
    } finally {
      setSubmitting(false)
    }
  }

  const nextQuestion = async () => {
    const nextIdx = currentIdx + 1
    if (nextIdx >= tasks.length) {
      await api.post("/diagnostic/complete", results)
      setCompleted(true)
    } else {
      setCurrentIdx(nextIdx)
      setAnswer("")
      setShowResult(null)
    }
  }

  if (loading) return <div className="flex items-center justify-center min-h-screen">Загрузка...</div>
  if (error) return <div className="flex items-center justify-center min-h-screen text-red-500">{error}</div>

  if (completed) {
    return (
      <div className="min-h-screen p-4 max-w-lg mx-auto flex flex-col items-center justify-center text-center">
        <div className="text-6xl mb-4">🎉</div>
        <h1 className="text-2xl font-bold mb-2">Диагностика завершена!</h1>
        <p className="text-gray-500 mb-2">
          Правильно: {results.filter(r => r.is_correct).length} из {results.length}
        </p>
        <p className="text-gray-500 mb-6">Ваш уровень определён по всем темам ЕГЭ</p>
        <button
          onClick={() => router.push("/dashboard")}
          className="bg-primary text-white px-8 py-4 rounded-2xl text-lg font-bold hover:bg-primary-dark transition shadow-lg shadow-primary/25"
        >
          Начать обучение
        </button>
      </div>
    )
  }

  if (!task) return <div className="flex items-center justify-center min-h-screen">Нет задач</div>

  return (
    <div className="min-h-screen p-4 max-w-lg mx-auto flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <span className="text-sm text-gray-400">Диагностика</span>
        <span className="text-sm font-medium text-primary">{currentIdx + 1} из {tasks.length}</span>
      </div>

      <div className="w-full bg-gray-200 rounded-full h-1.5 mb-6">
        <div className="bg-primary h-1.5 rounded-full transition-all" style={{ width: `${((currentIdx + 1) / tasks.length) * 100}%` }} />
      </div>

      {showResult ? (
        <div className="flex-1">
          <div className="text-center py-4">
            <div className="text-4xl mb-2">{showResult.is_correct ? "✅" : "❌"}</div>
            <p className="text-gray-600 text-sm">
              Правильный ответ: <span className="font-medium">{showResult.correct_answer}</span>
            </p>
          </div>
          {showResult.explanation && (
            <div className="bg-white p-4 rounded-xl border border-gray-100 mb-3">
              <MixedText text={showResult.explanation} />
            </div>
          )}
          {showResult.ai_explanation && (
            <div className="bg-indigo-50 p-4 rounded-xl border border-indigo-100 mb-4">
              <MixedText text={showResult.ai_explanation} className="text-sm" />
            </div>
          )}
          <button
            onClick={nextQuestion}
            className="w-full bg-primary text-white py-4 rounded-2xl text-lg font-semibold hover:bg-primary-dark transition"
          >
            {currentIdx + 1 >= tasks.length ? "Завершить диагностику" : "Следующий вопрос"}
          </button>
        </div>
      ) : (
        <>
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mb-6 flex-1">
            <h2 className="text-lg font-semibold mb-4"><MixedText text={task.content.text} /></h2>
            {task.content.formula && (
              <div className="bg-gray-50 p-3 rounded-lg text-center mb-4">
                <MixedText text={`$$${task.content.formula}$$`} />
              </div>
            )}
          </div>

          <div>
            <input
              type="text"
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && submitAnswer()}
              className="w-full border border-gray-300 rounded-xl px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Введите ответ..."
              autoFocus
            />
          </div>

          <button
            onClick={submitAnswer}
            disabled={!answer.trim() || submitting}
            className="w-full bg-primary text-white py-4 rounded-2xl text-lg font-semibold mt-4 hover:bg-primary-dark transition disabled:opacity-50"
          >
            {submitting ? "Проверяем..." : "Ответить"}
          </button>
        </>
      )}
    </div>
  )
}
