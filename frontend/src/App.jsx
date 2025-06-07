import { useState, useEffect, useRef } from 'react'
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
  const [isTyping, setIsTyping] = useState(false)
  const textareaRef = useRef(null)
  const responseRef = useRef(null)

  // Check system status on load with enhanced feedback
  useEffect(() => {
    checkSystemHealth()
    const interval = setInterval(checkSystemHealth, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px'
    }
  }, [query])

  // Scroll to response when it appears
  useEffect(() => {
    if (response && responseRef.current) {
      setTimeout(() => {
        responseRef.current.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start',
          inline: 'nearest'
        })
      }, 100)
    }
  }, [response])

  // Typing indicator effect
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsTyping(query.length > 0)
    }, 150)
    return () => clearTimeout(timer)
  }, [query])

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
      
      // Add to history with enhanced metadata
      const newEntry = {
        id: Date.now(),
        question: query,
        response: data,
        timestamp: new Date().toLocaleTimeString(),
        date: new Date().toLocaleDateString()
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

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery)
    setActiveTab('query')
    // Add a small delay for better UX
    setTimeout(() => {
      if (textareaRef.current) {
        textareaRef.current.focus()
      }
    }, 200)
  }

  const retryQuery = async (questionToRetry) => {
    setQuery(questionToRetry)
    setActiveTab('query')
    
    // Simulate form submission
    const fakeEvent = { preventDefault: () => {} }
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
          question: questionToRetry,
          session_id: sessionId
        })
      })

      if (!result.ok) {
        const errorData = await result.json()
        throw new Error(errorData.detail || 'Request failed')
      }

      const data = await result.json()
      setResponse(data)
      
    } catch (err) {
      setError(err.message || 'An error occurred while processing your query')
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

  const getConfidenceColor = (tool) => {
    switch (tool) {
      case 'csv': return '#10b981'
      case 'pdf': return '#3b82f6'
      case 'clarification': return '#f59e0b'
      default: return '#6b7280'
    }
  }

  return (
    <div className="App">
      {/* Enhanced Header with Particles */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-particles"></div>
          <h1 className="header-title">
            <span className="title-icon">🎖️</span>
            <span className="title-text">Military RAG Agent</span>
          </h1>
          <p className="header-subtitle">
            Intelligent document generation and military knowledge assistant
          </p>
          
          {/* Enhanced System Status */}
          {systemStatus && (
            <div className={`status-indicator ${systemStatus.status}`}>
              <div className="status-dot"></div>
              <span className="status-text">
                {systemStatus.status === 'healthy' ? 'System Ready' : 'System Issues'}
              </span>
              {systemStatus.status === 'healthy' && (
                <div className="status-wave"></div>
              )}
            </div>
          )}
        </div>
      </header>

      {/* Enhanced Navigation */}
      <nav className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'query' ? 'active' : ''}`}
          onClick={() => setActiveTab('query')}
        >
          <span className="tab-icon">💬</span>
          <span className="tab-text">Ask Question</span>
          {isTyping && activeTab !== 'query' && <div className="typing-indicator"></div>}
        </button>
        <button 
          className={`tab-button ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <span className="tab-icon">🕒</span>
          <span className="tab-text">History</span>
          {history.length > 0 && (
            <span className="history-count">{history.length}</span>
          )}
        </button>
      </nav>

      <main className="main-content">
        {/* Enhanced Query Tab */}
        {activeTab === 'query' && (
          <section className="query-section slide-in">
            <div className="section-header">
              <h2>Submit Your Query</h2>
              <p>Ask about military procedures or request document generation</p>
            </div>
            
            <div className="query-form">
              <div className="input-group">
                <div className="textarea-container">
                  <textarea
                    ref={textareaRef}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Enter your question here (Ctrl+Enter to submit)"
                    className={`query-input ${isTyping ? 'typing' : ''}`}
                    rows={3}
                    disabled={loading}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && e.ctrlKey && !loading && query.trim()) {
                        handleSubmit(e)
                      }
                    }}
                  />
                  <div className="input-effects">
                    <div className="character-count">
                      {query.length} characters
                    </div>
                    {isTyping && <div className="typing-pulse"></div>}
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
                        <div className="loading-spinner"></div>
                        <span>Processing...</span>
                      </>
                    ) : (
                      <>
                        <span className="button-icon">🚀</span>
                        <span>Submit Query</span>
                      </>
                    )}
                  </button>
                  
                  {query && (
                    <button 
                      onClick={() => setQuery('')}
                      className="submit-button secondary"
                      disabled={loading}
                    >
                      <span className="button-icon">🗑️</span>
                      <span>Clear</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}

        {/* Enhanced History Tab */}
        {activeTab === 'history' && (
          <section className="history-section slide-in">
            <div className="section-header">
              <h2>Query History</h2>
              <p>Your recent interactions with the system</p>
              {history.length > 0 && (
                <button 
                  onClick={() => setHistory([])}
                  className="clear-history-btn"
                >
                  <span className="button-icon">🗑️</span>
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
                {history.map((entry, index) => (
                  <div key={entry.id} className={`history-item fade-in-delay-${index % 3}`}>
                    <div className="history-header">
                      <div className="history-question">
                        <strong>Q:</strong> {entry.question}
                      </div>
                      <div className="history-meta">
                        <span className="timestamp">{entry.date} {entry.timestamp}</span>
                        <span className="tool-badge" style={{backgroundColor: getConfidenceColor(entry.response.tool_used)}}>
                          {getToolIcon(entry.response.tool_used)} {entry.response.tool_used}
                        </span>
                      </div>
                    </div>
                    <div className="history-answer">
                      <strong>A:</strong> {entry.response.answer.substring(0, 300)}
                      {entry.response.answer.length > 300 ? '...' : ''}
                    </div>
                    <button 
                      onClick={() => retryQuery(entry.question)}
                      className="retry-btn"
                      disabled={loading}
                    >
                      <span className="button-icon">🔄</span>
                      Ask Again
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}

        {/* Enhanced Error Display */}
        {error && (
          <div className="error-message shake">
            <div className="error-content">
              <div className="error-icon">⚠️</div>
              <div className="error-text">
                <strong>Error:</strong> {error}
              </div>
            </div>
            <button onClick={() => setError('')} className="dismiss-error">
              ×
            </button>
          </div>
        )}

        {/* Enhanced Response Display */}
        {response && (
          <section ref={responseRef} className="response-section slide-up">
            <div className="response-card">
              <div className="response-header">
                <h3 className="response-title">
                  <span className="response-icon">{getToolIcon(response.tool_used)}</span>
                  <span>Response</span>
                </h3>
                <div className="response-meta">
                  <span 
                    className="tool-used"
                    style={{backgroundColor: getConfidenceColor(response.tool_used)}}
                  >
                    Primary Tool: {response.tool_used}
                  </span>
                </div>
              </div>
              
              <div className="response-content">
                <div className="answer">
                  {response.answer}
                </div>
                
                <div className="response-footer">
                  <div className="sources-summary">
                    <div className="sources-info">
                      <strong>📚 Sources Used: (Top 5 for each)</strong> {formatSources(response.sources)}
                    </div>
                    {response.sources && (response.sources.csv_results?.length > 0 || response.sources.pdf_results?.length > 0) && (
                      <button 
                        onClick={() => setShowSources(!showSources)}
                        className="toggle-sources-btn"
                      >
                        <span>{showSources ? '👁️‍🗨️ Hide' : '👁️ Show'} Details</span>
                        <span className={`arrow ${showSources ? 'up' : 'down'}`}>▼</span>
                      </button>
                    )}
                  </div>
                  
                  {showSources && response.sources && (
                    <div className="sources-detail slide-down">
                      {response.sources.csv_results?.length > 0 && (
                        <div className="source-group">
                          <h5>📊 template_fields.csv:</h5>
                          <ul>
                            {response.sources.csv_results.map((source, idx) => (
                              <li key={idx} className="source-item">
                                <div className="source-content">
                                  <strong>{source.template_name}</strong> - {source.field_label}
                                  {source.relevance_score && (
                                    <span className="relevance-score">
                                      Relevance: {(source.relevance_score * 100).toFixed(0)}%
                                    </span>
                                  )}
                                </div>
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
                              <li key={idx} className="source-item">
                                <div className="source-content">
                                  <strong>{source.source || 'ARN42404-FM_5-0-000-WEB-1.pdf'}</strong> - Page {source.page}
                                  {source.relevance_score && (
                                    <span className="relevance-score">
                                      Relevance: {(source.relevance_score * 100).toFixed(0)}%
                                    </span>
                                  )}
                                  {source.military_terms_matched?.length > 0 && (
                                    <div className="military-terms">
                                      🎯 Military terms: {source.military_terms_matched.join(', ')}
                                    </div>
                                  )}
                                </div>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {response.classification && (
                    <div className="classification-info">
                      <strong>🧠 Reasoning:</strong> {response.classification.reasoning}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </section>
        )}
      </main>

      {/* Enhanced Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <p>💡 <strong>Pro Tip:</strong> Use specific military terms for better results. The system understands MDMP, ACFT, DA forms, and more.</p>
          <div className="footer-stats">
            Session ID: {sessionId.split('-')[1]} • Queries: {history.length}
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App