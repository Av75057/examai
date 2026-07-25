"use client"

import { useEffect, useState } from "react"
import { api } from "@/lib/api"

interface StreakData {
  streak: number
  active_dates: string[]
}

interface OverviewData {
  total_answers: number
  correct_answers: number
  accuracy: number
  total_sessions: number
  avg_mastery: number
  topics_mastered: number
  total_topics: number
}

export function useProgress() {
  const [streak, setStreak] = useState(0)
  const [overview, setOverview] = useState<OverviewData | null>(null)

  const load = () => {
    api.get<StreakData>("/progress/streak").then(d => setStreak(d.streak)).catch(() => {})
    api.get<OverviewData>("/progress/overview").then(setOverview).catch(() => {})
  }

  useEffect(() => { load() }, [])

  return { streak, overview, refresh: load }
}
