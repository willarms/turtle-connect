import { useParams, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { sendGroupReport } from '../services/api'

const REASONS = [
  'Harassment or bullying',
  'Spam or self-promotion',
  'Unsafe behavior',
  'Inappropriate content',
  'Other',
]

export default function ReportGroup() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [reason, setReason] = useState('')
  const [details, setDetails] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const handleSubmit = async () => {
    if (!reason) return

    setLoading(true)

    try {
      // uses your existing backend email/report system
      await sendGroupReport(id, {
        reason,
        details,
      })

      setSubmitted(true)

    } catch (err) {
      console.error(err)
      alert('Failed to send report')
    } finally {
      setLoading(false)
    }
  }

  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--turtle-bg)] px-6">
        <div className="bg-white p-8 rounded-2xl border text-center shadow-sm max-w-md w-full">
  
          <div className="text-4xl mb-3">🛡️</div>
  
          <h1 className="text-xl font-bold mb-2">
            Report submitted
          </h1>
  
          <p className="text-[var(--turtle-text-muted)] mb-6">
            Thanks for helping keep the community safe. Your report has been sent for review.
          </p>
  
          <button
            onClick={() => navigate(`/groups/${id}`)}
            className="w-full py-3 bg-[var(--turtle-green)] text-white rounded-lg hover:bg-[var(--turtle-green-dark)] transition-colors"
          >
            Got it
          </button>
  
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--turtle-bg)] flex items-center justify-center px-6">
      <div className="bg-white w-full max-w-lg p-6 rounded-2xl border shadow-sm">

        <h1 className="text-xl font-bold mb-1">Report Group</h1>
        <p className="text-sm text-[var(--turtle-text-muted)] mb-6">
          This report will be sent to our safety team.
        </p>

        {/* reason selection */}
        <div className="space-y-2 mb-4">
          {REASONS.map(r => (
            <button
              key={r}
              onClick={() => setReason(r)}
              className={`w-full text-left px-4 py-3 rounded-lg border transition ${
                reason === r
                  ? 'border-red-500 bg-red-50 text-red-600'
                  : 'border-[var(--turtle-border)] hover:bg-gray-50'
              }`}
            >
              {r}
            </button>
          ))}
        </div>

        {/* details */}
        <textarea
          value={details}
          onChange={(e) => setDetails(e.target.value)}
          placeholder="Add any additional context (optional)"
          className="w-full border border-[var(--turtle-border)] rounded-lg p-3 h-28 mb-4"
        />

        <button
          onClick={handleSubmit}
          disabled={!reason || loading}
          className="w-full py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50"
        >
          {loading ? 'Sending...' : 'Submit Report'}
        </button>

        <button
          onClick={() => navigate(-1)}
          className="w-full mt-3 text-sm text-[var(--turtle-text-muted)] hover:text-black"
        >
          Cancel
        </button>
      </div>
    </div>
  )
}