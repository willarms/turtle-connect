import { useEffect, useRef, useState } from 'react'
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
import { getGuardianDashboard, sendGuardianReport } from '../services/api'

const COLORS = ['#5a7a5a', '#8ba88b', '#b5c9b5', '#d4e0d4']

export default function Guardian() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [reportSent, setReportSent] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const sentTimer = useRef(null)

  useEffect(() => {
    if (!user?.id) return
  
    let mounted = true
    setLoading(true)
  
    const fetchData = async () => {
      try {
        const res = await getGuardianDashboard(user.id)
        if (mounted) setData(res.data)
      } finally {
        if (mounted) setLoading(false)
      }
    }
  
    fetchData()
  
    const interval = setInterval(fetchData, 30000)
  
    return () => {
      mounted = false
      clearInterval(interval)
    }
  }, [user])

  const confirmSendReport = async () => {
    setShowConfirm(false)
    setSending(true)
  
    try {
      await sendGuardianReport(user.id)
    setShowSuccess(true)

    setTimeout(() => {
      setShowSuccess(false)
    }, 3000)
    } catch {
      // silently fail
    } finally {
      setSending(false)
    }
  }

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
        <p className="text-[var(--turtle-text-muted)] text-base mb-6">
          Monitoring activity for: {data.senior_name}
        </p>

        {/* Alerts */}
        {data?.alerts?.length > 0 && (
          <div className="bg-white border border-[var(--turtle-border)] rounded-xl p-4 mb-6">
            <h2 className="font-semibold text-[var(--turtle-text)] mb-2 text-base flex items-center gap-1">
              ⚠ Alerts &amp; Notifications
            </h2>
            {data.alerts.map((a, i) => (
              <p key={i} className="text-base text-red-600">{a}</p>
            ))}
          </div>
        )}

        {/* Stats grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {stats.map(s => (
            <div key={s.label} className="bg-white border border-[var(--turtle-border)] rounded-xl p-4">
              <p className="text-[var(--turtle-text-muted)] text-sm mb-1 flex items-center gap-1">
                {s.icon} {s.label}
              </p>
              <p className="text-2xl font-bold text-[var(--turtle-text)]">{s.value}</p>
              <p className="text-sm text-[var(--turtle-text-muted)]">{s.sub}</p>
            </div>
          ))}
        </div>

        {/* Send report button */}
        <div className="mb-6 flex items-center gap-4">
        <button
            onClick={() => setShowConfirm(true)}
            disabled={sending}
            className="px-6 py-3 bg-[var(--turtle-green)] text-white text-base font-medium rounded-xl hover:bg-[var(--turtle-green-dark)] transition-colors disabled:opacity-50"
          >
            📧 Send Report Now
          </button>
          {reportSent && (
            <p className="text-[var(--turtle-green)] font-medium text-base">
              Report sent to guardian!
            </p>
          )}
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white border border-[var(--turtle-border)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--turtle-text)] text-base mb-4">Weekly Activity</h3>
            <p className="text-sm text-[var(--turtle-text-muted)] mb-3">Calls and messages over the past week</p>
            {data.weekly_activity.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={data.weekly_activity}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="day" tick={{ fontSize: 13 }} />
                  <YAxis tick={{ fontSize: 13 }} />
                  <Tooltip />
                  <Legend wrapperStyle={{ fontSize: 13 }} />
                  <Bar dataKey="calls" fill="#5a7a5a" name="Calls" />
                  <Bar dataKey="messages" fill="#b5c9b5" name="Messages" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-[var(--turtle-text-muted)] text-sm text-center py-8">No activity this week yet</p>
            )}
          </div>

          <div className="bg-white border border-[var(--turtle-border)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--turtle-text)] text-base mb-4">Group Participation</h3>
            <p className="text-sm text-[var(--turtle-text-muted)] mb-3">Time spent in each group (%)</p>
            {data.group_participation.length > 0 ? (
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie data={data.group_participation} dataKey="percentage" nameKey="name" cx="50%" cy="45%" outerRadius={75} label={({ percentage }) => `${percentage}%`} labelLine={false}>
                    {data.group_participation.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value, name) => [`${value}%`, name]} />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: 13, paddingTop: 8 }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-[var(--turtle-text-muted)] text-sm text-center py-8">No group activity yet</p>
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white border border-[var(--turtle-border)] rounded-xl p-4">
          <h3 className="font-semibold text-[var(--turtle-text)] text-base mb-4">Recent Activity</h3>
          {data.recent_activity.length > 0 ? (
            <div className="space-y-3">
              {data.recent_activity.map((a, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-[var(--turtle-border)] last:border-0">
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{a.type === 'call' ? '📞' : '💬'}</span>
                    <div>
                      <p className="font-medium text-base text-[var(--turtle-text)]">{a.group}</p>
                      <p className="text-sm text-[var(--turtle-text-muted)]">
                        {a.duration_minutes ? `${a.duration_minutes} min` : ''} · {new Date(a.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <span className={`text-sm px-3 py-1 rounded-full font-medium ${
                    a.type === 'call' ? 'bg-[var(--turtle-green-light)] text-[var(--turtle-green)]' : 'bg-gray-100 text-gray-600'
                  }`}>
                    {a.type === 'call' ? 'Call' : 'Chat'}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[var(--turtle-text-muted)] text-sm text-center py-4">No recent activity yet</p>
          )}
        </div>
      </div>
      {showConfirm && (
      <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
        <div className="bg-white rounded-xl p-6 w-full max-w-sm shadow-lg">
          <h2 className="text-lg font-semibold text-[var(--turtle-text)] mb-2">
            Send Report?
          </h2>

          <p className="text-sm text-[var(--turtle-text-muted)] mb-6">
            This will email the latest activity report to the guardian.
          </p>

          <div className="flex justify-end gap-3">
            <button
              onClick={() => setShowConfirm(false)}
              className="px-4 py-2 text-sm rounded-lg border border-gray-300 hover:bg-gray-50"
            >
              Cancel
            </button>

            <button
              onClick={confirmSendReport}
              className="px-4 py-2 text-sm rounded-lg bg-[var(--turtle-green)] text-white hover:bg-[var(--turtle-green-dark)]"
            >
              Yes, Send
            </button>
          </div>
        </div>
      </div>
    )}
    {showSuccess && (
      <div className="fixed bottom-6 right-6 bg-white border border-[var(--turtle-border)] shadow-lg rounded-xl px-4 py-3 flex items-center gap-2 z-50">
        <span className="text-green-600 text-lg">✔</span>
        <p className="text-sm font-medium text-[var(--turtle-text)]">
          Report sent successfully
        </p>
      </div>
    )}
    </div>
  )
}
