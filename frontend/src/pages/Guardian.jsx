import { useEffect, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useAuth } from '../context/AuthContext'
import { getGuardianDashboard } from '../services/api'

const COLORS = ['#5a7a5a', '#8ba88b', '#b5c9b5', '#d4e0d4']

export default function Guardian() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user?.id) return
  
    const fetchData = () =>
      getGuardianDashboard(user.id).then(res => setData(res.data))
  
    fetchData()
    const interval = setInterval(fetchData, 30000)
  
    return () => clearInterval(interval)
  }, [user])

  if (loading) return <div className="flex items-center justify-center min-h-screen"><p className="text-[var(--turtle-text-muted)]">Loading dashboard...</p></div>
  if (!data) return <div>No dashboard data</div>

  const stats = [
    { label: 'Total Calls', value: data.total_calls, sub: 'This week', icon: '📞' },
    { label: 'Messages', value: data.total_messages, sub: 'This week', icon: '💬' },
    { label: 'Avg Duration', value: `${data.avg_duration_minutes}m`, sub: 'Per call', icon: '⏱' },
    { label: 'Active Groups', value: data.active_groups, sub: 'Joined groups', icon: '👥' },
  ]

  return (
    <div className="min-h-screen bg-[var(--turtle-bg)] py-8 px-6">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-[var(--turtle-green)] text-xl">🛡️</span>
          <h1 className="text-2xl font-bold text-[var(--turtle-text)]">Guardian Dashboard</h1>
        </div>
        <p className="text-[var(--turtle-text-muted)] text-sm mb-6">
          Monitoring activity for: {data.senior_name}
        </p>

        {/* Alerts */}
        {data.alerts.length > 0 && (
          <div className="bg-white border border-[var(--turtle-border)] rounded-xl p-4 mb-6">
            <h2 className="font-semibold text-[var(--turtle-text)] mb-2 text-sm flex items-center gap-1">
              ⚠ Alerts &amp; Notifications
            </h2>
            {data.alerts.map((a, i) => (
              <p key={i} className="text-sm text-red-600">{a}</p>
            ))}
          </div>
        )}

        {/* Stats grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {stats.map(s => (
            <div key={s.label} className="bg-white border border-[var(--turtle-border)] rounded-xl p-4">
              <p className="text-[var(--turtle-text-muted)] text-xs mb-1 flex items-center gap-1">
                {s.icon} {s.label}
              </p>
              <p className="text-2xl font-bold text-[var(--turtle-text)]">{s.value}</p>
              <p className="text-xs text-[var(--turtle-text-muted)]">{s.sub}</p>
            </div>
          ))}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white border border-[var(--turtle-border)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--turtle-text)] text-sm mb-4">Weekly Activity</h3>
            <p className="text-xs text-[var(--turtle-text-muted)] mb-3">Calls and messages over the past week</p>
            {data.weekly_activity.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={data.weekly_activity}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="calls" fill="#5a7a5a" name="Calls" />
                  <Bar dataKey="messages" fill="#b5c9b5" name="Messages" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-[var(--turtle-text-muted)] text-xs text-center py-8">No activity this week yet</p>
            )}
          </div>

          <div className="bg-white border border-[var(--turtle-border)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--turtle-text)] text-sm mb-4">Group Participation</h3>
            <p className="text-xs text-[var(--turtle-text-muted)] mb-3">Time spent in each group (%)</p>
            {data.group_participation.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie data={data.group_participation} dataKey="percentage" nameKey="name" cx="50%" cy="50%" outerRadius={80} label={({ name, percentage }) => `${name} ${percentage}%`}>
                    {data.group_participation.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-[var(--turtle-text-muted)] text-xs text-center py-8">No group activity yet</p>
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white border border-[var(--turtle-border)] rounded-xl p-4">
          <h3 className="font-semibold text-[var(--turtle-text)] text-sm mb-4">Recent Activity</h3>
          {data.recent_activity.length > 0 ? (
            <div className="space-y-3">
              {data.recent_activity.map((a, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-[var(--turtle-border)] last:border-0">
                  <div className="flex items-center gap-3">
                    <span className="text-lg">{a.type === 'call' ? '📞' : '💬'}</span>
                    <div>
                      <p className="font-medium text-sm text-[var(--turtle-text)]">{a.group}</p>
                      <p className="text-xs text-[var(--turtle-text-muted)]">
                        {a.duration_minutes ? `${a.duration_minutes} min` : ''} · {new Date(a.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                    a.type === 'call' ? 'bg-[var(--turtle-green-light)] text-[var(--turtle-green)]' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {a.type === 'call' ? 'Call' : 'Chat'}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[var(--turtle-text-muted)] text-xs text-center py-4">No recent activity yet</p>
          )}
        </div>
      </div>
    </div>
  )
}
