import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { updateProfile } from '../services/api'

const INTERESTS = [
  { label: 'Gardening', emoji: '🌱' },
  { label: 'Crocheting', emoji: '🧶' },
  { label: 'Knitting', emoji: '🪡' },
  { label: 'Fishing', emoji: '🎣' },
  { label: 'Movies', emoji: '🎬' },
  { label: 'Reading', emoji: '📚' },
  { label: 'Cooking', emoji: '🍳' },
  { label: 'Baking', emoji: '🧁' },
  { label: 'Painting', emoji: '🎨' },
  { label: 'Photography', emoji: '📷' },
  { label: 'Bird Watching', emoji: '🦜' },
  { label: 'Chess', emoji: '♟️' },
  { label: 'Card Games', emoji: '🃏' },
  { label: 'Music', emoji: '🎵' },
  { label: 'Walking', emoji: '🚶' },
  { label: 'Pets', emoji: '🐕' },
]

export default function ProfileSetup() {
  const { user, refreshUser } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState(user?.name || '')
  const [selected, setSelected] = useState([])
  const [guardianEnabled, setGuardianEnabled] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const toggle = (label) => {
    setSelected(prev =>
      prev.includes(label) ? prev.filter(i => i !== label) : [...prev, label]
    )
  }

  const handleSubmit = async () => {
    if (!name.trim()) { setError('Please enter your name.'); return }
    if (selected.length < 3) { setError('Please select at least 3 interests.'); return }
    setError('')
    setSaving(true)
    try {
      await updateProfile({
        name,
        interests: selected,
        guardian_enabled: guardianEnabled,
      })
      await refreshUser()
      navigate('/assessment')
    } catch {
      setError('Could not save your profile. Please try again.')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-[var(--turtle-bg)] py-10 px-4">
      <div className="max-w-2xl mx-auto bg-white rounded-2xl border border-[var(--turtle-border)] p-8 shadow-sm">
        <div className="text-center mb-6">
          <p className="text-[var(--turtle-green)] font-medium text-base">Set Up Your Profile</p>
          <p className="text-[var(--turtle-text-muted)] text-base mt-1">
            Tell us about yourself and select at least 3 interests to help us find the perfect groups for you
          </p>
        </div>

        <div className="mb-6">
          <label className="block font-medium text-[var(--turtle-text)] mb-2">Your Name</label>
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="Enter your name"
            className="w-full px-4 py-4 border border-[var(--turtle-border)] rounded-lg text-base focus:outline-none focus:border-[var(--turtle-green)] bg-[var(--turtle-bg)]"
          />
        </div>

        <div className="mb-6">
          <label className="block font-medium text-[var(--turtle-text)] mb-1">
            Select Your Interests ({selected.length} selected)
          </label>
          <p className="text-[var(--turtle-text-muted)] text-sm mb-3">Choose at least 3 activities you enjoy</p>
          <div className="grid grid-cols-4 gap-3">
            {INTERESTS.map(({ label, emoji }) => (
              <button
                key={label}
                onClick={() => toggle(label)}
                className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all text-center ${
                  selected.includes(label)
                    ? 'border-[var(--turtle-green)] bg-[var(--turtle-green-light)]'
                    : 'border-[var(--turtle-border)] hover:border-[var(--turtle-green)] bg-white'
                }`}
              >
                <span className="text-3xl mb-1">{emoji}</span>
                <span className="text-sm font-medium text-[var(--turtle-text)]">{label}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="mb-6 p-4 border border-[var(--turtle-border)] rounded-xl">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-medium text-[var(--turtle-text)] text-base">Guardian Monitoring</h3>
              <p className="text-[var(--turtle-text-muted)] text-sm mt-1">
                Allow a trusted guardian to monitor your activity and conversation frequency for your safety
              </p>
            </div>
            <div className="ml-4 flex-shrink-0 w-6 h-6 mt-1">
              <input
                type="radio"
                checked={guardianEnabled}
                onChange={() => setGuardianEnabled(!guardianEnabled)}
                className="w-6 h-6 accent-[var(--turtle-green)]"
              />
            </div>
          </div>
          {guardianEnabled && (
            <div className="mt-3 pt-3 border-t border-[var(--turtle-border)] flex items-center justify-between">
              <div>
                <p className="text-base font-medium text-[var(--turtle-text)]">Enable Guardian Access</p>
                <p className="text-sm text-[var(--turtle-text-muted)]">Guardians can view activity stats but not message content</p>
              </div>
              <div className="w-10 h-6 bg-[var(--turtle-green)] rounded-full relative cursor-pointer">
                <div className="w-4 h-4 bg-white rounded-full absolute top-1 right-1 shadow" />
              </div>
            </div>
          )}
        </div>

        {error && <p className="text-red-500 text-base text-center mb-4">{error}</p>}

        <button
          onClick={handleSubmit}
          disabled={saving}
          className="w-full py-4 bg-[var(--turtle-green)] text-white text-lg rounded-lg font-medium hover:bg-[var(--turtle-green-dark)] transition-colors disabled:opacity-50"
        >
          {saving ? 'Saving...' : 'Find My Groups'}
        </button>
      </div>
    </div>
  )
}
