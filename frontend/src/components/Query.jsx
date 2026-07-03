import { useState } from 'react'
import { queryDocument } from '../api'
import { Send, AlertTriangle, CheckCircle, Loader, Zap, ChevronDown, ChevronUp } from 'lucide-react'

function Query({ onQuerySuccess }) {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState('')
  const [showDebug, setShowDebug] = useState(false)
  const [showChunks, setShowChunks] = useState(false)

  const handleSubmit = async () => {
    if (!question.trim()) return
    setStatus('loading')
    setError('')
    try {
      const data = await queryDocument(question, 3)
      setResult(data)
      setStatus('success')
      if (onQuerySuccess) onQuerySuccess(data)
    } catch (err) {
      setStatus('error')
      setError(err.response?.data?.detail || 'Query failed')
    }
  }

  const getScoreColor = (score) => {
    if (score >= 0.7) return '#059669'
    if (score >= 0.4) return '#d97706'
    return '#dc2626'
  }

  const getGradeColor = (grade) => {
    if (!grade) return '#6b7280'
    if (grade.startsWith('A') || grade.startsWith('B')) return '#059669'
    if (grade.startsWith('C')) return '#d97706'
    return '#dc2626'
  }

  const getSeverityColor = (severity) => {
    if (severity === 'healthy') return '#059669'
    if (severity === 'average') return '#d97706'
    if (severity === 'poor') return '#ea580c'
    return '#dc2626'
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Ask a Question</h2>

      <div style={styles.inputRow}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          placeholder="Ask something about your document..."
          style={styles.input}
        />
        <button
          onClick={handleSubmit}
          disabled={status === 'loading' || !question.trim()}
          style={{
            ...styles.button,
            opacity: status === 'loading' || !question.trim() ? 0.5 : 1
          }}
        >
          {status === 'loading' ? <Loader size={18} /> : <Send size={18} />}
        </button>
      </div>

      {error && <p style={styles.errorText}>{error}</p>}

      {result && (
        <div style={styles.resultBox}>

          {/* Cache hit badge */}
          {result.cache_hit && (
            <div style={styles.cacheBadge}>
              <Zap size={14} />
              <span>⚡ Served from cache — saved 1 API call</span>
              {result.matched_question && (
                <span style={styles.matchedQ}>
                  Matched: "{result.matched_question.slice(0, 50)}..."
                </span>
              )}
            </div>
          )}

          {/* Answer */}
          <div style={styles.answerBox}>
            <p style={styles.label}>Answer</p>
            <p style={styles.answerText}>{result.answer}</p>
          </div>

          {/* Hallucination */}
          {result.hallucinated ? (
            <div style={styles.warningBox}>
              <AlertTriangle size={18} color="#dc2626" />
              <span>Hallucination detected — answer may not be grounded in document</span>
            </div>
          ) : (
            <div style={styles.safeBox}>
              <CheckCircle size={18} color="#059669" />
              <span>Answer is grounded in retrieved context</span>
            </div>
          )}

          {/* Score Cards */}
          <div style={styles.scoreGrid}>
            <ScoreCard label="Retrieval" score={result.retrieval_score} color={getScoreColor(result.retrieval_score)} />
            <ScoreCard label="Faithfulness" score={result.faithfulness_score} color={getScoreColor(result.faithfulness_score)} />
            <ScoreCard label="Utilization" score={result.utilization_score} color={getScoreColor(result.utilization_score)} />
          </div>

          {/* Overall Grade */}
          <div style={{ ...styles.gradeBox, borderColor: getGradeColor(result.grade) }}>
            <span style={styles.gradeLabel}>Overall Grade</span>
            <span style={{ ...styles.gradeValue, color: getGradeColor(result.grade) }}>
              {result.grade}
            </span>
          </div>

          {/* Diagnosis */}
          <div style={styles.diagnosisBox}>
            <p style={styles.label}>Diagnosis</p>
            <p style={styles.diagnosisText}>{result.diagnosis}</p>
          </div>

          {/* Debug Suggestions */}
          {result.debug && (
            <div style={styles.debugBox}>
              <button
                onClick={() => setShowDebug(!showDebug)}
                style={styles.debugToggle}
              >
                <span style={{
                  ...styles.severityBadge,
                  backgroundColor: getSeverityColor(result.debug.severity) + '20',
                  color: getSeverityColor(result.debug.severity)
                }}>
                  {result.debug.severity.toUpperCase()}
                </span>
                <span style={styles.debugToggleText}>
                  {result.debug.issues.length} issue(s) found — {showDebug ? 'hide' : 'show'} fixes
                </span>
                {showDebug ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </button>

              {showDebug && (
                <div style={styles.debugContent}>
                  <p style={styles.label}>Issues</p>
                  {result.debug.issues.map((issue, i) => (
                    <div key={i} style={styles.issueItem}>
                      ⚠️ {issue}
                    </div>
                  ))}

                  <p style={{ ...styles.label, marginTop: '12px' }}>Suggested Fixes</p>
                  {result.debug.fixes.map((fix, i) => (
                    <div key={i} style={styles.fixItem}>
                      ✅ {fix}
                    </div>
                  ))}

                  <div style={styles.priorityBox}>
                    <strong>Priority Fix:</strong> {result.debug.priority_fix}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Retrieved Chunks toggle */}
          <button
            onClick={() => setShowChunks(!showChunks)}
            style={styles.chunksToggle}
          >
            {showChunks ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            {showChunks ? 'Hide' : 'Show'} retrieved chunks ({result.retrieved_chunks.length})
          </button>

          {showChunks && (
            <div style={styles.chunksBox}>
              {result.retrieved_chunks.map((chunk, i) => (
                <div key={i} style={styles.chunkItem}>
                  <span style={styles.chunkIndex}>Chunk {i + 1}</span>
                  <p style={styles.chunkText}>{chunk}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function ScoreCard({ label, score, color }) {
  return (
    <div style={styles.scoreCard}>
      <p style={styles.scoreLabel}>{label}</p>
      <p style={{ ...styles.scoreValue, color }}>
        {(score * 100).toFixed(0)}%
      </p>
    </div>
  )
}

const styles = {
  container: { padding: '24px', border: '1px solid #e5e7eb', borderRadius: '12px', backgroundColor: '#ffffff' },
  heading: { fontSize: '18px', fontWeight: 600, marginBottom: '16px' },
  inputRow: { display: 'flex', gap: '8px' },
  input: { flex: 1, padding: '10px 14px', border: '1px solid #d1d5db', borderRadius: '8px', fontSize: '14px', outline: 'none' },
  button: { padding: '10px 16px', backgroundColor: '#4f46e5', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' },
  errorText: { color: '#dc2626', fontSize: '13px', marginTop: '8px' },
  resultBox: { marginTop: '20px', display: 'flex', flexDirection: 'column', gap: '14px' },
  cacheBadge: { display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 14px', backgroundColor: '#fffbeb', border: '1px solid #fcd34d', borderRadius: '8px', fontSize: '13px', color: '#92400e' },
  matchedQ: { fontSize: '11px', color: '#b45309', marginLeft: '8px' },
  answerBox: { padding: '14px', backgroundColor: '#f9fafb', borderRadius: '8px' },
  label: { fontSize: '12px', fontWeight: 600, color: '#6b7280', marginBottom: '6px', textTransform: 'uppercase' },
  answerText: { fontSize: '14px', color: '#111827', lineHeight: 1.5 },
  warningBox: { display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 14px', backgroundColor: '#fef2f2', borderRadius: '8px', fontSize: '13px', color: '#991b1b' },
  safeBox: { display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 14px', backgroundColor: '#f0fdf4', borderRadius: '8px', fontSize: '13px', color: '#166534' },
  scoreGrid: { display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' },
  scoreCard: { padding: '12px', backgroundColor: '#f9fafb', borderRadius: '8px', textAlign: 'center' },
  scoreLabel: { fontSize: '12px', color: '#6b7280', marginBottom: '4px' },
  scoreValue: { fontSize: '22px', fontWeight: 700 },
  gradeBox: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px', border: '2px solid', borderRadius: '8px' },
  gradeLabel: { fontSize: '13px', fontWeight: 500, color: '#374151' },
  gradeValue: { fontSize: '16px', fontWeight: 700 },
  diagnosisBox: { padding: '14px', backgroundColor: '#f9fafb', borderRadius: '8px' },
  diagnosisText: { fontSize: '13px', color: '#374151', lineHeight: 1.5 },
  debugBox: { border: '1px solid #e5e7eb', borderRadius: '8px', overflow: 'hidden' },
  debugToggle: { width: '100%', display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 14px', backgroundColor: '#f9fafb', border: 'none', cursor: 'pointer', fontSize: '13px', color: '#374151' },
  debugToggleText: { flex: 1, textAlign: 'left' },
  severityBadge: { padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: 700 },
  debugContent: { padding: '14px', display: 'flex', flexDirection: 'column', gap: '6px' },
  issueItem: { fontSize: '13px', color: '#991b1b', padding: '6px 10px', backgroundColor: '#fef2f2', borderRadius: '6px' },
  fixItem: { fontSize: '13px', color: '#166534', padding: '6px 10px', backgroundColor: '#f0fdf4', borderRadius: '6px' },
  priorityBox: { marginTop: '8px', padding: '10px', backgroundColor: '#eff6ff', borderRadius: '6px', fontSize: '13px', color: '#1e40af' },
  chunksToggle: { display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 0', backgroundColor: 'transparent', border: 'none', cursor: 'pointer', fontSize: '13px', color: '#6b7280' },
  chunksBox: { display: 'flex', flexDirection: 'column', gap: '8px' },
  chunkItem: { padding: '10px', backgroundColor: '#f9fafb', borderRadius: '8px', borderLeft: '3px solid #4f46e5' },
  chunkIndex: { fontSize: '11px', fontWeight: 600, color: '#4f46e5' },
  chunkText: { fontSize: '12px', color: '#374151', marginTop: '4px', lineHeight: 1.5 }
}

export default Query