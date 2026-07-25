"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import type { Task, AnswerResult } from "@/types"
import { MixedText } from "@/components/Latex"

interface ExamTask extends Task {
  student_answer: string
  result: AnswerResult | null
}

export default function ExamSimulatorPage() {
  const router = useRouter()
  const [tasks, setTasks] = useState<ExamTask[]>([])
  const [attemptId, setAttemptId] = useState<number>(0)
  const [timeLeft, setTimeLeft] = useState(235 * 60)
  const [loading, setLoading] = useState(true)
  const [finished, setFinished] = useState(false)
  const [score, setScore] = useState<{ primary: number; test: number } | null>(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    api.get<{ attempt_id: number; duration_minutes: number; tasks: Task[] }>("/exam-sim/start")
      .then(d => {
        setAttemptId(d.attempt_id)
        setTasks(d.tasks.map(t => ({ ...t, student_answer: "", result: null })))
        setTimeLeft(d.duration_minutes * 60)
      })
      .catch(() => router.push("/dashboard"))
      .finally(() => setLoading(false))
  }, [router])

  useEffect(() => {
    if (finished || loading) return
    const timer = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          clearInterval(timer)
          return 0
        }
        return t - 1
      })
    }, 1000)
    return () => clearInterval(timer)
  }, [finished, loading])

  const checkAnswer = async (taskId: number, answer: string, idx: number) => {
    if (!answer.trim()) return
    try {
      const result = await api.post<AnswerResult>(`/exam-sim/${attemptId}/submit`, {
        task_id: taskId,
        answer: answer.trim(),
        time_spent_seconds: 0,
      })
      setTasks(prev => prev.map((t, i) => i === idx ? { ...t, result } : t))
    } catch (err) {
      console.error(err)
    }
  }

  const updateAnswer = (idx: number, answer: string) => {
    setTasks(prev => prev.map((t, i) => i === idx ? { ...t, student_answer: answer } : t))
  }

  const finishExam = async () => {
    setSubmitting(true)
    const answers = tasks.map(t => ({
      task_id: t.id,
      answer: t.student_answer,
      is_correct: t.result?.is_correct || false,
    }))
    try {
      const result = await api.post<{ primary_score: number; test_score: number }>(`/exam-sim/${attemptId}/finish`, answers)
      setScore({ primary: result.primary_score, test: result.test_score })
      setFinished(true)
    } catch (err) {
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  const formatTime = (s: number) => {
    const h = Math.floor(s / 3600)
    const m = Math.floor((s % 3600) / 60)
    const sec = s % 60
    return `${h}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`
  }

  if (loading) return <div className="flex items-center justify-center min-h-screen">Загрузка...</div>

  if (finished && score) {
    return (
      <div className="min-h-screen p-4 max-w-lg mx-auto text-center flex flex-col items-center justify-center">
        <div className="text-6xl mb-4">🎓</div>
        <h1 className="text-2xl font-bold mb-2">Экзамен завершён!</h1>
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 my-6 w-full">
          <p className="text-gray-500 text-sm">Первичный балл</p>
          <p className="text-4xl font-bold text-primary">{score.primary} / 32</p>
          <p className="text-gray-500 text-sm mt-3">Тестовый балл</p>
          <p className="text-4xl font-bold text-green-600">{score.test}</p>
        </div>
        <button onClick={() => router.push("/dashboard")} className="bg-primary text-white px-8 py-4 rounded-2xl text-lg font-bold">
          На главную
        </button>
      </div>
    )
  }

  const part1 = tasks.slice(0, 12)
  const part2 = tasks.slice(12, 18)
  const timeWarning = timeLeft < 600

  return (
    <div className="min-h-screen bg-gray-50">
      <div className={`sticky top-0 z-10 p-3 text-center font-mono text-lg font-bold ${timeWarning ? "bg-red-500 text-white" : "bg-white border-b"}`}>
        {formatTime(timeLeft)}
      </div>

      <div className="p-4 max-w-2xl mx-auto">
        <h1 className="text-xl font-bold mb-2">Пробный ЕГЭ — Профиль</h1>
        <p className="text-gray-500 text-sm mb-6">Часть 1: 12 заданий с кратким ответом</p>

        <div className="space-y-4 mb-8">
          {part1.map((task, i) => (
            <div key={task.id} className="bg-white p-4 rounded-xl border border-gray-100">
              <div className="flex gap-3">
                <span className="text-sm font-bold text-gray-400 w-6">{i + 1}.</span>
                <div className="flex-1">
                  <p className="text-sm mb-2"><MixedText text={task.content.text} /></p>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={task.student_answer}
                      onChange={e => updateAnswer(i, e.target.value)}
                      className="flex-1 border rounded-lg px-3 py-1.5 text-sm"
                      placeholder="Ответ"
                    />
                    <button
                      onClick={() => checkAnswer(task.id, task.student_answer, i)}
                      disabled={!task.student_answer.trim() || task.result !== null}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                        task.result
                          ? task.result.is_correct ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                          : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                      }`}
                    >
                      {task.result ? (task.result.is_correct ? "✓" : "✗") : "Проверить"}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <p className="text-gray-500 text-sm mb-4">Часть 2: 6 заданий с развёрнутым ответом</p>
        <div className="space-y-4 mb-8">
          {part2.map((task, i) => (
            <div key={task.id} className="bg-white p-4 rounded-xl border border-gray-100">
              <div className="flex gap-3">
                <span className="text-sm font-bold text-gray-400 w-6">{i + 13}.</span>
                <div className="flex-1">
                  <p className="text-sm mb-2"><MixedText text={task.content.text} /></p>
                  <textarea
                    value={task.student_answer}
                    onChange={e => updateAnswer(12 + i, e.target.value)}
                    className="w-full border rounded-lg px-3 py-1.5 text-sm min-h-[60px]"
                    placeholder="Введите решение..."
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={finishExam}
          disabled={submitting}
          className="w-full bg-primary text-white py-4 rounded-2xl text-lg font-bold hover:bg-primary-dark transition mb-8 disabled:opacity-50"
        >
          {submitting ? "Проверяем..." : "Завершить экзамен"}
        </button>
      </div>
    </div>
  )
}
