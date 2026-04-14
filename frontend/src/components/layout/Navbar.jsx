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
    <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
      <Link to="/" className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-[var(--turtle-green)] flex items-center justify-center">
          <span className="text-white text-xs font-bold">T</span>
        </div>
        <div>
          <div className="font-semibold text-[var(--turtle-text)] text-sm leading-tight">Turtle</div>
          <div className="text-[10px] text-[var(--turtle-text-muted)] leading-tight">Connect at Your Own Pace</div>
        </div>
      </Link>

      {user ? (
        <div className="flex items-center gap-6 text-sm text-[var(--turtle-text-muted)]">
          <Link to="/groups" className="hover:text-[var(--turtle-green)] transition-colors flex items-center gap-1">
            My Groups
          </Link>
          <Link to="/profile" className="hover:text-[var(--turtle-green)] transition-colors">
            Profile
          </Link>
          <Link to="/guardian" className="hover:text-[var(--turtle-green)] transition-colors">
            Guardian
          </Link>
          <button
            onClick={handleLogout}
            className="hover:text-[var(--turtle-green)] transition-colors"
          >
            Logout
          </button>
        </div>
      ) : (
        <Link
          to="/login"
          className="px-4 py-2 border border-gray-300 rounded-md text-sm text-[var(--turtle-text)] hover:border-[var(--turtle-green)] transition-colors"
        >
          Login
        </Link>
      )}
    </nav>
  )
}
