import { useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { googleCallback } from '../services/api'

export default function OAuthCallback() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const { refreshUser } = useAuth()
  const ranOnce = useRef(false)

  useEffect(() => {
    if (ranOnce.current) return
    ranOnce.current = true

    const code = searchParams.get('code')
    const returnedState = searchParams.get('state')
    const error = searchParams.get('error')

    if (error || !code) {
      navigate('/login?error=google_denied')
      return
    }

    const savedState = sessionStorage.getItem('oauth_state')
    const codeVerifier = sessionStorage.getItem('pkce_verifier')
    sessionStorage.removeItem('oauth_state')
    sessionStorage.removeItem('pkce_verifier')

    if (savedState && returnedState !== savedState) {
      navigate('/login?error=state_mismatch')
      return
    }

    const postOAuthGroup = sessionStorage.getItem('post_oauth_group')
    sessionStorage.removeItem('post_oauth_group')

    googleCallback(code, codeVerifier || '')
      .then(async res => {
        localStorage.setItem('token', res.data.access_token)
        // Refresh AuthContext so ProtectedRoute sees the user before we navigate
        await refreshUser()
        const destination = postOAuthGroup ? `/groups/${postOAuthGroup}` : '/groups'
        navigate(destination, { replace: true })
      })
      .catch(() => {
        navigate('/login?error=google_failed')
      })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="flex items-center justify-center min-h-screen bg-[var(--turtle-bg)]">
      <div className="text-center">
        <div className="text-5xl mb-4">🐢</div>
        <p className="text-[var(--turtle-text-muted)] text-lg">Signing you in with Google...</p>
      </div>
    </div>
  )
}
