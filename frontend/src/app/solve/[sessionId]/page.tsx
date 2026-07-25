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

  const goNext = () => {
    const nextIdx = currentIdx + 1
    if (nextIdx < sessionIds.length) {
      router.push(`/solve/${sessionIds[nextIdx]}?session=${sessionIds.join(",")}&idx=${nextIdx}`)
    } else {
      router.push("/dashboard?done=1")
    }
  }

  const submitAnswer = async () => {
    if (!answer.trim()) return
    setSubmitting(true)
    const timeSpent = (Date.now() - startTime) / 1000
    try {
      const result = await api.post<AnswerResult>("/tasks/submit", {
        task_id: Number(taskId),
        answer: answer.trim(),
        time_spent_seconds: timeSpent,
      })
      const sp = new URLSearchParams({
        correct: String(result.is_correct),
        answer: result.correct_answer || "",
        student: answer.trim(),
        explanation: result.explanation || "",
        ai: result.ai_explanation || "",
        error: result.error_type || "",
        micro: result.micro_task || "",
        session: sessionIds.join(","),
        idx: String(currentIdx),
      })
      router.push(`/result/${taskId}?${sp.toString()}`)
    } catch (err) {
      console.error(err)
      setSubmitting(false)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Загрузка...</div>
  }

  if (!task) {
    return <div className="flex items-center justify-center min-h-screen">Задача не найдена</div>
  }

  return (
    <div className="min-h-screen p-4 max-w-lg mx-auto flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <button onClick={() => router.push("/dashboard")} className="text-gray-400">← Выйти</button>
        <span className="text-sm text-gray-400">Задача {currentIdx + 1} из {sessionIds.length}</span>
      </div>

      <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mb-6">
        <h2 className="text-lg font-semibold mb-4">
          <MixedText text={task.content.text} />
        </h2>
        {task.content.formula && (
          <div className="bg-gray-50 p-3 rounded-lg text-center font-mono text-lg mb-4">
            <MixedText text={`$$${task.content.formula}$$`} />
          </div>
        )}
      </div>

      <div className="flex-1">
        <label className="block text-sm font-medium text-gray-700 mb-2">Ваш ответ:</label>
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
        {submitting ? "Проверяем..." : "Проверить"}
      </button>
    </div>
  )
}
