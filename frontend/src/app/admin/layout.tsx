"use client"

import { useAdmin, AdminAuthProvider } from "@/lib/admin-auth"
import { useRouter, usePathname } from "next/navigation"
import { useEffect, useState } from "react"

const NAV_ITEMS = [
  { label: "Дашборд", href: "/admin/dashboard", icon: "📊", roles: ["super_admin", "analyst"] },
  { label: "Темы и задачи", href: "/admin/topics", icon: "📝", roles: ["super_admin", "content_manager"] },
  { label: "Классы", href: "/admin/grades", icon: "🎒", roles: ["super_admin", "content_manager"] },
  { label: "Пользователи", href: "/admin/users", icon: "👥", roles: ["super_admin", "support"] },
  { label: "Адаптивность", href: "/admin/adaptive", icon: "🧠", roles: ["super_admin"] },
  { label: "ИИ-модерация", href: "/admin/ai", icon: "🤖", roles: ["super_admin", "ai_moderator"] },
  { label: "Экзамены", href: "/admin/exams", icon: "🎓", roles: ["super_admin", "content_manager"] },
  { label: "Биллинг", href: "/admin/billing", icon: "💳", roles: ["super_admin"] },
  { label: "Аналитика", href: "/admin/analytics", icon: "📈", roles: ["super_admin", "analyst"] },
  { label: "Настройки", href: "/admin/settings", icon: "⚙️", roles: ["super_admin"] },
]

function AdminLayoutInner({ children }: { children: React.ReactNode }) {
  const { admin, loading, logout } = useAdmin()
  const router = useRouter()
  const pathname = usePathname()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  useEffect(() => {
    if (!loading && !admin && pathname && pathname !== "/admin/login") {
      router.push("/admin/login")
    }
  }, [admin, loading, router, pathname])

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen bg-gray-900 text-white">Загрузка...</div>
  }

  if (!admin) {
    return <>{children}</>
  }

  const filteredNav = NAV_ITEMS.filter((item) => item.roles.includes(admin.role))

  return (
    <div className="flex h-screen bg-gray-900 text-gray-100">
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden" onClick={() => setSidebarOpen(false)}>
          <div className="absolute inset-0 bg-black/50" />
        </div>
      )}

      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50 w-64 bg-gray-800 border-r border-gray-700 flex flex-col
        transform transition-transform duration-200
        lg:translate-x-0
        ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
      `}>
        <div className="p-4 border-b border-gray-700">
          <h1 className="text-lg font-bold text-indigo-400">ExamAI Admin</h1>
          <p className="text-xs text-gray-500 mt-1">{admin.email}</p>
          <span className="inline-block mt-2 text-xs bg-indigo-900 text-indigo-300 px-2 py-0.5 rounded-full">
            {admin.role === "super_admin" ? "Super Admin" : admin.role}
          </span>
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {filteredNav.map((item) => (
            <button
              key={item.href}
              onClick={() => { router.push(item.href); setSidebarOpen(false) }}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition flex items-center gap-2 ${
                pathname?.startsWith(item.href)
                  ? "bg-indigo-600 text-white"
                  : "text-gray-400 hover:bg-gray-700 hover:text-white"
              }`}
            >
              <span>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>
        <div className="p-3 border-t border-gray-700">
          <button
            onClick={logout}
            className="w-full text-left px-3 py-2 rounded-lg text-sm text-gray-400 hover:bg-gray-700 hover:text-white transition"
          >
            Выйти
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="lg:hidden flex items-center gap-3 p-4 border-b border-gray-700">
          <button onClick={() => setSidebarOpen(true)} className="text-gray-400 text-xl">☰</button>
          <span className="text-sm font-medium">ExamAI Admin</span>
        </div>
        <div className="p-4 lg:p-6">{children}</div>
      </main>
    </div>
  )
}

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <AdminAuthProvider>
      <AdminLayoutInner>{children}</AdminLayoutInner>
    </AdminAuthProvider>
  )
}
