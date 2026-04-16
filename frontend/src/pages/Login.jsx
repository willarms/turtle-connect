import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getGoogleAuthorizeUrl } from '../services/api'

export default function Login() {
  const [isRegister, setIsRegister] = useState(false)
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login, register } = useAuth()
  const navigate = useNavigate()

  const handleGoogleSignIn = async () => {
    // Generate PKCE code verifier + challenge
    const verifier = Array.from(crypto.getRandomValues(new Uint8Array(32)))
      .map(b => b.toString(16).padStart(2, '0')).join('')
    const encoder = new TextEncoder()
    const data = encoder.encode(verifier)
    const digest = await crypto.subtle.digest('SHA-256', data)
    const challenge = btoa(String.fromCharCode(...new Uint8Array(digest)))
      .replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
    const state = crypto.randomUUID()

    sessionStorage.setItem('pkce_verifier', verifier)
    sessionStorage.setItem('oauth_state', state)

    try {
      const res = await getGoogleAuthorizeUrl('login', state, challenge)
      window.location.href = res.data.authorize_url
    } catch {
      setError('Google sign-in is not available right now.')
    }
  }

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

        {/* Google SSO divider */}
        <div className="flex items-center gap-3 mt-5 mb-4">
          <div className="flex-1 h-px bg-[var(--turtle-border)]" />
          <span className="text-sm text-[var(--turtle-text-muted)]">or</span>
          <div className="flex-1 h-px bg-[var(--turtle-border)]" />
        </div>

        <button
          onClick={handleGoogleSignIn}
          type="button"
          className="w-full py-4 flex items-center justify-center gap-3 border border-[var(--turtle-border)] rounded-lg text-base font-medium text-[var(--turtle-text)] hover:border-[var(--turtle-green)] hover:bg-[var(--turtle-green-light)] transition-colors"
        >
          <svg width="20" height="20" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M44.5 20H24v8.5h11.8C34.7 33.9 29.8 37 24 37c-7.2 0-13-5.8-13-13s5.8-13 13-13c3.1 0 5.9 1.1 8.1 2.9l6.4-6.4C34.6 5.1 29.6 3 24 3 12.4 3 3 12.4 3 24s9.4 21 21 21c10.5 0 20-7.6 20-21 0-1.3-.2-2.7-.5-4z" fill="#FFC107"/>
            <path d="M6.3 14.7l7 5.1C15.1 16.1 19.2 13 24 13c3.1 0 5.9 1.1 8.1 2.9l6.4-6.4C34.6 5.1 29.6 3 24 3 16.3 3 9.6 7.9 6.3 14.7z" fill="#FF3D00"/>
            <path d="M24 45c5.5 0 10.5-1.9 14.3-5.1l-6.6-5.6C29.6 36 26.9 37 24 37c-5.8 0-10.7-3.9-12.4-9.3l-7 5.4C7.9 40.7 15.4 45 24 45z" fill="#4CAF50"/>
            <path d="M44.5 20H24v8.5h11.8c-.8 2.4-2.3 4.4-4.3 5.8l6.6 5.6C41.7 36.6 45 30.8 45 24c0-1.3-.2-2.7-.5-4z" fill="#1976D2"/>
          </svg>
          Sign in with Google
        </button>

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
