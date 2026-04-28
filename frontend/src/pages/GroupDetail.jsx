import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { createMeetLink, getGoogleAuthorizeUrl, getGroup, getMessages, joinGroup, logCall, leaveGroup, submitMeetingReport } from '../services/api'
import socket from '../services/socket'

const DURATION_OPTIONS = [
  { label: 'About 15 minutes', minutes: 15 },
  { label: 'About 30 minutes', minutes: 30 },
  { label: 'About 45 minutes', minutes: 45 },
  { label: 'An hour or more', minutes: null },
]

function formatMinutes(mins) {
  const h = Math.floor(mins / 60)
  const m = mins % 60
  if (m === 0) return h === 1 ? '1 hour' : `${h} hours`
  return h > 0 ? `${h} hr ${m} min` : `${m} min`
}

export default function GroupDetail() {
  const { id } = useParams()
  const [group, setGroup] = useState(null)
  const [loading, setLoading] = useState(true)
  const [meetError, setMeetError] = useState('')
  const [meetCreating, setMeetCreating] = useState(false)
  const [showCallPrompt, setShowCallPrompt] = useState(false)
  const [showHourPicker, setShowHourPicker] = useState(false)
  const [customMinutes, setCustomMinutes] = useState(60)
  const [callLogged, setCallLogged] = useState(false)
  const [showMeetingReport, setShowMeetingReport] = useState(false)
  const [reportFlags, setReportFlags] = useState({
    flag_password_request: false,
    flag_offensive_language: false,
    flag_confusing: false,
    additional_notes: '',
  })
  const [reportSubmitting, setReportSubmitting] = useState(false)
  const [messages, setMessages] = useState([])
  const [chatInput, setChatInput] = useState('')
  const messagesEndRef = useRef(null)

  // Load message history and connect socket when group is a member
  useEffect(() => {
    if (!group?.is_member) return
    getMessages(id).then(res => setMessages(res.data))

    socket.connect()
    socket.emit('join_group', { group_id: id })
    socket.on('new_message', msg => {
      if (String(msg.group_id) === String(id)) {
        setMessages(prev => [...prev, msg])
      }
    })
    return () => {
      socket.off('new_message')
      socket.disconnect()
    }
  }, [id, group?.is_member])

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSendMessage = () => {
    if (!chatInput.trim()) return
    socket.emit('send_message', { group_id: id, content: chatInput.trim() })
    setChatInput('')
  }

  useEffect(() => {
    getGroup(id)
      .then(async res => {
        setGroup(res.data)
        const pending = sessionStorage.getItem('pending_meet_group')
        if (pending === id) {
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

  // Show the call prompt when the user comes back from the Meet tab
  useEffect(() => {
    const handleFocus = () => {
      const callGroupId = sessionStorage.getItem('call_group_id')
      if (callGroupId === id) {
        setShowCallPrompt(true)
      }
    }
    window.addEventListener('focus', handleFocus)
    return () => window.removeEventListener('focus', handleFocus)
  }, [id])

  const handleJoin = async () => {
    await joinGroup(id)
    const res = await getGroup(id)
    setGroup(res.data)
  }

  const handleJoinMeet = () => {
    sessionStorage.setItem('call_group_id', id)
    window.open(group.google_meet_url, '_blank')
  }

  const handleLogCall = async (minutes) => {
    sessionStorage.removeItem('call_group_id')
    setShowCallPrompt(false)
    setShowHourPicker(false)
    try {
      await logCall(id, minutes)
      setCallLogged(true)
      setTimeout(() => setCallLogged(false), 4000)
    } catch {
      // fail silently — not critical
    }
    // Reset report flags and show the safety report step
    setReportFlags({
      flag_password_request: false,
      flag_offensive_language: false,
      flag_confusing: false,
      additional_notes: '',
    })
    setShowMeetingReport(true)
  }

  const handleReportSubmit = async () => {
    setReportSubmitting(true)
    try {
      await submitMeetingReport(id, reportFlags)
    } catch {
      // fail silently — report submission is non-critical
    } finally {
      setReportSubmitting(false)
      setShowMeetingReport(false)
    }
  }

  const handleReportSkip = () => {
    setShowMeetingReport(false)
  }

  const handleDurationChoice = (minutes) => {
    if (minutes === null) {
      setCustomMinutes(60)
      setShowHourPicker(true)
    } else {
      handleLogCall(minutes)
    }
  }

  const handleSkipLog = () => {
    sessionStorage.removeItem('call_group_id')
    setShowCallPrompt(false)
    setShowHourPicker(false)
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

      {/* Call duration prompt overlay */}
      {showCallPrompt && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-6">
          <div className="bg-white rounded-2xl p-8 max-w-sm w-full shadow-xl text-center">
            {!showHourPicker ? (
              <>
                <div className="text-5xl mb-4">👋</div>
                <h2 className="text-2xl font-bold text-[var(--turtle-text)] mb-2">Welcome back!</h2>
                <p className="text-lg text-[var(--turtle-text-muted)] mb-6">How long were you on the call?</p>
                <div className="grid grid-cols-2 gap-3 mb-4">
                  {DURATION_OPTIONS.map(({ label, minutes }) => (
                    <button
                      key={label}
                      onClick={() => handleDurationChoice(minutes)}
                      className="py-5 px-3 bg-[var(--turtle-green-light)] border-2 border-[var(--turtle-green)] text-[var(--turtle-green)] text-base font-semibold rounded-xl hover:bg-[var(--turtle-green)] hover:text-white transition-colors"
                    >
                      {label}
                    </button>
                  ))}
                </div>
                <button
                  onClick={handleSkipLog}
                  className="w-full py-3 text-[var(--turtle-text-muted)] text-base hover:text-[var(--turtle-text)] transition-colors"
                >
                  I didn't end up joining
                </button>
              </>
            ) : (
              <>
                <div className="text-5xl mb-4">⏱️</div>
                <h2 className="text-2xl font-bold text-[var(--turtle-text)] mb-2">How long?</h2>
                <p className="text-lg text-[var(--turtle-text-muted)] mb-6">Use the buttons to set the time</p>
                <div className="flex items-center justify-center gap-6 mb-8">
                  <button
                    onClick={() => setCustomMinutes(m => Math.max(60, m - 15))}
                    className="w-14 h-14 rounded-full bg-[var(--turtle-green-light)] border-2 border-[var(--turtle-green)] text-[var(--turtle-green)] text-3xl font-bold flex items-center justify-center hover:bg-[var(--turtle-green)] hover:text-white transition-colors"
                  >
                    −
                  </button>
                  <span className="text-2xl font-bold text-[var(--turtle-text)] min-w-[7rem] text-center">
                    {formatMinutes(customMinutes)}
                  </span>
                  <button
                    onClick={() => setCustomMinutes(m => m + 15)}
                    className="w-14 h-14 rounded-full bg-[var(--turtle-green-light)] border-2 border-[var(--turtle-green)] text-[var(--turtle-green)] text-3xl font-bold flex items-center justify-center hover:bg-[var(--turtle-green)] hover:text-white transition-colors"
                  >
                    +
                  </button>
                </div>
                <button
                  onClick={() => handleLogCall(customMinutes)}
                  className="w-full py-4 bg-[var(--turtle-green)] text-white text-lg font-semibold rounded-xl hover:bg-[var(--turtle-green-dark)] transition-colors mb-3"
                >
                  Save
                </button>
                <button
                  onClick={() => setShowHourPicker(false)}
                  className="w-full py-3 text-[var(--turtle-text-muted)] text-base hover:text-[var(--turtle-text)] transition-colors"
                >
                  ← Go back
                </button>
              </>
            )}
          </div>
        </div>
      )}

      {/* Post-meeting safety report modal */}
      {showMeetingReport && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-6">
          <div className="bg-white rounded-2xl p-8 max-w-sm w-full shadow-xl">
            <div className="text-5xl mb-4 text-center">🛡️</div>
            <h2 className="text-2xl font-bold text-[var(--turtle-text)] mb-2 text-center">
              Before you go
            </h2>
            <p className="text-base text-[var(--turtle-text-muted)] mb-6 text-center leading-relaxed">
              Did anything concern you during the meeting? Your answers are private.
            </p>

            <div className="space-y-3 mb-6">
              {[
                { key: 'flag_password_request', label: 'Someone asked for my password or login information' },
                { key: 'flag_offensive_language', label: 'Someone used offensive or upsetting language' },
                { key: 'flag_confusing',          label: 'Something happened that I didn\'t understand' },
              ].map(({ key, label }) => (
                <label
                  key={key}
                  className={`flex items-start gap-4 py-4 px-4 rounded-xl border-2 cursor-pointer transition-colors ${
                    reportFlags[key]
                      ? 'border-[var(--turtle-green)] bg-[var(--turtle-green-light)]'
                      : 'border-[var(--turtle-border)] bg-gray-50 hover:border-[var(--turtle-green)]'
                  }`}
                >
                  <input
                    type="checkbox"
                    className="mt-0.5 w-5 h-5 accent-[var(--turtle-green)] shrink-0"
                    checked={reportFlags[key]}
                    onChange={e => setReportFlags(f => ({ ...f, [key]: e.target.checked }))}
                  />
                  <span className="text-base text-[var(--turtle-text)] leading-snug">{label}</span>
                </label>
              ))}
            </div>

            <div className="mb-6">
              <label className="block text-base font-medium text-[var(--turtle-text)] mb-2">
                Tell us more <span className="font-normal text-[var(--turtle-text-muted)]">(optional)</span>
              </label>
              <textarea
                rows={3}
                placeholder="Describe what happened, or name the person who concerned you…"
                value={reportFlags.additional_notes}
                onChange={e => setReportFlags(f => ({ ...f, additional_notes: e.target.value }))}
                className="w-full rounded-xl border-2 border-[var(--turtle-border)] px-4 py-3 text-base text-[var(--turtle-text)] placeholder:text-[var(--turtle-text-muted)] focus:outline-none focus:border-[var(--turtle-green)] resize-none"
              />
            </div>

            <button
              onClick={handleReportSubmit}
              disabled={reportSubmitting}
              className="w-full py-4 bg-[var(--turtle-green)] text-white text-lg font-semibold rounded-xl hover:bg-[var(--turtle-green-dark)] transition-colors mb-3 disabled:opacity-60"
            >
              {reportSubmitting ? 'Sending…' : 'Submit Report'}
            </button>
            <button
              onClick={handleReportSkip}
              className="w-full py-3 text-[var(--turtle-text-muted)] text-base hover:text-[var(--turtle-text)] transition-colors"
            >
              Everything was fine
            </button>
          </div>
        </div>
      )}

      <div className="max-w-2xl mx-auto">
        <Link to="/groups" className="text-base text-[var(--turtle-text-muted)] hover:text-[var(--turtle-green)] mb-4 inline-block">
          ← Back to Groups
        </Link>

        <div className="bg-white rounded-2xl border border-[var(--turtle-border)] p-6 shadow-sm">
        <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-xl font-bold text-[var(--turtle-text)]">{group.name}</h1>
              <p className="text-[var(--turtle-text-muted)] text-base mt-1">
                {group.member_count} members
              </p>
            </div>

            <div className="flex items-center gap-2">
              {/* Report button */}
              <Link
                to={`/groups/${id}/report`}
                className="p-2 rounded-lg hover:bg-red-50 text-[var(--turtle-text-muted)] hover:text-red-600 transition-colors relative group"
                aria-label="Report group"
              >
                {/* Bell icon (simple SVG) */}
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="w-5 h-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 17h5l-1.405-1.405C18.21 14.79 18 14.4 18 14V11a6 6 0 10-12 0v3c0 .4-.21.79-.595 1.095L4 17h5m6 0a3 3 0 11-6 0m6 0H9"
                  />
                </svg>

                {/* Tooltip */}
                <span className="absolute right-0 -bottom-8 hidden group-hover:block bg-black text-white text-xs px-2 py-1 rounded">
                  Report
                </span>
              </Link>

              {/* Leave group button (only if member) */}
              {group.is_member && (
                <div className="relative group">
                <button
                  onClick={async () => {
                    await leaveGroup(id)
                    const res = await getGroup(id)
                    setGroup(res.data)
                  }}
                  className="p-2 rounded-lg border border-red-500 text-red-500 hover:bg-red-50 transition-colors"
                  aria-label="Exit group"
                >
                  {/* exit icon */}
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="w-5 h-5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H6a2 2 0 01-2-2V7a2 2 0 012-2h5a2 2 0 012 2v1"
                    />
                  </svg>
                </button>
              
                {/* tooltip */}
                <span className="absolute right-0 -bottom-8 hidden group-hover:block bg-black text-white text-xs px-2 py-1 rounded">
                  Exit Group
                </span>
              </div>
              )}
              

              {/* Join button */}
              {!group.is_member && (
                <button
                  onClick={handleJoin}
                  className="px-6 py-3 bg-[var(--turtle-green)] text-white text-base rounded-lg hover:bg-[var(--turtle-green-dark)] transition-colors"
                >
                  Join Group
                </button>
              )}
            </div>
          </div>

          <p className="text-[var(--turtle-text-muted)] text-base mb-4 leading-relaxed">{group.description}</p>

          <div className="flex flex-wrap gap-2 mb-4">
            {group.topics.map(t => (
              <span key={t} className="px-3 py-1.5 bg-[var(--turtle-green-light)] text-[var(--turtle-green)] text-sm rounded-full">
                {t}
              </span>
            ))}
          </div>

          {group.members?.length > 0 && (
            <div className="mb-6">
              <p className="text-sm font-medium text-[var(--turtle-text-muted)] mb-2">Members</p>
              <div className="flex flex-wrap gap-2">
                {group.members.map(m => (
                  <span key={m.id} className="px-3 py-1.5 bg-gray-100 text-[var(--turtle-text)] text-sm rounded-full">
                    {m.name}
                  </span>
                ))}
              </div>
            </div>
          )}

          {group.is_member && (
            <div className="border-t border-[var(--turtle-border)] pt-4 mt-4">
              <h2 className="text-lg font-semibold text-[var(--turtle-text)] mb-3">Group Chat</h2>
              <div className="h-64 overflow-y-auto bg-gray-50 rounded-xl p-3 mb-3 space-y-2">
                {messages.length === 0
                  ? <p className="text-[var(--turtle-text-muted)] text-sm text-center mt-8">No messages yet. Say hello!</p>
                  : messages.map(m => (
                    <div key={m.id} className="text-base">
                      <span className="font-semibold text-[var(--turtle-green)]">{m.sender_name}: </span>
                      <span className="text-[var(--turtle-text)]">{m.content}</span>
                    </div>
                  ))
                }
                <div ref={messagesEndRef} />
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={e => setChatInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Type a message…"
                  className="flex-1 border-2 border-[var(--turtle-border)] rounded-xl px-4 py-3 text-base focus:outline-none focus:border-[var(--turtle-green)]"
                />
                <button
                  onClick={handleSendMessage}
                  className="px-5 py-3 bg-[var(--turtle-green)] text-white text-base font-semibold rounded-xl hover:bg-[var(--turtle-green-dark)] transition-colors"
                >
                  Send
                </button>
              </div>
            </div>
          )}

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

              {callLogged && (
                <p className="text-center text-[var(--turtle-green)] font-medium text-base bg-[var(--turtle-green-light)] rounded-lg py-3">
                  Great — your call has been logged!
                </p>
              )}

              {group.google_meet_url ? (
                <button
                  onClick={handleJoinMeet}
                  className="flex items-center justify-center gap-2 w-full py-4 bg-[var(--turtle-green)] text-white text-lg rounded-lg font-medium hover:bg-[var(--turtle-green-dark)] transition-colors"
                >
                  📹 Join Google Meet
                </button>
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
