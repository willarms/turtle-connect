import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { createMeetLink, getGoogleAuthorizeUrl, getGroup, joinGroup } from '../services/api'

export default function GroupDetail() {
  const { id } = useParams()
  const [group, setGroup] = useState(null)
  const [loading, setLoading] = useState(true)
  const [meetError, setMeetError] = useState('')
  const [meetCreating, setMeetCreating] = useState(false)

  useEffect(() => {
    getGroup(id)
      .then(async res => {
        setGroup(res.data)
        const pending = sessionStorage.getItem('pending_meet_group')
        if (pending === id && !res.data.google_meet_url) {
          sessionStorage.removeItem('pending_meet_group')
          setMeetCreating(true)
          try {
            const linkRes = await createMeetLink(id)
            if (linkRes.data.needs_calendar_auth) {
              setMeetError('Calendar permission not granted. Please try creating the link again.')
            } else {
              const refreshed = await getGroup(id)
              setGroup(refreshed.data)
            }
          } catch (err) {
            setMeetError(err.response?.data?.detail || 'Failed to create Meet link.')
          } finally {
            setMeetCreating(false)
          }
        }
      })
      .finally(() => setLoading(false))
  }, [id])

  const handleJoin = async () => {
    await joinGroup(id)
    const res = await getGroup(id)
    setGroup(res.data)
  }

  const handleCreateMeetLink = async () => {
    setMeetError('')
    setMeetCreating(true)
    try {
      const res = await createMeetLink(id)
      if (res.data.needs_calendar_auth) {
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
        sessionStorage.setItem('post_oauth_group', id)
        sessionStorage.setItem('pending_meet_group', id)
        const authRes = await getGoogleAuthorizeUrl('calendar', state, challenge)
        window.location.href = authRes.data.authorize_url
      } else {
        const groupRes = await getGroup(id)
        setGroup(groupRes.data)
      }
    } catch (err) {
      setMeetError(err.response?.data?.detail || 'Failed to create Meet link.')
    } finally {
      setMeetCreating(false)
    }
  }

  if (loading) return <div className="flex items-center justify-center min-h-screen"><p className="text-[var(--turtle-text-muted)]">Loading...</p></div>
  if (!group) return <div className="flex items-center justify-center min-h-screen"><p className="text-[var(--turtle-text-muted)]">Group not found.</p></div>

  return (
    <div className="min-h-screen bg-[var(--turtle-bg)] py-8 px-6">
      <div className="max-w-2xl mx-auto">
        <Link to="/groups" className="text-base text-[var(--turtle-text-muted)] hover:text-[var(--turtle-green)] mb-4 inline-block">
          ← Back to Groups
        </Link>

        <div className="bg-white rounded-2xl border border-[var(--turtle-border)] p-6 shadow-sm">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-xl font-bold text-[var(--turtle-text)]">{group.name}</h1>
              <p className="text-[var(--turtle-text-muted)] text-base mt-1">{group.member_count} members</p>
            </div>
            {!group.is_member && (
              <button
                onClick={handleJoin}
                className="px-6 py-3 bg-[var(--turtle-green)] text-white text-base rounded-lg hover:bg-[var(--turtle-green-dark)] transition-colors"
              >
                Join Group
              </button>
            )}
          </div>

          <p className="text-[var(--turtle-text-muted)] text-base mb-4 leading-relaxed">{group.description}</p>

          <div className="flex flex-wrap gap-2 mb-6">
            {group.topics.map(t => (
              <span key={t} className="px-3 py-1.5 bg-[var(--turtle-green-light)] text-[var(--turtle-green)] text-sm rounded-full">
                {t}
              </span>
            ))}
          </div>

          {group.is_member ? (
            <div className="border-t border-[var(--turtle-border)] pt-4 space-y-3">
              <p className="text-base text-[var(--turtle-green)] font-medium text-center">
                You are a member of this group
              </p>

              {meetError && (
                <p className="text-red-600 text-sm text-center bg-red-50 rounded-lg p-3">{meetError}</p>
              )}

              {meetCreating && (
                <p className="text-[var(--turtle-text-muted)] text-sm text-center">Creating Meet link...</p>
              )}

              {group.google_meet_url ? (
                <a
                  href={group.google_meet_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 w-full py-4 bg-[var(--turtle-green)] text-white text-lg rounded-lg font-medium hover:bg-[var(--turtle-green-dark)] transition-colors"
                >
                  📹 Join Google Meet
                </a>
              ) : (
                <button
                  onClick={handleCreateMeetLink}
                  disabled={meetCreating}
                  className="flex items-center justify-center gap-2 w-full py-4 border-2 border-[var(--turtle-green)] text-[var(--turtle-green)] text-lg rounded-lg font-medium hover:bg-[var(--turtle-green-light)] transition-colors disabled:opacity-50"
                >
                  🔗 {meetCreating ? 'Creating...' : 'Create Meet Link'}
                </button>
              )}
            </div>
          ) : (
            <div className="bg-[var(--turtle-green-light)] rounded-xl p-4 text-center">
              <p className="text-base text-[var(--turtle-text)]">Join this group to connect with members and participate in activities</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
