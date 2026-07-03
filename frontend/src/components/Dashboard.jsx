import { useState, useEffect } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { getHistory, getStats } from '../api'
import { TrendingUp, FileText, Target, Download } from 'lucide-react'

function Dashboard({ refreshTrigger }) {
  const [history, setHistory] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [refreshTrigger])

  const loadData = async () => {
    setLoading(true)
    try {
      const [historyData, statsData] = await Promise.all([
        getHistory(20),
        getStats()
      ])
      setHistory(historyData.reverse())
      setStats(statsData)
    } catch (err) {
      console.error('Failed to load dashboard data', err)
    }
    setLoading(false)
  }

  const handleExportCSV = () => {
    window.open('http://localhost:8000/export/csv', '_blank')
  }

  const chartData = history.map((run, index) => ({
    index: index + 1,
    Retrieval: run.retrieval_score,
    Faithfulness: run.faithfulness_score,
    Utilization: run.utilization_score,
    Overall: run.overall_score
  }))

  if (loading) {
    return <div style={styles.container}>Loading dashboard...</div>
  }

  return (
    <div style={styles.container}>
      <div style={styles.headerRow}>
        <h2 style={styles.heading}>Analytics Dashboard</h2>
        <button onClick={handleExportCSV} style={styles.exportBtn}>
          <Download size={16} />
          Export CSV
        </button>
      </div>

      {/* Stat Cards */}
      <div style={styles.statsGrid}>
        <StatCard
          icon={<FileText size={20} />}
          label="Total Queries"
          value={stats?.total_runs || 0}
        />
        <StatCard
          icon={<Target size={20} />}
          label="Avg Retrieval"
          value={`${((stats?.avg_retrieval_score || 0) * 100).toFixed(0)}%`}
        />
        <StatCard
          icon={<TrendingUp size={20} />}
          label="Avg Faithfulness"
          value={`${((stats?.avg_faithfulness_score || 0) * 100).toFixed(0)}%`}
        />
        <StatCard
          icon={<TrendingUp size={20} />}
          label="Avg Overall"
          value={`${((stats?.avg_overall_score || 0) * 100).toFixed(0)}%`}
        />
      </div>

      {/* Trend Chart */}
      <div style={styles.chartBox}>
        <p style={styles.chartTitle}>Score Trends Over Time</p>
        {chartData.length === 0 ? (
          <p style={styles.emptyText}>No queries yet — ask a question to see trends</p>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="index" tick={{ fontSize: 12 }} />
              <YAxis domain={[0, 1]} tick={{ fontSize: 12 }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="Retrieval" stroke="#4f46e5" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="Faithfulness" stroke="#059669" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="Utilization" stroke="#d97706" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="Overall" stroke="#dc2626" strokeWidth={3} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}

function StatCard({ icon, label, value }) {
  return (
    <div style={styles.statCard}>
      <div style={styles.statIcon}>{icon}</div>
      <div>
        <p style={styles.statLabel}>{label}</p>
        <p style={styles.statValue}>{value}</p>
      </div>
    </div>
  )
}

const styles = {
  container: { padding: '24px', border: '1px solid #e5e7eb', borderRadius: '12px', backgroundColor: '#ffffff' },
  headerRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' },
  heading: { fontSize: '18px', fontWeight: 600 },
  exportBtn: { display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px', backgroundColor: '#4f46e5', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontSize: '13px', fontWeight: 500 },
  statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '20px' },
  statCard: { display: 'flex', alignItems: 'center', gap: '10px', padding: '14px', backgroundColor: '#f9fafb', borderRadius: '8px' },
  statIcon: { color: '#4f46e5' },
  statLabel: { fontSize: '12px', color: '#6b7280' },
  statValue: { fontSize: '18px', fontWeight: 700, color: '#111827' },
  chartBox: { padding: '16px', backgroundColor: '#f9fafb', borderRadius: '8px' },
  chartTitle: { fontSize: '13px', fontWeight: 600, color: '#374151', marginBottom: '12px' },
  emptyText: { fontSize: '13px', color: '#9ca3af', textAlign: 'center', padding: '40px 0' }
}

export default Dashboard