import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getMyGroups, getSuggestedGroups, joinGroup, toggleFavorite } from '../services/api'

function GroupCard({ group, onJoin, onFavorite }) {
  return (
    <div className="bg-white border border-[var(--turtle-border)] rounded-xl p-4">
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-semibold text-[var(--turtle-text)] text-base">{group.name}</h3>
        <div className="flex gap-2">
          <button
            onClick={() => onFavorite(group.id)}
            className={`text-xl transition-colors ${group.is_favorite ? 'text-yellow-400' : 'text-gray-400 hover:text-yellow-300'}`}
            title="Favorite"
          >
            ★
          </button>
        </div>
      </div>
      <p className="text-[var(--turtle-text-muted)] text-sm mb-3 leading-relaxed">{group.description}</p>
      <div className="flex flex-wrap gap-1 mb-3">
        {group.topics.slice(0, 3).map(t => (
          <span key={t} className="px-2 py-1 bg-[var(--turtle-green-light)] text-[var(--turtle-green)] text-sm rounded-full">
            {t}
          </span>
        ))}
      </div>
      <div className="flex items-center justify-between">
        <span className="text-sm text-[var(--turtle-text-muted)]">{group.member_count} members</span>
        <div className="flex gap-2">
          {!group.is_member && (
            <button
              onClick={() => onJoin(group.id)}
              className="px-4 py-2.5 bg-[var(--turtle-green)] text-white text-sm rounded-lg hover:bg-[var(--turtle-green-dark)] transition-colors"
            >
              Join
            </button>
          )}
          <Link
            to={`/groups/${group.id}`}
            className="px-4 py-2.5 border border-[var(--turtle-border)] text-sm text-[var(--turtle-text)] rounded-lg hover:border-[var(--turtle-green)] transition-colors"
          >
            View Group
          </Link>
        </div>
      </div>
    </div>
  )
}

export default function Groups() {
  const { user } = useAuth()
  const [myGroups, setMyGroups] = useState([])
  const [suggested, setSuggested] = useState([])
  const [tab, setTab] = useState('all')
  const [loading, setLoading] = useState(true)

  const load = async () => {
    try {
      const [myRes, sugRes] = await Promise.all([getMyGroups(), getSuggestedGroups()])
      setMyGroups(myRes.data)
      setSuggested(sugRes.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleJoin = async (id) => {
    await joinGroup(id)
    load()
  }

  const handleFavorite = async (id) => {
    await toggleFavorite(id)
    load()
  }

  const displayed = tab === 'favorites'
    ? myGroups.filter(g => g.is_favorite)
    : myGroups

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-[var(--turtle-text-muted)]">Finding your groups...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--turtle-bg)] py-8 px-6">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-[var(--turtle-text)]">Your Groups</h1>
            <p className="text-[var(--turtle-text-muted)] text-sm">
              Based on your interests, we found these wonderful groups for you.
            </p>
          </div>
          <Link
            to="#"
            className="px-4 py-3 border border-[var(--turtle-green)] text-[var(--turtle-green)] text-base rounded-lg hover:bg-[var(--turtle-green-light)] transition-colors"
          >
            + Create Group
          </Link>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 mb-6 text-base border-b border-[var(--turtle-border)] pb-2">
          <button
            onClick={() => setTab('all')}
            className={`pb-1 font-medium transition-colors ${tab === 'all' ? 'text-[var(--turtle-text)] border-b-2 border-[var(--turtle-green)]' : 'text-[var(--turtle-text-muted)]'}`}
          >
            All Groups ({myGroups.length})
          </button>
          <button
            onClick={() => setTab('favorites')}
            className={`pb-1 font-medium transition-colors ${tab === 'favorites' ? 'text-[var(--turtle-text)] border-b-2 border-[var(--turtle-green)]' : 'text-[var(--turtle-text-muted)]'}`}
          >
            Favorites ({myGroups.filter(g => g.is_favorite).length})
          </button>
        </div>

        {displayed.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-10">
            {displayed.map(g => (
              <GroupCard key={g.id} group={g} onJoin={handleJoin} onFavorite={handleFavorite} />
            ))}
          </div>
        ) : (
          <p className="text-[var(--turtle-text-muted)] text-sm mb-10">No groups yet. Check out suggestions below!</p>
        )}

        {suggested.length > 0 && (
          <>
            <h2 className="text-xl font-semibold text-[var(--turtle-text)] mb-4">Suggested For You</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
              {suggested.filter(g => !g.is_member).map(g => (
                <GroupCard key={g.id} group={g} onJoin={handleJoin} onFavorite={handleFavorite} />
              ))}
            </div>
          </>
        )}

        <div className="bg-[var(--turtle-green-light)] rounded-xl p-6 text-center">
          <p className="font-medium text-[var(--turtle-text)] mb-2">Want to explore more interests?</p>
          <p className="text-[var(--turtle-text-muted)] text-base mb-4">
            Update your profile to discover even more groups
          </p>
          <Link
            to="/profile"
            className="px-5 py-3 border border-[var(--turtle-green)] text-[var(--turtle-green)] text-base rounded-lg hover:bg-white transition-colors"
          >
            Update Profile
          </Link>
        </div>
      </div>
    </div>
  )
}
