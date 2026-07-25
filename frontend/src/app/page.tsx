"use client"

import Link from "next/link"

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 text-center">
      <h1 className="text-4xl font-bold text-primary mb-4">
        ExamAI
      </h1>
      <p className="text-xl text-gray-600 mb-2">
        Адаптивный тренажёр по математике
      </p>
      <p className="text-lg text-gray-500 mb-8">
        Профиль ЕГЭ, 70+ баллов
      </p>

      <div className="flex gap-4">
        <Link
          href="/auth/register"
          className="bg-primary text-white px-8 py-3 rounded-xl font-semibold hover:bg-primary-dark transition"
        >
          Начать бесплатно
        </Link>
        <Link
          href="/auth/login"
          className="border border-primary text-primary px-8 py-3 rounded-xl font-semibold hover:bg-primary/5 transition"
        >
          Войти
        </Link>
      </div>

      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-2xl">
        <div className="bg-white p-5 rounded-xl shadow-sm">
          <div className="text-2xl mb-2">🎯</div>
          <h3 className="font-semibold mb-1">Адаптивные задания</h3>
          <p className="text-sm text-gray-500">Тренажёр подстраивается под ваш уровень</p>
        </div>
        <div className="bg-white p-5 rounded-xl shadow-sm">
          <div className="text-2xl mb-2">🤖</div>
          <h3 className="font-semibold mb-1">ИИ-разбор ошибок</h3>
          <p className="text-sm text-gray-500">Объяснение каждой ошибки с примерами</p>
        </div>
        <div className="bg-white p-5 rounded-xl shadow-sm">
          <div className="text-2xl mb-2">📊</div>
          <h3 className="font-semibold mb-1">Дневник прогресса</h3>
          <p className="text-sm text-gray-500">Отслеживайте рост по всем 24 темам ЕГЭ</p>
        </div>
      </div>
    </div>
  )
}
