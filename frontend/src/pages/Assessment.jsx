import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { updateProfile } from '../services/api'

const QUESTIONS = [
  { id: "q1", question: "I am talkative", trait: "extraversion", reverse: false },
  { id: "q2", question: "I am reserved", trait: "extraversion", reverse: true },
  { id: "q3", question: "I am full of energy", trait: "extraversion", reverse: false },
  { id: "q4", question: "I tend to be quiet", trait: "extraversion", reverse: true },

  { id: "q5", question: "I am helpful and unselfish with others", trait: "agreeableness", reverse: false },
  { id: "q6", question: "I tend to find fault with others", trait: "agreeableness", reverse: true },
  { id: "q7", question: "I have a forgiving nature", trait: "agreeableness", reverse: false },
  { id: "q8", question: "I am sometimes rude to others", trait: "agreeableness", reverse: true },

  { id: "q9", question: "I do a thorough job", trait: "conscientiousness", reverse: false },
  { id: "q10", question: "I can be somewhat careless", trait: "conscientiousness", reverse: true },
  { id: "q11", question: "I am reliable", trait: "conscientiousness", reverse: false },
  { id: "q12", question: "I tend to be disorganized", trait: "conscientiousness", reverse: true },

  { id: "q13", question: "I get nervous easily", trait: "neuroticism", reverse: false },
  { id: "q14", question: "I am relaxed and handle stress well", trait: "neuroticism", reverse: true },
  { id: "q15", question: "I worry a lot", trait: "neuroticism", reverse: false },
  { id: "q16", question: "I am emotionally stable", trait: "neuroticism", reverse: true },

  { id: "q17", question: "I am curious about many different things", trait: "openness", reverse: false },
  { id: "q18", question: "I have an active imagination", trait: "openness", reverse: false },
  { id: "q19", question: "I am not interested in abstract ideas", trait: "openness", reverse: true },
  { id: "q20", question: "I enjoy thinking about complex problems", trait: "openness", reverse: false },
]

const OPTIONS = [
  { label: "Strongly disagree", value: 1 },
  { label: "Disagree", value: 2 },
  { label: "Neutral", value: 3 },
  { label: "Agree", value: 4 },
  { label: "Strongly agree", value: 5 },
]

export default function Assessment() {
  const [current, setCurrent] = useState(0)
  const [answers, setAnswers] = useState({})
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [showIntro, setShowIntro] = useState(true)

  const { refreshUser } = useAuth()
  const navigate = useNavigate()

  const selectAnswer = (value) => {
  setAnswers(prev => ({ ...prev, [q.id]: value }))
  setError('')
}

  const exitToProfile = () => {
    navigate('/profile')
  }

  const skipAssessment = () => {
    navigate('/groups')
  }

  const next = async () => {
    if (!answers[q.id]) {
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

      // await updateProfile({
      //   personality_scores: sortedScores,
      //   onboarding_complete: true,
      // })

      const token = localStorage.getItem("token")

      // 1. Send quiz answers to backend
      await fetch("http://localhost:8000/api/personality/big5", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ answers }),
      })

      // 2. Run matching (Groq + group assignment)
      await fetch("http://localhost:8000/api/match", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
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
  const selected = answers[q.id]

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
          {OPTIONS.map(option => (
            <button
              key={option.value}
              onClick={() => selectAnswer(option.value)}
              className={`w-full text-left p-4 rounded-lg border transition ${
                selected === option.value
                  ? 'border-[var(--turtle-green)] bg-[var(--turtle-green-light)]'
                  : 'border-[var(--turtle-border)] hover:border-gray-300'
              }`}
            >
              {option.label}
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