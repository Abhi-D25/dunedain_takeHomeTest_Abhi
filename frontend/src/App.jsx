import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [examples, setExamples] = useState([])
  const [history, setHistory] = useState([])

  // Fetch example queries on component mount
  useEffect(() => {
    fetchExamples()
  }, [])

  const fetchExamples = async () => {
    try {
      const result = await axios.get(`${API_BASE_URL}/api/examples`)
      setExamples(result.data.examples)
    } catch (err) {
      console.error('Failed to fetch examples:', err)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setResponse(null)

    try {
      const result = await axios.post(`${API_BASE_URL}/api/query`, {
        question: query,
        session_id: 'demo-session'
      })

      setResponse(result.data)
      
      // Add to history
      const newEntry = {
        id: Date.now(),
        question: query,
        response: result.data,
        timestamp: new Date().toLocaleTimeString()
      }
      setHistory(prev => [newEntry, ...prev])
      
      setQuery('') // Clear the input
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while processing your query')
      console.error('Query error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery)
  }

  const formatSources = (sources) => {
    const { csv_results, pdf_results } = sources
    let sourceText = []
    
    if (csv_results && csv_results.length > 0) {
      sourceText.push(`CSV Sources: ${csv_results.length} template(s) found`)
    }
    
    if (pdf_results && pdf_results.length > 0) {
      sourceText.push(`PDF Sources: ${pdf_results.length} document section(s) found`)
    }
    
    return sourceText.length > 0 ? sourceText.join(', ') : 'No sources used'
  }

  return (
    <div className="App">
      <header className="app-header">
        <h1>🎖️ Military RAG Agent System</h1>
        <p>Ask questions about military procedures or request document generation</p>
      </header>

      <main className="main-content">
        {/* Query Input Section */}
        <section className="query-section">
          <form onSubmit={handleSubmit} className="query-form">
            <div className="input-group">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question or request document generation..."
                className="query-input"
                rows={3}
                disabled={loading}
              />
              <button 
                type="submit" 
                disabled={loading || !query.trim()}
                className="submit-button"
              >
                {loading ? 'Processing...' : 'Submit'}
              </button>
            </div>
          </form>

          {/* Example Queries */}
          {examples.length > 0 && (
            <div className="examples-section">
              <h3>Example Queries:</h3>
              <div className="examples-grid">
                {examples.map((example, index) => (
                  <div key={index} className="example-card">
                    <div className="example-category">{example.category}</div>
                    <div 
                      className="example-query"
                      onClick={() => handleExampleClick(example.query)}
                    >
                      "{example.query}"
                    </div>
                    <div className="example-tool">Expected tool: {example.expected_tool}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        {/* Error Display */}
        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* Loading Indicator */}
        {loading && (
          <div className="loading-indicator">
            <div className="spinner"></div>
            <p>Processing your query...</p>
          </div>
        )}

        {/* Response Display */}
        {response && (
          <section className="response-section">
            <div className="response-card">
              <div className="response-header">
                <h3>Response</h3>
                <div className="response-meta">
                  <span className="tool-used">Tool: {response.tool_used}</span>
                  <span className="confidence">Confidence: {response.confidence}</span>
                </div>
              </div>
              
              <div className="response-content">
                <div className="answer">
                  {response.answer}
                </div>
                
                <div className="sources-info">
                  <strong>Sources:</strong> {formatSources(response.sources)}
                </div>
                
                {response.classification && (
                  <div className="classification-info">
                    <strong>Reasoning:</strong> {response.classification.reasoning}
                  </div>
                )}
              </div>
            </div>
          </section>
        )}

        {/* Chat History */}
        {history.length > 0 && (
          <section className="history-section">
            <h3>Query History</h3>
            <div className="history-list">
              {history.slice(0, 5).map((entry) => (
                <div key={entry.id} className="history-item">
                  <div className="history-question">
                    <strong>Q:</strong> {entry.question}
                  </div>
                  <div className="history-answer">
                    <strong>A:</strong> {entry.response.answer.substring(0, 200)}
                    {entry.response.answer.length > 200 ? '...' : ''}
                  </div>
                  <div className="history-meta">
                    {entry.timestamp} | Tool: {entry.response.tool_used}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

export default App