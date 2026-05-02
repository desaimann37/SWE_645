import { useState, useEffect, useRef } from 'react'
import axios from 'axios'

const AGENT_URL = import.meta.env.VITE_AGENT_URL || 'http://localhost:9000'

function generateSessionId() {
  return 'sess-' + Math.random().toString(36).slice(2) + Date.now().toString(36)
}

const SAMPLE_PROMPTS = [
  'Create a survey for Jane Smith. She liked atmosphere and sports. She heard about the university from friends.',
  'Show all surveys where students liked dorm rooms.',
  'Update John Doe\'s recommendation to Likely.',
  'Delete John Doe\'s survey.',
  'Show me all surveys.',
  'List students who liked campus atmosphere.',
  'How many students are unlikely to recommend the school?',
  'Change survey 102 interest source to Internet.',
]

export default function AISurveyAssistant() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI Survey Assistant. You can ask me to create, find, update, or delete student surveys using plain English. How can I help you today?',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [sessionId] = useState(generateSessionId)
  const [actionLog, setActionLog] = useState([])
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text) => {
    const userText = (text || input).trim()
    if (!userText) return

    setMessages(prev => [...prev, { role: 'user', content: userText }])
    setInput('')
    setLoading(true)

    try {
      const res = await axios.post(`${AGENT_URL}/agent/query`, {
        session_id: sessionId,
        message: userText,
      })
      const reply = res.data.reply || 'No response from agent.'
      setMessages(prev => [...prev, { role: 'assistant', content: reply }])

      // Track actions in the log
      const lower = reply.toLowerCase()
      if (lower.includes('created') || lower.includes('successfully created')) {
        setActionLog(prev => [`Created a survey`, ...prev].slice(0, 10))
      } else if (lower.includes('deleted') || lower.includes('successfully deleted')) {
        setActionLog(prev => [`Deleted a survey`, ...prev].slice(0, 10))
      } else if (lower.includes('updated') || lower.includes('successfully updated')) {
        setActionLog(prev => [`Updated a survey`, ...prev].slice(0, 10))
      } else if (lower.includes('found') || lower.includes('survey') && lower.includes('result')) {
        setActionLog(prev => [`Queried surveys`, ...prev].slice(0, 10))
      }
    } catch {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I could not reach the AI agent. Please make sure the agent service is running.' },
      ])
    }
    setLoading(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const styles = {
    page: {
      display: 'flex',
      flexDirection: 'column',
      height: 'calc(100vh - 56px)',
      background: '#f4f6fb',
    },
    header: {
      background: '#003366',
      color: 'white',
      padding: '12px 24px',
      fontSize: '16px',
      fontWeight: 'bold',
      letterSpacing: '0.5px',
    },
    body: {
      display: 'flex',
      flex: 1,
      overflow: 'hidden',
    },
    leftPanel: {
      width: '280px',
      minWidth: '240px',
      background: '#fff',
      borderRight: '1px solid #dde3ef',
      padding: '20px 16px',
      overflowY: 'auto',
      display: 'flex',
      flexDirection: 'column',
      gap: '20px',
    },
    sectionTitle: {
      fontWeight: 'bold',
      color: '#003366',
      fontSize: '13px',
      marginBottom: '6px',
      textTransform: 'uppercase',
      letterSpacing: '0.5px',
    },
    bullet: {
      fontSize: '13px',
      color: '#444',
      marginBottom: '4px',
      paddingLeft: '4px',
    },
    promptChip: {
      display: 'block',
      width: '100%',
      textAlign: 'left',
      background: '#eef2ff',
      border: '1px solid #c7d2fe',
      borderRadius: '6px',
      padding: '7px 10px',
      fontSize: '12px',
      color: '#1e3a8a',
      cursor: 'pointer',
      marginBottom: '6px',
      lineHeight: '1.4',
    },
    mainChat: {
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
    },
    chatMessages: {
      flex: 1,
      overflowY: 'auto',
      padding: '20px 24px',
      display: 'flex',
      flexDirection: 'column',
      gap: '12px',
    },
    messageRow: (role) => ({
      display: 'flex',
      justifyContent: role === 'user' ? 'flex-end' : 'flex-start',
    }),
    bubble: (role) => ({
      maxWidth: '70%',
      padding: '10px 14px',
      borderRadius: role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
      background: role === 'user' ? '#003366' : '#fff',
      color: role === 'user' ? 'white' : '#222',
      fontSize: '14px',
      lineHeight: '1.5',
      boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
      whiteSpace: 'pre-wrap',
      border: role === 'assistant' ? '1px solid #e5e7eb' : 'none',
    }),
    label: (role) => ({
      fontSize: '11px',
      color: '#888',
      marginBottom: '3px',
      textAlign: role === 'user' ? 'right' : 'left',
    }),
    typingBubble: {
      padding: '10px 16px',
      borderRadius: '16px 16px 16px 4px',
      background: '#fff',
      border: '1px solid #e5e7eb',
      color: '#888',
      fontSize: '14px',
      display: 'inline-block',
    },
    inputArea: {
      borderTop: '1px solid #dde3ef',
      padding: '12px 20px',
      background: '#fff',
      display: 'flex',
      gap: '10px',
      alignItems: 'flex-end',
    },
    textarea: {
      flex: 1,
      resize: 'none',
      padding: '10px 14px',
      fontSize: '14px',
      border: '1px solid #cbd5e1',
      borderRadius: '8px',
      outline: 'none',
      fontFamily: 'inherit',
      lineHeight: '1.5',
      maxHeight: '100px',
    },
    sendBtn: {
      background: '#003366',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      padding: '10px 20px',
      fontSize: '14px',
      cursor: 'pointer',
      fontWeight: 'bold',
      whiteSpace: 'nowrap',
    },
    sendBtnDisabled: {
      background: '#94a3b8',
      cursor: 'not-allowed',
    },
    rightPanel: {
      width: '200px',
      minWidth: '160px',
      background: '#fff',
      borderLeft: '1px solid #dde3ef',
      padding: '16px 12px',
      overflowY: 'auto',
    },
    logItem: {
      fontSize: '12px',
      color: '#555',
      padding: '5px 0',
      borderBottom: '1px solid #f0f0f0',
    },
  }

  return (
    <div style={styles.page}>
      <div style={styles.header}>Student Survey AI Assistant</div>
      <div style={styles.body}>
        {/* Left Panel */}
        <div style={styles.leftPanel}>
          <div>
            <div style={styles.sectionTitle}>AI Survey Assistant</div>
            <div style={{ fontSize: '12px', color: '#666', marginBottom: '10px' }}>
              Use natural language to manage student surveys.
            </div>
            <div style={styles.sectionTitle}>What you can do</div>
            {['Create a new survey', 'Search surveys', 'Update survey records', 'Delete survey records'].map(item => (
              <div key={item} style={styles.bullet}>• {item}</div>
            ))}
          </div>

          <div>
            <div style={styles.sectionTitle}>To create a survey, include</div>
            {[
              'Full name (first & last)',
              'Address (street, city, state, zip)',
              'Phone number',
              'Email address',
              'Survey date',
              'What the student liked most',
              'Interest source (Friends, Internet, Television, Other)',
              'Recommendation likelihood',
            ].map(f => (
              <div key={f} style={styles.bullet}>• {f}</div>
            ))}
          </div>

          <div>
            <div style={styles.sectionTitle}>Example prompts</div>
            {SAMPLE_PROMPTS.map((p, i) => (
              <button
                key={i}
                style={styles.promptChip}
                onClick={() => sendMessage(p)}
                disabled={loading}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Main Chat Panel */}
        <div style={styles.mainChat}>
          <div style={styles.chatMessages}>
            {messages.map((msg, i) => (
              <div key={i}>
                <div style={styles.label(msg.role)}>
                  {msg.role === 'user' ? 'You' : 'Agent'}
                </div>
                <div style={styles.messageRow(msg.role)}>
                  <div style={styles.bubble(msg.role)}>
                    {msg.content}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div>
                <div style={styles.label('assistant')}>Agent</div>
                <div style={styles.messageRow('assistant')}>
                  <div style={styles.typingBubble}>Thinking...</div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div style={styles.inputArea}>
            <textarea
              rows={2}
              style={styles.textarea}
              placeholder="Type your request here... (Enter to send, Shift+Enter for new line)"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button
              style={{ ...styles.sendBtn, ...(loading || !input.trim() ? styles.sendBtnDisabled : {}) }}
              onClick={() => sendMessage()}
              disabled={loading || !input.trim()}
            >
              Send
            </button>
          </div>
        </div>

        {/* Right Panel — Recent AI Actions */}
        <div style={styles.rightPanel}>
          <div style={styles.sectionTitle}>Recent AI Actions</div>
          {actionLog.length === 0 ? (
            <div style={{ fontSize: '12px', color: '#aaa' }}>No actions yet.</div>
          ) : (
            actionLog.map((entry, i) => (
              <div key={i} style={styles.logItem}>• {entry}</div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
