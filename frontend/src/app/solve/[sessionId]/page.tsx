"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter, useSearchParams } from "next/navigation"
import { api } from "@/lib/api"
import type { Task, AnswerResult } from "@/types"
import { MixedText } from "@/components/Latex"

export default function SolvePage() {
  const params = useParams()
  const router = useRouter()
  const searchParams = useSearchParams()
  const taskId = params.sessionId as string
  const sessionIds = (searchParams.get("session") || "").split(",").filter(Boolean)
  const currentIdx = parseInt(searchParams.get("idx") || "0")

  const [task, setTask] = useState<Task | null>(null)
  const [answer, setAnswer] = useState("")
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [startTime] = useState(Date.now())

  useEffect(() => {
    api.get<Task>(`/tasks/${taskId}`)
      .then(setTask)
      .catch(() => router.push("/dashboard"))
      .finally(() => setLoading(false))
  }, [taskId, router])

  const submitAnswer = async () => {
    if (!answer.trim()) return
    setSubmitting(true)
    const timeSpent = (Date.now() - startTime) / 1000
    try {
      const result = await api.post<AnswerResult>("/tasks/submit", {
        task_id: Number(taskId), answer: answer.trim(), time_spent_seconds: timeSpent,
      })
      const sp = new URLSearchParams({
        correct: String(result.is_correct), answer: result.correct_answer || "",
        student: answer.trim(), explanation: result.explanation || "",
        ai: result.ai_explanation || "", error: result.error_type || "",
        micro: result.micro_task || "", session: sessionIds.join(","), idx: String(currentIdx),
      })
      router.push(`/result/${taskId}?${sp.toString()}`)
    } catch { setSubmitting(false) }
  }

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="w-8 h-8 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
    </div>
  )

  if (!task) return <div className="flex items-center justify-center min-h-screen text-slate-400">Задача не найдена</div>

  return (
    <div className="min-h-screen flex flex-col animate-fade-in">
      <div className="glass sticky top-0 z-10 px-4 py-3 flex justify-between items-center border-b border-white/20">
        <button onClick={() => router.push("/dashboard")} className="text-slate-500 text-sm">← Выйти</button>
        <div className="flex items-center gap-2">
          <div className="h-1.5 w-32 bg-slate-200 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all" style={{ width: `${((currentIdx + 1) / sessionIds.length) * 100}%` }} />
          </div>
          <span className="text-xs font-medium text-slate-500">{currentIdx + 1}/{sessionIds.length}</span>
        </div>
      </div>

      <div className="flex-1 max-w-lg mx-auto w-full px-4 py-6 flex flex-col">
        <div className="card p-6 mb-6 flex-1">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xs font-bold text-indigo-500 bg-indigo-50 px-2 py-1 rounded-full">Задача {currentIdx + 1}</span>
            <span className="text-xs text-slate-400">Сложность: {Math.round(task.difficulty * 100)}%</span>
          </div>
          <h2 className="text-lg font-semibold text-slate-800 mb-3 leading-relaxed">
            <MixedText text={task.content.text} />
          </h2>
          {task.content.formula && (
            <div className="bg-slate-50 p-4 rounded-xl text-center border border-slate-100">
              <MixedText text={`$$${task.content.formula}$$`} />
            </div>
          )}
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-500 mb-2">Ваш ответ</label>
          <input
            type="text"
            value={answer}
            onChange={e => setAnswer(e.target.value)}
            onKeyDown={e => e.key === "Enter" && submitAnswer()}
            className="w-full bg-white border border-slate-200 rounded-2xl px-5 py-4 text-lg focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-transparent transition shadow-sm"
            placeholder="Введите ответ..."
            autoFocus
          />
        </div>

        <button
          onClick={submitAnswer}
          disabled={!answer.trim() || submitting}
          className="btn-primary w-full py-4 text-lg font-bold"
        >
          {submitting ? (
            <span className="flex items-center justify-center gap-2">
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Проверяем...
            </span>
          ) : "Проверить"}
        </button>
      </div>
    </div>
  )
}
