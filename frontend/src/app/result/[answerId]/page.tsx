"use client"

import { useSearchParams, useRouter, useParams } from "next/navigation"
import { MixedText } from "@/components/Latex"
import { ChatBox } from "@/components/ChatBox"

export default function ResultPage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const params = useParams()

  const isCorrect = searchParams.get("correct") === "true"
  const correctAnswer = searchParams.get("answer") || ""
  const studentAnswer = searchParams.get("student") || ""
  const explanation = searchParams.get("explanation") || ""
  const aiExplanation = searchParams.get("ai") || ""
  const errorType = searchParams.get("error") || ""
  const microTask = searchParams.get("micro") || ""

  const sessionIds = (searchParams.get("session") || "").split(",").filter(Boolean)
  const currentIdx = parseInt(searchParams.get("idx") || "0")

  const nextIdx = currentIdx + 1
  const hasNext = nextIdx < sessionIds.length

  const goNext = () => {
    if (hasNext) {
      router.push(`/solve/${sessionIds[nextIdx]}?session=${sessionIds.join(",")}&idx=${nextIdx}`)
    } else {
      router.push("/dashboard?done=1")
    }
  }

  return (
    <div className="min-h-screen p-4 max-w-lg mx-auto">
      <div className="text-center py-8">
        <div className="text-6xl mb-4">{isCorrect ? "✅" : "❌"}</div>
        <h1 className="text-2xl font-bold mb-2">
          {isCorrect ? "Правильно!" : "Ошибка"}
        </h1>
        <p className="text-sm text-gray-400 mb-1">
          Задача {currentIdx + 1} из {sessionIds.length}
        </p>
        {!isCorrect && (
          <p className="text-gray-600">
            Ваш ответ: <span className="text-danger font-medium">{studentAnswer}</span>
            <br />
            Правильный: <span className="text-success font-medium"><MixedText text={`$$${correctAnswer}$$`} /></span>
          </p>
        )}
      </div>

      {!isCorrect && explanation && (
        <div className="bg-white p-4 rounded-xl border border-gray-100 mb-3">
          <h3 className="font-semibold text-sm text-gray-500 mb-1">Разбор ошибки</h3>
          <MixedText text={explanation} className="block" />
        </div>
      )}

      {!isCorrect && aiExplanation && (
        <div className="bg-indigo-50 p-4 rounded-xl border border-indigo-100 mb-3">
          <h3 className="font-semibold text-sm text-indigo-600 mb-1">🤖 ИИ-разбор</h3>
          <MixedText text={aiExplanation} className="block whitespace-pre-wrap text-sm" />
        </div>
      )}

      {!isCorrect && microTask && (
        <div className="bg-amber-50 p-4 rounded-xl border border-amber-100 mb-6">
          <h3 className="font-semibold text-sm text-amber-600 mb-1">📝 Закрепление</h3>
          <MixedText text={microTask} className="block text-sm" />
        </div>
      )}

      {!isCorrect && <ChatBox taskId={Number(params.answerId)} />}

      <div className="flex gap-3">
        <button
          onClick={goNext}
          className="flex-1 bg-primary text-white py-3 rounded-xl font-semibold hover:bg-primary-dark transition"
        >
          {hasNext ? `Следующая задача (${nextIdx + 1}/${sessionIds.length})` : "Завершить"}
        </button>
        <button
          onClick={() => router.push("/dashboard")}
          className="flex-1 border border-gray-300 py-3 rounded-xl font-semibold hover:bg-gray-50 transition"
        >
          На главную
        </button>
      </div>
    </div>
  )
}
