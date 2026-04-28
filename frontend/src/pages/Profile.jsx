import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { updateGuardianEmail, updateProfile } from '../services/api'

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

export default function Profile() {
  const { user, refreshUser } = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState(user?.name || '')
  const [selected, setSelected] = useState(user?.profile?.interests || [])
  const [guardianEnabled, setGuardianEnabled] = useState(user?.profile?.guardian_enabled || false)
  const [guardianEmail, setGuardianEmail] = useState(user?.profile?.guardian_email || '')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  const toggle = (label) => {
    setSelected(prev =>
      prev.includes(label) ? prev.filter(i => i !== label) : [...prev, label]
    )
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await updateProfile({ name, interests: selected, guardian_enabled: guardianEnabled })
      if (guardianEnabled && guardianEmail.trim()) {
        await updateGuardianEmail(guardianEmail.trim())
      }
      await refreshUser()
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="min-h-screen bg-[var(--turtle-bg)] py-8 px-6">
      <div className="max-w-2xl mx-auto bg-white rounded-2xl border border-[var(--turtle-border)] p-8 shadow-sm">
        <h1 className="text-xl font-bold text-[var(--turtle-text)] mb-6">Edit Profile</h1>
        
        <div className="mb-6">
          <label className="block font-medium text-[var(--turtle-text)] mb-2 text-base">Your Name</label>
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            className="w-full px-4 py-4 border border-[var(--turtle-border)] rounded-lg text-base focus:outline-none focus:border-[var(--turtle-green)] bg-[var(--turtle-bg)]"
          />
        </div>

        <div className="mb-6">
          <label className="block font-medium text-[var(--turtle-text)] mb-1 text-base">
            Your Interests ({selected.length} selected)
          </label>
          <div className="grid grid-cols-4 gap-3 mt-3">
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
        <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigate('/assessment')}
          className="w-full py-2 text-sm rounded-lg bg-[var(--turtle-green)] text-white hover:bg-[var(--turtle-green-dark)] transition-colors"
        >
          Retake Personality Assessment
        </button>
      </div>

        <div className="mb-6 flex items-center justify-between p-4 border border-[var(--turtle-border)] rounded-xl">
          <div>
            <p className="font-medium text-[var(--turtle-text)] text-base">Guardian Monitoring</p>
            <p className="text-sm text-[var(--turtle-text-muted)] mt-0.5">
              Allow a guardian to monitor your activity for safety
            </p>
          </div>
          <button
            onClick={() => setGuardianEnabled(!guardianEnabled)}
            className={`w-12 h-6 rounded-full relative transition-colors ${guardianEnabled ? 'bg-[var(--turtle-green)]' : 'bg-gray-300'}`}
          >
            <div className={`w-5 h-5 bg-white rounded-full absolute top-0.5 transition-all shadow ${guardianEnabled ? 'right-0.5' : 'left-0.5'}`} />
          </button>
        </div>

        {guardianEnabled && (
          <div className="mb-6">
            <label className="block font-medium text-[var(--turtle-text)] mb-2 text-base">
              Guardian's Email Address
            </label>
            <p className="text-sm text-[var(--turtle-text-muted)] mb-2">
              Weekly activity reports will be sent to this address
            </p>
            <input
              type="email"
              value={guardianEmail}
              onChange={e => setGuardianEmail(e.target.value)}
              placeholder="guardian@example.com"
              className="w-full px-4 py-4 border border-[var(--turtle-border)] rounded-lg text-base focus:outline-none focus:border-[var(--turtle-green)] bg-[var(--turtle-bg)]"
            />
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex-1 py-4 bg-[var(--turtle-green)] text-white text-lg rounded-lg font-medium hover:bg-[var(--turtle-green-dark)] transition-colors disabled:opacity-50"
          >
            {saving ? 'Saving...' : saved ? 'Saved!' : 'Save Changes'}
          </button>
          <button
            onClick={() => navigate('/groups')}
            className="px-6 py-4 border border-[var(--turtle-border)] rounded-lg text-base text-[var(--turtle-text)] hover:border-[var(--turtle-green)] transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
