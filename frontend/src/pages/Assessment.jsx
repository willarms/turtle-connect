import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { updateProfile } from '../services/api'

const QUESTIONS = [
  {
    question: 'When facing a problem, I tend to:',
    options: [
      'Focus on doing the right thing and fixing what\'s wrong',
      'Think about how to help others through it',
      'Look for the most efficient solution to succeed',
      'Reflect on my feelings and the deeper meaning',
      'Step back and analyze it objectively',
      'Consider all possible risks and outcomes',
      'Look for the positive opportunities it presents',
      'Take charge and confront it directly',
      'Try to keep the peace and avoid conflict',
    ],
  },
  {
    question: 'In social situations, I usually:',
    options: [
      'Listen more than I speak',
      'Make sure everyone feels included',
      'Get straight to the point',
      'Share stories and personal experiences',
      'Ask thoughtful questions',
      'Plan ahead before speaking',
      'Keep things light and positive',
      'Take the lead',
      'Go along with what others prefer',
    ],
  },
  {
    question: 'My ideal afternoon would be:',
    options: [
      'Volunteering in the community',
      'Spending time with close friends or family',
      'Working on a personal project or goal',
      'Reading, journaling, or creating something',
      'Learning something new',
      'Organizing and planning',
      'Trying something fun and spontaneous',
      'Taking on a challenge',
      'Relaxing at home peacefully',
    ],
  },
  {
    question: 'When I meet someone new, I tend to:',
    options: [
      'Share my values openly',
      'Focus on finding common ground',
      'Keep it professional and efficient',
      'Look for a deep personal connection',
      'Ask lots of questions to understand them',
      'Hold back until I know them better',
      'Bring energy and enthusiasm',
      'Take initiative in the conversation',
      'Let them lead the conversation',
    ],
  },
  {
    question: 'What matters most to me in a group or community?',
    options: [
      'Shared values and integrity',
      'Warmth and care for one another',
      'Getting things done together',
      'Meaningful, authentic interactions',
      'Learning and intellectual growth',
      'Safety and reliability',
      'Fun and shared enjoyment',
      'Clear leadership and direction',
      'Harmony and avoiding conflict',
    ],
  },
]

export default function Assessment() {
  const [current, setCurrent] = useState(0)
  const [answers, setAnswers] = useState({})
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [showIntro, setShowIntro] = useState(true)

  const { refreshUser } = useAuth()
  const navigate = useNavigate()

  const selectAnswer = (option) => {
    setAnswers(prev => ({ ...prev, [current]: option }))
    setError('')
  }

  const exitToProfile = () => {
    navigate('/profile')
  }

  const skipAssessment = () => {
    navigate('/groups')
  }

  const next = async () => {
    if (!answers[current]) {
      setError('Please select an option before continuing.')
      return
    }

    setError('')

    if (current < QUESTIONS.length - 1) {
      setCurrent(c => c + 1)
      return
    }

    // FINAL STEP
    if (Object.keys(answers).length < QUESTIONS.length) {
      setError('Please answer all questions before finishing.')
      return
    }

    setSaving(true)

    try {
      const sortedScores = Object.keys(answers)
      .sort((a, b) => Number(a) - Number(b))
      .reduce((acc, key) => {
        acc[key] = answers[key]
        return acc
      }, {})

      await updateProfile({
        personality_scores: sortedScores,
        onboarding_complete: true,
      })

      await refreshUser()
      navigate('/groups')
    } catch {
      setSaving(false)
      setError('Failed to save your results. Please try again.')
    }
  }

  const prev = () => {
    if (current > 0) setCurrent(c => c - 1)
  }

  const progress = ((current + 1) / QUESTIONS.length) * 100
  const q = QUESTIONS[current]
  const selected = answers[current]

  return (
    <div className="min-h-screen bg-[var(--turtle-bg)] py-10 px-4 relative">

      {/* INTRO MODAL */}
      {showIntro && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white max-w-lg w-full rounded-2xl p-8 border border-[var(--turtle-border)] shadow-lg">

            <h2 className="text-xl font-semibold mb-3">
              Before you begin
            </h2>

            <p className="text-[var(--turtle-text-muted)] mb-6">
              This personality assessment helps us match you with compatible groups.
              Your responses are confidential and only used for matching.
            </p>

            <div className="flex gap-3">
              <button
                onClick={skipAssessment}
                className="w-1/2 py-3 rounded-lg border border-[var(--turtle-border)] hover:bg-gray-50"
              >
                Skip
              </button>

              <button
                onClick={() => setShowIntro(false)}
                className="w-1/2 bg-[var(--turtle-green)] text-white py-3 rounded-lg hover:bg-[var(--turtle-green-dark)]"
              >
                Continue
              </button>
            </div>

          </div>
        </div>
      )}

      {/* MAIN */}
      <div className={`max-w-2xl mx-auto bg-white rounded-2xl border border-[var(--turtle-border)] p-8 shadow-sm ${showIntro ? 'blur-sm pointer-events-none' : ''}`}>

        {/* HEADER */}
        <div className="flex items-center justify-between mb-2">

          <div className="flex items-center gap-3">
            <button
              onClick={exitToProfile}
              className="text-sm text-[var(--turtle-text-muted)] hover:text-red-500"
            >
              ← Profile
            </button>

            <span className="text-[var(--turtle-green)] text-lg">🧭</span>
            <span className="font-semibold">Personality Assessment</span>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={skipAssessment}
              className="text-sm text-[var(--turtle-text-muted)] hover:text-[var(--turtle-text)]"
            >
              Skip
            </button>

            <span className="text-sm text-[var(--turtle-text-muted)]">
              {current + 1}/{QUESTIONS.length}
            </span>
          </div>

        </div>

        {/* PROGRESS */}
        <div className="w-full bg-[var(--turtle-border)] rounded-full h-2 mb-4">
          <div
            className="bg-[var(--turtle-green)] h-2 rounded-full"
            style={{ width: `${progress}%` }}
          />
        </div>

        <h2 className="text-xl font-semibold mb-4">{q.question}</h2>

        {error && <p className="text-red-500 text-sm mb-3">{error}</p>}

        <div className="space-y-2 mb-6">
          {q.options.map(option => (
            <button
              key={option}
              onClick={() => selectAnswer(option)}
              className={`w-full text-left p-4 rounded-lg border transition ${
                selected === option
                  ? 'border-[var(--turtle-green)] bg-[var(--turtle-green-light)]'
                  : 'border-[var(--turtle-border)] hover:border-gray-300'
              }`}
            >
              {option}
            </button>
          ))}
        </div>

        {/* NAV */}
        <div className="flex justify-between">
          <button onClick={prev} disabled={current === 0}>
            ← Back
          </button>

          <button
            onClick={next}
            disabled={!selected || saving}
            className="px-6 py-3 bg-[var(--turtle-green)] text-white rounded-lg disabled:opacity-50"
          >
            {saving ? 'Saving...' : current === QUESTIONS.length - 1 ? 'Finish' : 'Next →'}
          </button>
        </div>

      </div>
    </div>
  )
}