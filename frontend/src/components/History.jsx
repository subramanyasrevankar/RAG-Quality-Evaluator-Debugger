import { useState, useEffect } from 'react'
import { getHistory } from '../api'
import { Clock, ChevronDown, ChevronUp } from 'lucide-react'

function History({ refreshTrigger }) {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState(null)

  useEffect(() => {
    loadHistory()
  }, [refreshTrigger])

  const loadHistory = async () => {
    setLoading(true)
    try {
      const data = await getHistory(15)
      setHistory(data)
    } catch (err) {
      console.error('Failed to load history', err)
    }
    setLoading(false)
  }

  const getVerdictColor = (verdict) => {
    if (!verdict) return '#6b7280'
    if (verdict === 'Good') return '#059669'
    if (verdict === 'Average') return '#d97706'
    if (verdict === 'Poor') return '#ea580c'
    return '#dc2626'
  }

  const getScoreColor = (score) => {
    if (!score) return '#6b7280'
    if (score >= 0.7) return '#059669'
    if (score >= 0.4) return '#d97706'
    return '#dc2626'
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return <div style={styles.container}>Loading history...</div>
  }

  return (
    <div style={styles.container}>
      <div style={styles.headerRow}>
        <h2 style={styles.heading}>Query History</h2>
        <span style={styles.count}>{history.length} queries</span>
      </div>

      {history.length === 0 ? (
        <div style={styles.emptyBox}>
          <Clock size={32} color="#d1d5db" />
          <p style={styles.emptyText}>No queries yet</p>
        </div>
      ) : (
        <div style={styles.list}>
          {history.map((run) => (
            <div key={run.id} style={styles.card}>
              {/* Summary row */}
              <div
                style={styles.cardHeader}
                onClick={() => setExpanded(expanded === run.id ? null : run.id)}
              >
                <div style={styles.cardLeft}>
                  <span style={styles.questionText}>
                    {run.question.length > 60
                      ? run.question.slice(0, 60) + '...'
                      : run.question}
                  </span>
                  <span style={styles.timeText}>{formatDate(run.created_at)}</span>
                </div>

                <div style={styles.cardRight}>
                  {/* Score pills */}
                  <span style={{ ...styles.scorePill, color: getScoreColor(run.retrieval_score) }}>
                    R: {run.retrieval_score != null ? `${(run.retrieval_score * 100).toFixed(0)}%` : '—'}
                  </span>
                  <span style={{ ...styles.scorePill, color: getScoreColor(run.faithfulness_score) }}>
                    F: {run.faithfulness_score != null ? `${(run.faithfulness_score * 100).toFixed(0)}%` : '—'}
                  </span>
                  <span style={{ ...styles.scorePill, color: getScoreColor(run.overall_score) }}>
                    {run.overall_score != null ? `${(run.overall_score * 100).toFixed(0)}%` : '—'}
                  </span>

                  {/* Verdict badge */}
                  <span style={{
                    ...styles.verdictBadge,
                    color: getVerdictColor(run.verdict),
                    backgroundColor: getVerdictColor(run.verdict) + '15'
                  }}>
                    {run.verdict || 'N/A'}
                  </span>

                  {expanded === run.id
                    ? <ChevronUp size={16} color="#9ca3af" />
                    : <ChevronDown size={16} color="#9ca3af" />
                  }
                </div>
              </div>

              {/* Expanded answer */}
              {expanded === run.id && (
                <div style={styles.cardBody}>
                  <p style={styles.label}>Answer</p>
                  <p style={styles.answerText}>
                    {run.answer || 'No answer recorded'}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

const styles = {
  container: { padding: '24px', border: '1px solid #e5e7eb', borderRadius: '12px', backgroundColor: '#ffffff' },
  headerRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' },
  heading: { fontSize: '18px', fontWeight: 600 },
  count: { fontSize: '13px', color: '#6b7280', backgroundColor: '#f3f4f6', padding: '4px 10px', borderRadius: '12px' },
  emptyBox: { display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', padding: '40px 0' },
  emptyText: { fontSize: '13px', color: '#9ca3af' },
  list: { display: 'flex', flexDirection: 'column', gap: '8px' },
  card: { border: '1px solid #e5e7eb', borderRadius: '8px', overflow: 'hidden' },
  cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', cursor: 'pointer', backgroundColor: '#fafafa' },
  cardLeft: { display: 'flex', flexDirection: 'column', gap: '4px', flex: 1 },
  questionText: { fontSize: '14px', fontWeight: 500, color: '#111827' },
  timeText: { fontSize: '11px', color: '#9ca3af' },
  cardRight: { display: 'flex', alignItems: 'center', gap: '8px' },
  scorePill: { fontSize: '12px', fontWeight: 600 },
  verdictBadge: { padding: '3px 10px', borderRadius: '12px', fontSize: '11px', fontWeight: 600 },
  cardBody: { padding: '12px 16px', borderTop: '1px solid #e5e7eb', backgroundColor: '#ffffff' },
  label: { fontSize: '11px', fontWeight: 600, color: '#6b7280', textTransform: 'uppercase', marginBottom: '6px' },
  answerText: { fontSize: '13px', color: '#374151', lineHeight: 1.6 }
}

export default History