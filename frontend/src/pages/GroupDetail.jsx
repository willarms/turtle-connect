import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getGroup, joinGroup } from '../services/api'

export default function GroupDetail() {
  const { id } = useParams()
  const [group, setGroup] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getGroup(id).then(res => setGroup(res.data)).finally(() => setLoading(false))
  }, [id])

  const handleJoin = async () => {
    await joinGroup(id)
    const res = await getGroup(id)
    setGroup(res.data)
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
            <div className="border-t border-[var(--turtle-border)] pt-4">
              <p className="text-base text-[var(--turtle-green)] font-medium text-center">
                You are a member of this group
              </p>
              <p className="text-sm text-[var(--turtle-text-muted)] text-center mt-1">
                Group chat and calling features coming soon
              </p>
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
