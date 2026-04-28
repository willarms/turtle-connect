import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { createGroup } from '../services/api'

export default function CreateGroup() {
  const navigate = useNavigate()

  const [form, setForm] = useState({
    name: '',
    description: '',
    topics: ''
  })

  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      await createGroup({
        ...form,
        topics: form.topics
          .split(',')
          .map(t => t.trim())
          .filter(Boolean)
      })

      navigate('/groups')
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[var(--turtle-bg)] py-10 px-6">
      <div className="max-w-2xl mx-auto">

        {/* Header */}
        <div className="mb-6">
          <Link
            to="/groups"
            className="text-sm text-[var(--turtle-text-muted)] hover:text-[var(--turtle-text)]"
          >
            ← Back to Groups
          </Link>

          <h1 className="text-2xl font-bold text-[var(--turtle-text)] mt-2">
            Create a New Group
          </h1>
          <p className="text-[var(--turtle-text-muted)] text-sm mt-1">
            Start a community around something you care about.
          </p>
        </div>

        {/* Form Card */}
        <form
          onSubmit={handleSubmit}
          className="bg-white border border-[var(--turtle-border)] rounded-xl p-6 shadow-sm"
        >
          {/* Group Name */}
          <div className="mb-5">
            <label className="block text-sm font-medium text-[var(--turtle-text)] mb-1">
              Group Name
            </label>
            <input
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="e.g. Garden Enthusiasts"
              className="w-full px-3 py-2 border border-[var(--turtle-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--turtle-green-light)]"
              required
            />
          </div>

          {/* Description */}
          <div className="mb-5">
            <label className="block text-sm font-medium text-[var(--turtle-text)] mb-1">
              Description
            </label>
            <textarea
              name="description"
              value={form.description}
              onChange={handleChange}
              placeholder="e.g. Connect with fellow gardeners to share tips, seeds, and stories from our gardens."
              rows={4}
              className="w-full px-3 py-2 border border-[var(--turtle-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--turtle-green-light)]"
              required
            />
          </div>

          {/* Topics */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-[var(--turtle-text)] mb-1">
              Topics
            </label>
            <input
              name="topics"
              value={form.topics}
              onChange={handleChange}
              placeholder="e.g. Gardening, Plants, Outdoors"
              className="w-full px-3 py-2 border border-[var(--turtle-border)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--turtle-green-light)]"
            />
            <p className="text-xs text-[var(--turtle-text-muted)] mt-1">
              Separate topics with commas
            </p>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between">
            <Link
              to="/groups"
              className="text-sm text-[var(--turtle-text-muted)] hover:text-[var(--turtle-text)]"
            >
              Cancel
            </Link>

            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2.5 bg-[var(--turtle-green)] text-white text-sm rounded-lg hover:bg-[var(--turtle-green-dark)] transition-colors disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Group'}
            </button>
          </div>
        </form>

        {/* Bottom helper section */}
        
      </div>
    </div>
  )
}