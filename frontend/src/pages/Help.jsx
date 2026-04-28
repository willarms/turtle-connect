import { Link } from 'react-router-dom'

export default function Help() {
  return (
    <div className="min-h-screen bg-[var(--turtle-bg)] py-10 px-6">
      <div className="max-w-3xl mx-auto">

        <Link
          to="/"
          className="text-sm text-[var(--turtle-text-muted)] hover:text-[var(--turtle-green)]"
        >
          ← Back
        </Link>

        <div className="mt-4 bg-white rounded-2xl border p-6 shadow-sm">

          <h1 className="text-2xl font-bold text-[var(--turtle-text)] mb-2">
            Help & Support
          </h1>

          <p className="text-[var(--turtle-text-muted)] mb-6">
            Everything you need to use Turtle Connect safely and effectively.
          </p>

          {/* SECTION 1 */}
          <h2 className="text-lg font-semibold mb-2">📱 Getting Started</h2>
          <p className="text-[var(--turtle-text-muted)] mb-4">
            Join groups based on shared interests. Once you join, you can start calls,
            message members, and track your activity.
          </p>

          {/* SECTION 2 */}
          <h2 className="text-lg font-semibold mb-2">📞 Making Calls</h2>
          <p className="text-[var(--turtle-text-muted)] mb-4">
            Click “Join Google Meet” inside a group. After your call, you’ll be asked to
            log how long you participated.
          </p>

          {/* SECTION 3 */}
          <h2 className="text-lg font-semibold mb-2">🛡 Safety & Reporting</h2>
          <p className="text-[var(--turtle-text-muted)] mb-4">
            If something feels unsafe, click the report icon inside any group.
            Reports are anonymous and reviewed by our team.
          </p>

          {/* SECTION 4 */}
          <h2 className="text-lg font-semibold mb-2">👥 Leaving a Group</h2>
          <p className="text-[var(--turtle-text-muted)] mb-4">
            You can leave any group at any time using the “Leave Group” button in the group page.
          </p>

          {/* SECTION 5 */}
          <h2 className="text-lg font-semibold mb-2">📧 Contact Support</h2>
          <p className="text-[var(--turtle-text-muted)] mb-2">
            Need help?
          </p>

          <a
            href="mailto:fdougher@nd.edu"
            className="text-[var(--turtle-green)] font-medium hover:underline"
          >
            support@turtleconnect.com
          </a>

        </div>
      </div>
    </div>
  )
}