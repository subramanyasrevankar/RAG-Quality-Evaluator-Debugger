import { useState } from 'react'
import Upload from './components/Upload'
import Query from './components/Query'
import Dashboard from './components/Dashboard'
import History from './components/History'
import { Activity } from 'lucide-react'

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0)
  const [activeTab, setActiveTab] = useState('query')

  const triggerRefresh = () => {
    setRefreshTrigger(prev => prev + 1)
  }

  return (
    <div style={styles.page}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <div style={styles.logo}>
            <Activity size={24} color="#4f46e5" />
            <div>
              <h1 style={styles.title}>RAG Quality Evaluator</h1>
              <p style={styles.subtitle}>Diagnose why your RAG pipeline is failing</p>
            </div>
          </div>

          {/* Tabs */}
          <nav style={styles.nav}>
            {['query', 'dashboard', 'history'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  ...styles.navBtn,
                  backgroundColor: activeTab === tab ? '#4f46e5' : 'transparent',
                  color: activeTab === tab ? '#ffffff' : '#6b7280'
                }}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main style={styles.main}>

        {/* Query Tab */}
        {activeTab === 'query' && (
          <div style={styles.queryLayout}>
            <div style={styles.uploadCol}>
              <Upload onUploadSuccess={triggerRefresh} />
            </div>
            <div style={styles.queryCol}>
              <Query onQuerySuccess={triggerRefresh} />
            </div>
          </div>
        )}

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <Dashboard refreshTrigger={refreshTrigger} />
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <History refreshTrigger={refreshTrigger} />
        )}

      </main>
    </div>
  )
}

const styles = {
  page: {
    minHeight: '100vh',
    backgroundColor: '#f3f4f6',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
  },
  header: {
    backgroundColor: '#ffffff',
    borderBottom: '1px solid #e5e7eb',
    padding: '0 24px'
  },
  headerContent: {
    maxWidth: '1100px',
    margin: '0 auto',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: '64px'
  },
  logo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px'
  },
  title: {
    fontSize: '18px',
    fontWeight: 700,
    color: '#111827',
    margin: 0
  },
  subtitle: {
    fontSize: '12px',
    color: '#6b7280',
    margin: 0
  },
  nav: {
    display: 'flex',
    gap: '4px'
  },
  navBtn: {
    padding: '8px 16px',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 500,
    transition: 'all 0.15s'
  },
  main: {
    maxWidth: '1100px',
    margin: '0 auto',
    padding: '24px'
  },
  queryLayout: {
    display: 'grid',
    gridTemplateColumns: '1fr 1.6fr',
    gap: '20px',
    alignItems: 'start'
  },
  uploadCol: {},
  queryCol: {}
}

export default App