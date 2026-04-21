import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Home button — always visible */}
        <Link
          to="/"
          className="flex items-center gap-3 px-4 py-3 bg-[var(--turtle-green)] text-white rounded-xl hover:bg-[var(--turtle-green-dark)] transition-colors"
        >
          <span className="text-xl">🏠</span>
          <span className="text-lg font-semibold">Home</span>
        </Link>

        {user ? (
          <div className="flex items-center gap-2">
            <Link
              to="/groups"
              className="flex flex-col items-center px-4 py-2 rounded-xl border-2 border-transparent hover:border-[var(--turtle-green)] hover:bg-[var(--turtle-green-light)] transition-colors"
            >
              <span className="text-2xl">👥</span>
              <span className="text-sm font-medium text-[var(--turtle-text)] mt-0.5">My Groups</span>
            </Link>
            <Link
              to="/profile"
              className="flex flex-col items-center px-4 py-2 rounded-xl border-2 border-transparent hover:border-[var(--turtle-green)] hover:bg-[var(--turtle-green-light)] transition-colors"
            >
              <span className="text-2xl">👤</span>
              <span className="text-sm font-medium text-[var(--turtle-text)] mt-0.5">Profile</span>
            </Link>
            <Link
              to="/guardian"
              className="flex flex-col items-center px-4 py-2 rounded-xl border-2 border-transparent hover:border-[var(--turtle-green)] hover:bg-[var(--turtle-green-light)] transition-colors"
            >
              <span className="text-2xl">🛡️</span>
              <span className="text-sm font-medium text-[var(--turtle-text)] mt-0.5">Guardian</span>
            </Link>
            <button
              onClick={handleLogout}
              className="flex flex-col items-center px-4 py-2 rounded-xl border-2 border-transparent hover:border-red-300 hover:bg-red-50 transition-colors"
            >
              <span className="text-2xl">🚪</span>
              <span className="text-sm font-medium text-[var(--turtle-text)] mt-0.5">Logout</span>
            </button>
          </div>
        ) : (
          <Link
            to="/login"
            className="px-5 py-3 border border-gray-300 rounded-xl text-lg text-[var(--turtle-text)] hover:border-[var(--turtle-green)] transition-colors"
          >
            Login
          </Link>
        )}
      </div>
    </nav>
  )
}
