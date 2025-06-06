import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE_URL = 'http://localhost:8000'

// Example queries from the PDF requirements
const EXAMPLE_QUERIES = [
  {
    category: "Award Generation (Example 1)",
    query: "Write an award bullet for a Soldier that got a 600 on their ACFT",
    expectedTool: "csv + pdf (hybrid)",
    description: "Should find ACFT context from PDF and award template from CSV",
    icon: "🏆"
  },
  {
    category: "Information Retrieval (Example 2)", 
    query: "What is the role of the S6 during MDMP?",
    expectedTool: "pdf",
    description: "Should search PDF for MDMP procedures and S6 roles",
    icon: "📋"
  },
  {
    category: "Hybrid Generation (Example 3)",
    query: "Write a situation paragraph for my infantry battalion's upcoming mission at NTC",
    expectedTool: "csv + pdf (hybrid)",
    description: "Should use CSV for paragraph structure and PDF for military context",
    icon: "🎯"
  },
  {
    category: "Template-Focused Generation",
    query: "Create a character assessment for an NCO evaluation",
    expectedTool: "csv",
    description: "Should focus on evaluation report templates",
    icon: "📝"
  },
  {
    category: "Knowledge-Focused Query",
    query: "Explain the steps of the military decision making process",
    expectedTool: "pdf",
    description: "Should provide detailed MDMP information from manuals",
    icon: "🔍"
  }
]

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

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery)
    setActiveTab('query')
    // Auto-scroll to query section
    document.querySelector('.query-section')?.scrollIntoView({ behavior: 'smooth' })
  }

  const formatSources = (sources) => {
    const { csv_results = [], pdf_results = [] } = sources || {}
    let sourceText = []
    
    if (csv_results && csv_results.length > 0) {
      sourceText.push(`${csv_results.length} template(s)`)
    }
    
    if (pdf_results && pdf_results.length > 0) {
      sourceText.push(`${pdf_results.length} document section(s)`)
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
          className={`tab-button ${activeTab === 'examples' ? 'active' : ''}`}
          onClick={() => setActiveTab('examples')}
        >
          📚 Examples
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
                    placeholder="Examples:&#10;• Write an award bullet for a Soldier that got a 600 on their ACFT&#10;• What is the role of the S6 during MDMP?&#10;• Explain the steps of the military decision making process"
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

            {/* Quick Examples */}
            <div className="quick-examples">
              <h4>Quick Start:</h4>
              <div className="quick-example-buttons">
                <button 
                  onClick={() => handleExampleClick("Write an award bullet for a Soldier that got a 600 on their ACFT")}
                  className="quick-example-btn"
                >
                  🏆 Award Bullet
                </button>
                <button 
                  onClick={() => handleExampleClick("What is the role of the S6 during MDMP?")}
                  className="quick-example-btn"
                >
                  📋 S6 Role
                </button>
                <button 
                  onClick={() => handleExampleClick("Explain the steps of MDMP")}
                  className="quick-example-btn"
                >
                  🔍 MDMP Steps
                </button>
              </div>
            </div>
          </section>
        )}

        {/* Examples Tab */}
        {activeTab === 'examples' && (
          <section className="examples-section">
            <div className="section-header">
              <h2>Example Queries</h2>
              <p>Click on any example to try it out</p>
            </div>
            
            <div className="examples-grid">
              {EXAMPLE_QUERIES.map((example, index) => (
                <div 
                  key={index}
                  className="example-card"
                  onClick={() => handleExampleClick(example.query)}
                >
                  <div className="example-icon">{example.icon}</div>
                  <div className="example-content">
                    <div className="example-category">{example.category}</div>
                    <div className="example-query">"{example.query}"</div>
                    <div className="example-tool">Expected: {example.expectedTool}</div>
                    <div className="example-description">{example.description}</div>
                  </div>
                </div>
              ))}
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
                      onClick={() => handleExampleClick(entry.question)}
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
                          <h5>📊 CSV Templates:</h5>
                          <ul>
                            {response.sources.csv_results.map((source, idx) => (
                              <li key={idx}>
                                {source.template_name} - {source.field_label}
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
                                Page {source.page} - {source.source}
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