import { Link, useNavigate, useLocation } from 'react-router-dom'
import { BookOpen, FolderOpen, LogOut, User } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import clsx from 'clsx'

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const navLinks = [
    { to: '/projects', label: 'Projects', icon: FolderOpen },
    { to: '/decisions', label: 'All Decisions', icon: BookOpen },
  ]

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link to="/projects" className="flex items-center gap-2 font-bold text-brand-600 text-lg">
              <BookOpen size={20} />
              DevLog
            </Link>
            <nav className="flex items-center gap-1">
              {navLinks.map(({ to, label, icon: Icon }) => (
                <Link
                  key={to}
                  to={to}
                  className={clsx(
                    'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                    location.pathname.startsWith(to)
                      ? 'bg-brand-50 text-brand-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  )}
                >
                  <Icon size={15} />
                  {label}
                </Link>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1.5 text-sm text-gray-600">
              <User size={14} />
              {user?.name}
            </span>
            <button onClick={handleLogout} className="btn-secondary !py-1 !px-3 text-xs">
              <LogOut size={13} />
              Logout
            </button>
          </div>
        </div>
      </header>
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-6">{children}</main>
    </div>
  )
}
