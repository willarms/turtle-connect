import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const [isRegister, setIsRegister] = useState(false)
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login, register } = useAuth()
  const navigate = useNavigate()

  const update = (field) => (e) => setForm(f => ({ ...f, [field]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      if (isRegister) {
        const user = await register(form.name, form.email, form.password)
        navigate(user.profile?.onboarding_complete ? '/groups' : '/setup')
      } else {
        const user = await login(form.email, form.password)
        navigate(user.profile?.onboarding_complete ? '/groups' : '/setup')
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--turtle-bg)] px-4">
      <div className="bg-white rounded-2xl border border-[var(--turtle-border)] p-8 w-full max-w-sm shadow-sm">
        <div className="text-center mb-6">
          <div className="text-4xl mb-2">🐢</div>
          <h1 className="text-xl font-bold text-[var(--turtle-text)]">
            {isRegister ? 'Join Turtle' : 'Welcome Back'}
          </h1>
          <p className="text-[var(--turtle-text-muted)] text-base mt-1">
            {isRegister ? 'Create your account to get started' : 'Sign in to your account'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div>
              <label className="block text-base font-medium text-[var(--turtle-text)] mb-1">Your Name</label>
              <input
                type="text"
                value={form.name}
                onChange={update('name')}
                required
                placeholder="Enter your name"
                className="w-full px-4 py-4 border border-[var(--turtle-border)] rounded-lg text-base focus:outline-none focus:border-[var(--turtle-green)] bg-[var(--turtle-bg)]"
              />
            </div>
          )}
          <div>
            <label className="block text-base font-medium text-[var(--turtle-text)] mb-1">Email</label>
            <input
              type="email"
              value={form.email}
              onChange={update('email')}
              required
              placeholder="Enter your email"
              className="w-full px-4 py-4 border border-[var(--turtle-border)] rounded-lg text-base focus:outline-none focus:border-[var(--turtle-green)] bg-[var(--turtle-bg)]"
            />
          </div>
          <div>
            <label className="block text-base font-medium text-[var(--turtle-text)] mb-1">Password</label>
            <input
              type="password"
              value={form.password}
              onChange={update('password')}
              required
              placeholder="Enter your password"
              className="w-full px-4 py-4 border border-[var(--turtle-border)] rounded-lg text-base focus:outline-none focus:border-[var(--turtle-green)] bg-[var(--turtle-bg)]"
            />
          </div>

          {error && (
            <p className="text-red-500 text-sm text-center">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 bg-[var(--turtle-green)] text-white text-lg rounded-lg font-medium hover:bg-[var(--turtle-green-dark)] transition-colors disabled:opacity-50"
          >
            {loading ? 'Please wait...' : isRegister ? 'Create Account' : 'Sign In'}
          </button>
        </form>

        <p className="text-center text-base text-[var(--turtle-text-muted)] mt-4">
          {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
          <button
            onClick={() => { setIsRegister(!isRegister); setError('') }}
            className="text-[var(--turtle-green)] font-medium hover:underline"
          >
            {isRegister ? 'Sign In' : 'Join Turtle'}
          </button>
        </p>
      </div>
    </div>
  )
}
