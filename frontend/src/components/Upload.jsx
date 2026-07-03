import { useState } from 'react'
import { uploadDocument } from '../api'
import { Upload as UploadIcon, CheckCircle, XCircle, Loader } from 'lucide-react'

function Upload({ onUploadSuccess }) {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('idle') // idle | loading | success | error
  const [message, setMessage] = useState('')

  const handleFileChange = (e) => {
    const selected = e.target.files[0]
    if (selected) {
      setFile(selected)
      setStatus('idle')
      setMessage('')
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setStatus('loading')
    try {
      const result = await uploadDocument(file)
      setStatus('success')
      setMessage(`Uploaded ${result.filename} — ${result.total_chunks} chunks stored`)
      if (onUploadSuccess) onUploadSuccess(result)
    } catch (err) {
      setStatus('error')
      setMessage(err.response?.data?.detail || 'Upload failed')
    }
  }

  return (
    <div style={styles.container}>
      <h2 style={styles.heading}>Upload Document</h2>
      <p style={styles.subtext}>Supports .txt, .pdf, .md files</p>

      <div style={styles.uploadBox}>
        <input
          type="file"
          accept=".txt,.pdf,.md"
          onChange={handleFileChange}
          style={styles.fileInput}
          id="file-upload"
        />
        <label htmlFor="file-upload" style={styles.fileLabel}>
          <UploadIcon size={24} />
          <span>{file ? file.name : 'Choose a file'}</span>
        </label>
      </div>

      <button
        onClick={handleUpload}
        disabled={!file || status === 'loading'}
        style={{
          ...styles.button,
          opacity: !file || status === 'loading' ? 0.5 : 1
        }}
      >
        {status === 'loading' ? (
          <>
            <Loader size={18} className="spin" /> Processing...
          </>
        ) : (
          'Upload & Process'
        )}
      </button>

      {status === 'success' && (
        <div style={styles.successMsg}>
          <CheckCircle size={18} />
          <span>{message}</span>
        </div>
      )}

      {status === 'error' && (
        <div style={styles.errorMsg}>
          <XCircle size={18} />
          <span>{message}</span>
        </div>
      )}
    </div>
  )
}

const styles = {
  container: {
    padding: '24px',
    border: '1px solid #e5e7eb',
    borderRadius: '12px',
    backgroundColor: '#ffffff'
  },
  heading: {
    fontSize: '18px',
    fontWeight: 600,
    marginBottom: '4px'
  },
  subtext: {
    fontSize: '13px',
    color: '#6b7280',
    marginBottom: '16px'
  },
  uploadBox: {
    marginBottom: '16px'
  },
  fileInput: {
    display: 'none'
  },
  fileLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '14px',
    border: '2px dashed #d1d5db',
    borderRadius: '8px',
    cursor: 'pointer',
    color: '#374151',
    fontSize: '14px'
  },
  button: {
    width: '100%',
    padding: '10px',
    backgroundColor: '#4f46e5',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: 500,
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px'
  },
  successMsg: {
    marginTop: '12px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    color: '#059669',
    fontSize: '13px'
  },
  errorMsg: {
    marginTop: '12px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    color: '#dc2626',
    fontSize: '13px'
  }
}

export default Upload