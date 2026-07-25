"use client"

import { useEffect, useState } from "react"
import { adminApi } from "@/lib/admin-auth"

interface AdaptiveSettings {
  session_length: number
  diagnostic_length: number
  mastery_threshold: number
  difficulty_step_up: number
  difficulty_step_down: number
  streak_for_level_up: number
  streak_for_level_down: number
  new_topic_ratio: number
  review_ratio: number
  irt_model: string
}

const DEFAULTS: AdaptiveSettings = {
  session_length: 12, diagnostic_length: 20, mastery_threshold: 0.85,
  difficulty_step_up: 0.10, difficulty_step_down: 0.15,
  streak_for_level_up: 3, streak_for_level_down: 2,
  new_topic_ratio: 0.2, review_ratio: 0.3, irt_model: "1PL",
}

export default function AdminAdaptive() {
  const [settings, setSettings] = useState<AdaptiveSettings>(DEFAULTS)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    adminApi.get<{ settings: AdaptiveSettings }>("/admin/adaptive/settings")
      .then(d => setSettings(d.settings))
      .catch(() => {})
  }, [])

  const update = (key: keyof AdaptiveSettings, value: number | string) => {
    setSettings(s => ({ ...s, [key]: value }))
  }

  const save = async () => {
    try {
      await adminApi.put("/admin/adaptive/settings", settings)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (e) {
      console.error(e)
    }
  }

  const fields: { key: keyof AdaptiveSettings; label: string; type: string; step?: string }[] = [
    { key: "session_length", label: "Задач в дневной сессии", type: "number" },
    { key: "diagnostic_length", label: "Задач во входной диагностике", type: "number" },
    { key: "mastery_threshold", label: "Порог mastery", type: "number", step: "0.01" },
    { key: "difficulty_step_up", label: "Шаг усложнения", type: "number", step: "0.01" },
    { key: "difficulty_step_down", label: "Шаг упрощения", type: "number", step: "0.01" },
    { key: "streak_for_level_up", label: "Верных подряд для усложнения", type: "number" },
    { key: "streak_for_level_down", label: "Ошибок подряд для упрощения", type: "number" },
    { key: "new_topic_ratio", label: "Доля новых тем", type: "number", step: "0.01" },
    { key: "review_ratio", label: "Доля повторений", type: "number", step: "0.01" },
    { key: "irt_model", label: "Модель IRT", type: "text" },
  ]

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Адаптивный движок</h2>
        <button onClick={save} className={`px-4 py-2 rounded-lg text-sm font-medium transition ${saved ? "bg-green-600" : "bg-indigo-600 hover:bg-indigo-700"} text-white`}>
          {saved ? "Сохранено!" : "Сохранить"}
        </button>
      </div>

      <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
        <div className="grid grid-cols-2 gap-4">
          {fields.map(f => (
            <div key={f.key}>
              <label className="block text-sm text-gray-400 mb-1">{f.label}</label>
              <input
                type={f.type}
                step={f.step || "1"}
                value={settings[f.key]}
                onChange={e => update(f.key, f.type === "number" ? parseFloat(e.target.value) : e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white text-sm"
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
