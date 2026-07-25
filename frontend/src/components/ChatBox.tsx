"use client"

import { useState, useRef, useEffect } from "react"
import { api } from "@/lib/api"
import { MixedText } from "@/components/Latex"

interface Message {
  id?: number
  role: "user" | "assistant"
  content: string
}

export function ChatBox({ taskId }: { taskId: number }) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [sending, setSending] = useState(false)
  const [open, setOpen] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (open && messages.length === 0) {
      api.get<{ messages: Message[] }>(`/chat/history?task_id=${taskId}`)
        .then(d => setMessages(d.messages))
        .catch(() => {})
    }
  }, [open, taskId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const send = async () => {
    if (!input.trim() || sending) return
    const text = input.trim()
    setInput("")
    setSending(true)
    setMessages(prev => [...prev, { role: "user", content: text }])

    try {
      const res = await api.post<{ reply: string }>("/chat/send", {
        task_id: taskId,
        message: text,
      })
      setMessages(prev => [...prev, { role: "assistant", content: res.reply }])
    } catch {
      setMessages(prev => [...prev, { role: "assistant", content: "Не удалось получить ответ. Попробуй позже." }])
    } finally {
      setSending(false)
    }
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="w-full border-2 border-dashed border-indigo-300 py-4 rounded-xl text-indigo-500 font-medium hover:bg-indigo-50 transition"
      >
        💬 Задать вопрос репетитору
      </button>
    )
  }

  return (
    <div className="bg-white rounded-xl border border-gray-100 mb-4">
      <div className="flex justify-between items-center p-3 border-b">
        <h3 className="font-semibold text-sm">💬 ИИ-репетитор</h3>
        <button onClick={() => setOpen(false)} className="text-gray-400 text-sm">✕</button>
      </div>
      <div className="h-64 overflow-y-auto p-3 space-y-3">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] rounded-xl px-3 py-2 text-sm ${
              m.role === "user"
                ? "bg-indigo-500 text-white"
                : "bg-gray-100 text-gray-800"
            }`}>
              <MixedText text={m.content} />
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div className="flex gap-2 p-3 border-t">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && send()}
          placeholder="Спроси о задаче..."
          className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
        <button
          onClick={send}
          disabled={!input.trim() || sending}
          className="bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-600 transition disabled:opacity-50"
        >
          →
        </button>
      </div>
    </div>
  )
}
