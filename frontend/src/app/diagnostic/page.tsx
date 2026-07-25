"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import type { Task, AnswerResult } from "@/types"
import { MixedText } from "@/components/Latex"

interface DAnswer {
  answer: string
  is_correct: boolean | null
  result: AnswerResult | null
}

export default function DiagnosticPage() {
  const router = useRouter()
  const [tasks, setTasks] = useState<Task[]>([])
  const [answers, setAnswers] = useState<Record<number, DAnswer>>({})
  const [currentIdx, setCurrentIdx] = useState(0)
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [completed, setCompleted] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    api.get<Task[]>("/diagnostic/start")
      .then(setTasks)
      .catch(e => setError("Ошибка: " + (e.message || "попробуйте позже")))
      .finally(() => setLoading(false))
  }, [])

  const task = tasks[currentIdx]
  const ans = task ? answers[task.id] : null

  const submitAnswer = async () => {
    if (!ans?.answer.trim() || !task) return
    setSubmitting(true)
    try {
      const result = await api.post<AnswerResult>("/diagnostic/submit", {
        task_id: task.id, answer: ans.answer.trim(), time_spent_seconds: 5,
      })
      setAnswers(prev => ({ ...prev, [task.id]: { ...ans, is_correct: result.is_correct, result } }))
    } catch (e: any) {
      setError(e?.message || "Ошибка")
    } finally { setSubmitting(false) }
  }

  const finish = async () => {
    const results = tasks.map(t => ({ task_id: t.id, is_correct: answers[t.id]?.is_correct || false }))
    await api.post("/diagnostic/complete", results)
    setCompleted(true)
  }

  if (loading) return <div className="flex items-center justify-center min-h-screen">
    <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
  </div>
  if (error) return <div className="flex items-center justify-center min-h-screen text-red-500 p-4 text-center">{error}</div>

  if (completed) {
    const correct = Object.values(answers).filter(a => a.is_correct).length
    return (
      <div className="min-h-screen p-4 max-w-lg mx-auto flex flex-col items-center justify-center text-center animate-fade-in">
        <div className="text-6xl mb-4">🎉</div>
        <h1 className="text-2xl font-bold mb-2">Диагностика завершена!</h1>
        <p className="text-slate-500 mb-2">Правильно: {correct} из {tasks.length}</p>
        <p className="text-slate-400 mb-6 text-sm">Ваш уровень определён по {tasks.length} темам</p>
        <button onClick={() => router.push("/dashboard")} className="btn-primary px-10 py-4 text-lg font-bold">
          Начать обучение
        </button>
      </div>
    )
  }

  if (!task) return <div className="flex items-center justify-center min-h-screen text-slate-400">Нет задач</div>

  return (
    <div className="min-h-screen p-4 max-w-lg mx-auto flex flex-col animate-fade-in">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm text-slate-400">Диагностика</span>
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-indigo-500">{currentIdx + 1}/{tasks.length}</span>
          <button onClick={finish} className="text-xs bg-slate-100 text-slate-500 px-3 py-1 rounded-full hover:bg-slate-200">Завершить</button>
        </div>
      </div>

      <div className="w-full bg-slate-200 rounded-full h-1.5 mb-3 overflow-hidden">
        <div className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full transition-all" style={{ width: `${((currentIdx + 1) / tasks.length) * 100}%` }} />
      </div>

      <div className="flex gap-1 mb-4 overflow-x-auto hide-scrollbar py-1">
        {tasks.map((t, i) => (
          <button key={t.id} onClick={() => setCurrentIdx(i)}
            className={`w-7 h-7 rounded-full text-xs font-medium flex-shrink-0 transition ${
              i === currentIdx ? "bg-indigo-500 text-white" :
              answers[t.id]?.is_correct === true ? "bg-emerald-100 text-emerald-700" :
              answers[t.id]?.is_correct === false ? "bg-red-100 text-red-700" :
              "bg-slate-100 text-slate-400"
            }`}>{i + 1}</button>
        ))}
      </div>

      <div className="card p-5 mb-4 flex-1">
        <h2 className="text-lg font-semibold text-slate-800 mb-3"><MixedText text={task.content.text} /></h2>
        {task.content.formula && (
          <div className="bg-slate-50 p-3 rounded-xl text-center border border-slate-100"><MixedText text={`$$${task.content.formula}$$`} /></div>
        )}
      </div>

      {ans?.is_correct !== null ? (
        <div className={`p-3 rounded-xl text-sm mb-3 ${ans.is_correct ? "bg-emerald-50 border border-emerald-200" : "bg-red-50 border border-red-200"}`}>
          <p className="font-medium">{ans.is_correct ? "✅ Правильно" : "❌ Ошибка"}</p>
          {ans.result?.correct_answer && <p className="text-slate-600 mt-1">Ответ: {ans.result.correct_answer}</p>}
          {ans.result?.explanation && <div className="mt-2 text-slate-600"><MixedText text={ans.result.explanation} /></div>}
        </div>
      ) : (
        <div className="mb-3">
          <input type="text" value={ans?.answer || ""}
            onChange={e => setAnswers(prev => ({ ...prev, [task.id]: { answer: e.target.value, is_correct: null, result: null } }))}
            onKeyDown={e => e.key === "Enter" && submitAnswer()}
            className="w-full bg-white border border-slate-200 rounded-2xl px-5 py-4 text-lg focus:outline-none focus:ring-2 focus:ring-indigo-300 transition"
            placeholder="Введите ответ..." autoFocus />
          <button onClick={submitAnswer} disabled={!ans?.answer?.trim() || submitting}
            className="btn-primary w-full py-3.5 text-base font-bold mt-2">
            {submitting ? "Проверяем..." : "Ответить"}
          </button>
        </div>
      )}

      <div className="flex gap-2 mb-4">
        <button onClick={() => setCurrentIdx(i => i - 1)} disabled={currentIdx === 0}
          className="flex-1 bg-white border border-slate-200 py-3 rounded-2xl font-medium text-slate-600 hover:bg-slate-50 transition disabled:opacity-30">← Назад</button>
        {currentIdx < tasks.length - 1 ? (
          <button onClick={() => setCurrentIdx(i => i + 1)} className="btn-primary flex-1 py-3 text-base font-bold">Далее →</button>
        ) : (
          <button onClick={finish} className="flex-1 bg-emerald-500 text-white py-3 rounded-2xl font-bold hover:bg-emerald-600 transition">Завершить</button>
        )}
      </div>
    </div>
  )
}
