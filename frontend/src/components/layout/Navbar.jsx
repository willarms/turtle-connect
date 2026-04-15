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
    <nav className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <Link to="/" className="flex items-center gap-2">
        <div className="w-10 h-10 rounded-full bg-[var(--turtle-green)] flex items-center justify-center">
          <span className="text-white text-sm font-bold">T</span>
        </div>
        <div>
          <div className="font-semibold text-[var(--turtle-text)] text-base leading-tight">Turtle</div>
          <div className="text-xs text-[var(--turtle-text-muted)] leading-tight">Connect at Your Own Pace</div>
        </div>
      </Link>

      {user ? (
        <div className="flex items-center gap-6 text-base text-[var(--turtle-text-muted)]">
          <Link to="/groups" className="py-1 hover:text-[var(--turtle-green)] transition-colors flex items-center gap-1">
            My Groups
          </Link>
          <Link to="/profile" className="py-1 hover:text-[var(--turtle-green)] transition-colors">
            Profile
          </Link>
          <Link to="/guardian" className="py-1 hover:text-[var(--turtle-green)] transition-colors">
            Guardian
          </Link>
          <button
            onClick={handleLogout}
            className="px-2 py-1 hover:text-[var(--turtle-green)] transition-colors"
          >
            Logout
          </button>
        </div>
      ) : (
        <Link
          to="/login"
          className="px-5 py-3 border border-gray-300 rounded-md text-base text-[var(--turtle-text)] hover:border-[var(--turtle-green)] transition-colors"
        >
          Login
        </Link>
      )}
    </nav>
  )
}
