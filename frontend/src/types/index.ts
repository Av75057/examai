export interface User {
  id: number
  email: string
  name: string
  subscription: "free" | "premium"
  grade: number
  streak_days: number
}

export interface Task {
  id: number
  topic_id: number
  content: TaskContent
  format: "numeric" | "choice" | "short_answer" | "photo"
  difficulty: number
}

export interface TaskContent {
  text: string
  formula?: string
  image?: string
  options?: string[]
}

export interface AnswerResult {
  is_correct: boolean
  correct_answer: string
  explanation?: string
  ai_explanation?: string
  error_type?: string
  micro_task?: string
}

export interface Mastery {
  topic_code: string
  topic_name: string
  score: number
}

export interface ErrorLog {
  id: number
  task_id: number
  error_type: string
  mastered: boolean
  review_stage: number
  created_at: string
  next_review_at: string | null
}

export interface ExamAttempt {
  id: number
  started_at: string
  primary_score: number | null
  test_score: number | null
  completed: boolean
}

export interface SessionProgress {
  session_id: number
  tasks_completed: number
  correct_count: number
  accuracy: number
}
