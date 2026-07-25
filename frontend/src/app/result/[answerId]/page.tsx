"use client"

import { useSearchParams, useRouter, useParams } from "next/navigation"
import { MixedText } from "@/components/Latex"
import { ChatBox } from "@/components/ChatBox"

export default function ResultPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const params = useParams()
  const taskId = Number(params.answerId)

  const isCorrect = searchParams.get("correct") === "true"
  const correctAnswer = searchParams.get("answer") || ""
  const studentAnswer = searchParams.get("student") || ""
  const explanation = searchParams.get("explanation") || ""
  const aiExplanation = searchParams.get("ai") || ""
  const microTask = searchParams.get("micro") || ""
  const sessionIds = (searchParams.get("session") || "").split(",").filter(Boolean)
  const currentIdx = parseInt(searchParams.get("idx") || "0")
  const nextIdx = currentIdx + 1
  const hasNext = nextIdx < sessionIds.length

  const goNext = () => {
    if (hasNext) router.push(`/solve/${sessionIds[nextIdx]}?session=${sessionIds.join(",")}&idx=${nextIdx}`)
    else router.push("/dashboard?done=1")
  }

  return (
    <div className="min-h-screen animate-fade-in">
      <div className="max-w-lg mx-auto px-4 py-6">
        <div className={`text-center py-8 ${isCorrect ? "" : ""}`}>
          <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full mb-4 ${isCorrect ? "bg-emerald-100 text-emerald-600" : "bg-red-100 text-red-500"}`}>
            <span className="text-4xl">{isCorrect ? "✓" : "✗"}</span>
          </div>
          <h1 className={`text-2xl font-bold mb-1 ${isCorrect ? "text-emerald-700" : "text-red-600"}`}>
            {isCorrect ? "Правильно!" : "Ошибка"}
          </h1>
          <p className="text-sm text-slate-400">Задача {currentIdx + 1} из {sessionIds.length}</p>
        </div>

        {!isCorrect && (
          <div className="space-y-3 mb-6">
            <div className="card p-4">
              <p className="text-sm text-slate-500">Ваш ответ: <span className="text-red-500 font-semibold">{studentAnswer}</span></p>
              <p className="text-sm text-slate-500">Правильный: <span className="text-emerald-600 font-semibold"><MixedText text={`$$${correctAnswer}$$`} /></span></p>
            </div>

            {explanation && (
              <div className="card p-4 border-l-4 border-indigo-400">
                <h3 className="text-sm font-semibold text-slate-500 mb-1">Разбор ошибки</h3>
                <div className="text-sm text-slate-700"><MixedText text={explanation} /></div>
              </div>
            )}

            {aiExplanation && (
              <div className="card p-4 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100">
                <h3 className="text-sm font-semibold text-indigo-600 mb-1">🤖 ИИ-разбор</h3>
                <div className="text-sm text-slate-700 whitespace-pre-wrap"><MixedText text={aiExplanation} /></div>
              </div>
            )}

            {microTask && (
              <div className="card p-4 border-l-4 border-amber-400">
                <h3 className="text-sm font-semibold text-slate-500 mb-1">📝 Закрепление</h3>
                <div className="text-sm text-slate-700"><MixedText text={microTask} /></div>
              </div>
            )}

            <ChatBox taskId={taskId} />
          </div>
        )}

        <div className="flex gap-3">
          <button onClick={goNext} className="btn-primary flex-1 py-4 text-base font-bold text-center">
            {hasNext ? `Далее (${nextIdx + 1}/${sessionIds.length})` : "Завершить"}
          </button>
          <button onClick={() => router.push("/dashboard")} className="flex-1 bg-white border border-slate-200 py-4 rounded-2xl text-base font-semibold text-slate-600 hover:bg-slate-50 transition">
            На главную
          </button>
        </div>
      </div>
    </div>
  )
}
