"use client"

import Link from "next/link"

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="glass sticky top-0 z-10 border-b border-white/20">
        <div className="max-w-5xl mx-auto px-4 py-3 flex justify-between items-center">
          <span className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
            ExamAI
          </span>
          <Link href="/auth/login" className="text-sm font-medium text-indigo-600 hover:text-indigo-800 transition">
            Войти
          </Link>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-4 py-16 text-center animate-fade-in">
        <div className="inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 px-4 py-1.5 rounded-full text-sm font-medium mb-6">
          <span className="w-2 h-2 bg-indigo-500 rounded-full animate-pulse" />
          Открыт набор на 2026
        </div>

        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-4">
          <span className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-500 bg-clip-text text-transparent">
            ExamAI
          </span>
        </h1>

        <p className="text-xl md:text-2xl text-slate-600 mb-2 font-medium">
          Адаптивная подготовка к ЕГЭ по математике
        </p>
        <p className="text-lg text-slate-400 mb-10 max-w-md">
          ИИ-репетитор, который подстраивается под тебя. +20 баллов за 3 месяца.
        </p>

        <div className="flex gap-3 mb-16">
          <Link
            href="/auth/register"
            className="btn-primary px-10 py-4 text-lg"
          >
            Начать бесплатно
          </Link>
          <Link
            href="/auth/login"
            className="glass px-10 py-4 text-lg font-semibold text-slate-700 hover:bg-white/90 transition rounded-2xl"
          >
            Войти
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-3xl w-full">
          {[
            { emoji: "🎯", title: "Адаптивные задания", desc: "Тренажёр подстраивается под ваш уровень и темп обучения" },
            { emoji: "🤖", title: "ИИ-разбор ошибок", desc: "DeepSeek объясняет каждую ошибку и даёт похожий пример" },
            { emoji: "📈", title: "Прогресс за 3 месяца", desc: "Отслеживайте рост по всем 24 темам профильного ЕГЭ" },
          ].map((f, i) => (
            <div key={i} className="card p-6 text-left animate-slide-up" style={{ animationDelay: `${i * 0.15}s` }}>
              <div className="text-3xl mb-3">{f.emoji}</div>
              <h3 className="font-bold text-slate-800 mb-1">{f.title}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>

        <div className="mt-16 glass rounded-3xl px-8 py-6 max-w-2xl w-full text-center animate-slide-up">
          <p className="text-3xl md:text-4xl font-bold text-slate-800 mb-1">+12-20 баллов</p>
          <p className="text-slate-500">средний прирост за 3 месяца регулярных занятий</p>
        </div>
      </main>

      <footer className="text-center py-6 text-sm text-slate-400">
        ExamAI © 2026
      </footer>
    </div>
  )
}
