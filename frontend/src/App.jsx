import { useState, useEffect } from 'react'
import './App.css'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [history, setHistory] = useState([])
  const [systemStatus, setSystemStatus] = useState(null)
  const [activeTab, setActiveTab] = useState('query')
  const [sessionId] = useState(() => `session-${Date.now()}`)
  const [showSources, setShowSources] = useState(false)

  // Check system status on load
  useEffect(() => {
    checkSystemHealth()
  }, [])

  const checkSystemHealth = async () => {
    try {
      const result = await fetch(`${API_BASE_URL}/api/health`)
      const data = await result.json()
      setSystemStatus(data)
    } catch (err) {
      console.error('Health check failed:', err)
      setSystemStatus({ status: 'error', message: 'Backend not available' })
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setResponse(null)

    try {
      const result = await fetch(`${API_BASE_URL}/api/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: query,
          session_id: sessionId
        })
      })

      if (!result.ok) {
        const errorData = await result.json()
        throw new Error(errorData.detail || 'Request failed')
      }

      const data = await result.json()
      setResponse(data)
      
      // Add to history
      const newEntry = {
        id: Date.now(),
        question: query,
        response: data,
        timestamp: new Date().toLocaleTimeString()
      }
      setHistory(prev => [newEntry, ...prev])
      
      setQuery('') // Clear the input
    } catch (err) {
      setError(err.message || 'An error occurred while processing your query')
      console.error('Query error:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatSources = (sources) => {
    const { csv_results = [], pdf_results = [] } = sources || {}
    let sourceText = []
    
    if (csv_results && csv_results.length > 0) {
      sourceText.push(`template_fields.csv (${csv_results.length} entries)`)
    }
    
    if (pdf_results && pdf_results.length > 0) {
      // Extract unique source files from PDF results
      const uniqueSources = [...new Set(pdf_results.map(r => r.source).filter(Boolean))]
      if (uniqueSources.length > 0) {
        sourceText.push(`${uniqueSources.join(', ')} (${pdf_results.length} sections)`)
      } else {
        sourceText.push(`PDF documents (${pdf_results.length} sections)`)
      }
    }
    
    return sourceText.length > 0 ? sourceText.join(' + ') : 'No sources'
  }

  const getToolIcon = (tool) => {
    switch (tool) {
      case 'csv': return '📊'
      case 'pdf': return '📄'
      case 'clarification': return '❓'
      default: return '🔧'
    }
  }

  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case 'high': return '#27ae60'
      case 'medium': return '#f39c12'
      case 'low': return '#e74c3c'
      default: return '#95a5a6'
    }
  }

  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1>🎖️ Military RAG Agent System</h1>
          <p>Intelligent document generation and military knowledge assistant</p>
          
          {/* System Status Indicator */}
          {systemStatus && (
            <div className={`status-indicator ${systemStatus.status}`}>
              <span className="status-dot"></span>
              {systemStatus.status === 'healthy' ? 'System Ready' : 'System Issues'}
            </div>
          )}
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'query' ? 'active' : ''}`}
          onClick={() => setActiveTab('query')}
        >
          💬 Ask Question
        </button>
        <button 
          className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          🕒 History ({history.length})
        </button>
      </nav>

      <main className="main-content">
        {/* Query Tab */}
        {activeTab === 'query' && (
          <section className="query-section">
            <div className="section-header">
              <h2>Submit Your Query</h2>
              <p>Ask about military procedures or request document generation</p>
            </div>
            
            <div className="query-form">
              <div className="input-group">
                <div className="textarea-container">
                  <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Enter your question here..."
                    className="query-input"
                    rows={4}
                    disabled={loading}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && e.ctrlKey && !loading && query.trim()) {
                        handleSubmit(e)
                      }
                    }}
                  />
                  <div className="character-count">
                    {query.length} characters
                  </div>
                </div>
                
                <div className="button-group">
                  <button 
                    onClick={handleSubmit}
                    disabled={loading || !query.trim()}
                    className="submit-button primary"
                  >
                    {loading ? (
                      <>
                        <span className="loading-spinner"></span>
                        Processing...
                      </>
                    ) : (
                      <>
                        🚀 Submit Query
                      </>
                    )}
                  </button>
                  
                  {query && (
                    <button 
                      onClick={() => setQuery('')}
                      className="submit-button secondary"
                      disabled={loading}
                    >
                      Clear
                    </button>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}

        {/* History Tab */}
        {activeTab === 'history' && (
          <section className="history-section">
            <div className="section-header">
              <h2>Query History</h2>
              <p>Your recent interactions with the system</p>
              {history.length > 0 && (
                <button 
                  onClick={() => setHistory([])}
                  className="clear-history-btn"
                >
                  Clear History
                </button>
              )}
            </div>
            
            {history.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon">📝</div>
                <p>No queries yet. Submit your first question to get started!</p>
              </div>
            ) : (
              <div className="history-list">
                {history.map((entry) => (
                  <div key={entry.id} className="history-item">
                    <div className="history-header">
                      <div className="history-question">
                        <strong>Q:</strong> {entry.question}
                      </div>
                      <div className="history-meta">
                        <span className="timestamp">{entry.timestamp}</span>
                        <span className="tool-badge">
                          {getToolIcon(entry.response.tool_used)} {entry.response.tool_used}
                        </span>
                      </div>
                    </div>
                    <div className="history-answer">
                      <strong>A:</strong> {entry.response.answer.substring(0, 300)}
                      {entry.response.answer.length > 300 ? '...' : ''}
                    </div>
                    <button 
                      onClick={() => {
                        setQuery(entry.question);
                        setActiveTab('query');
                        handleSubmit(new Event('submit'));
                      }}
                      className="retry-btn"
                    >
                      🔄 Ask Again
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {/* Error Display */}
        {error && (
          <div className="error-message">
            <div className="error-icon">⚠️</div>
            <div>
              <strong>Error:</strong> {error}
              <button onClick={() => setError('')} className="dismiss-error">×</button>
            </div>
          </div>
        )}

        {/* Response Display */}
        {response && (
          <section className="response-section">
            <div className="response-card">
              <div className="response-header">
                <h3>
                  {getToolIcon(response.tool_used)} Response
                </h3>
                <div className="response-meta">
                  <span className="tool-used">
                    Tool: {response.tool_used}
                  </span>
                  <span 
                    className="confidence"
                    style={{ backgroundColor: getConfidenceColor(response.confidence) }}
                  >
                    {response.confidence} confidence
                  </span>
                </div>
              </div>
              
              <div className="response-content">
                <div className="answer">
                  {response.answer}
                </div>
                
                <div className="response-footer">
                  <div className="sources-summary">
                    <strong>Sources Used:</strong> {formatSources(response.sources)}
                    {response.sources && (response.sources.csv_results?.length > 0 || response.sources.pdf_results?.length > 0) && (
                      <button 
                        onClick={() => setShowSources(!showSources)}
                        className="toggle-sources-btn"
                      >
                        {showSources ? 'Hide' : 'Show'} Details
                      </button>
                    )}
                  </div>
                  
                  {showSources && response.sources && (
                    <div className="sources-detail">
                      {response.sources.csv_results?.length > 0 && (
                        <div className="source-group">
                          <h5>📊 template_fields.csv:</h5>
                          <ul>
                            {response.sources.csv_results.map((source, idx) => (
                              <li key={idx}>
                                <strong>{source.template_name}</strong> - {source.field_label}
                                {source.relevance_score && (
                                  <span className="relevance-score"> (Relevance: {(source.relevance_score * 100).toFixed(0)}%)</span>
                                )}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {response.sources.pdf_results?.length > 0 && (
                        <div className="source-group">
                          <h5>📄 PDF Documents:</h5>
                          <ul>
                            {response.sources.pdf_results.map((source, idx) => (
                              <li key={idx}>
                                <strong>{source.source || 'ARN42404-FM_5-0-000-WEB-1.pdf'}</strong> - Page {source.page}
                                {source.relevance_score && (
                                  <span className="relevance-score"> (Relevance: {(source.relevance_score * 100).toFixed(0)}%)</span>
                                )}
                                {source.military_terms_matched?.length > 0 && (
                                  <div className="military-terms">
                                    Military terms: {source.military_terms_matched.join(', ')}
                                  </div>
                                )}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {response.classification && (
                    <div className="classification-info">
                      <strong>Reasoning:</strong> {response.classification.reasoning}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>💡 Tip: Use specific military terms for better results. The system understands MDMP, ACFT, DA forms, and more.</p>
      </footer>
    </div>
  )
}

export default App