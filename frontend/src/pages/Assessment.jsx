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
  const { refreshUser } = useAuth()
  const navigate = useNavigate()

  const selectAnswer = (option) => {
    setAnswers(prev => ({ ...prev, [current]: option }))
  }

  const next = async () => {
    if (current < QUESTIONS.length - 1) {
      setCurrent(c => c + 1)
    } else {
      setSaving(true)
      try {
        await updateProfile({
          personality_scores: answers,
          onboarding_complete: true,
        })
        await refreshUser()
        navigate('/groups')
      } catch {
        setSaving(false)
      }
    }
  }

  const prev = () => { if (current > 0) setCurrent(c => c - 1) }

  const progress = ((current + 1) / QUESTIONS.length) * 100
  const q = QUESTIONS[current]
  const selected = answers[current]

  return (
    <div className="min-h-screen bg-[var(--turtle-bg)] py-10 px-4">
      <div className="max-w-2xl mx-auto bg-white rounded-2xl border border-[var(--turtle-border)] p-8 shadow-sm">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-[var(--turtle-green)] text-lg">🧭</span>
            <span className="font-semibold text-[var(--turtle-text)]">Personality Assessment</span>
          </div>
          <span className="text-base text-[var(--turtle-text-muted)]">
            Question {current + 1} of {QUESTIONS.length}
          </span>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-[var(--turtle-border)] rounded-full h-2.5 mb-4">
          <div
            className="bg-[var(--turtle-green)] h-2.5 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>

        <p className="text-base text-[var(--turtle-text-muted)] mb-4">
          Help us understand your personality to find the best matches for you
        </p>

        <h2 className="text-xl font-semibold text-[var(--turtle-text)] mb-4">{q.question}</h2>

        <div className="space-y-2 mb-8">
          {q.options.map(option => (
            <button
              key={option}
              onClick={() => selectAnswer(option)}
              className={`w-full text-left px-4 py-4 rounded-lg border text-base transition-all ${
                selected === option
                  ? 'border-[var(--turtle-green)] bg-[var(--turtle-green-light)] text-[var(--turtle-text)]'
                  : 'border-[var(--turtle-border)] hover:border-gray-300 text-[var(--turtle-text)]'
              }`}
            >
              {option}
            </button>
          ))}
        </div>

        <div className="flex justify-between">
          <button
            onClick={prev}
            disabled={current === 0}
            className="flex items-center gap-1 text-base text-[var(--turtle-text-muted)] hover:text-[var(--turtle-text)] disabled:opacity-40 transition-colors"
          >
            ← Previous
          </button>
          <button
            onClick={next}
            disabled={!selected || saving}
            className="flex items-center gap-1 px-6 py-4 bg-[var(--turtle-green)] text-white text-base rounded-lg hover:bg-[var(--turtle-green-dark)] disabled:opacity-50 transition-colors"
          >
            {saving ? 'Saving...' : current === QUESTIONS.length - 1 ? 'Finish' : 'Next →'}
          </button>
        </div>
      </div>
    </div>
  )
}
