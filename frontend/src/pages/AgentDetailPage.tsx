import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api/client'

interface Agent {
  id: string
  name: string
  description: string
  category: string
  tags: string[]
  version: string
  targets: string[]
  content: string
  created_at: string
  updated_at: string
}

export function AgentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [agent, setAgent] = useState<Agent | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [installing, setInstalling] = useState(false)
  const [installResult, setInstallResult] = useState<{ success: boolean; message: string } | null>(null)

  useEffect(() => {
    if (id) fetchAgent()
  }, [id])

  const fetchAgent = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await api.get<Agent>(`/api/v1/agents/${id}`)
      setAgent(response.data)
    } catch (err) {
      setError('Failed to load agent')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleInstall = async (target: string) => {
    if (!agent) return
    setInstalling(true)
    setInstallResult(null)
    try {
      const response = await api.post('/api/v1/install', {
        agent_id: agent.id,
        target,
      })
      setInstallResult({ success: true, message: `Successfully installed to ${target}` })
    } catch (err: any) {
      setInstallResult({ success: false, message: err.response?.data?.detail || 'Installation failed' })
    } finally {
      setInstalling(false)
    }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '300px' }}>
        <div className="spinner" role="status" aria-label="Loading agent..." />
      </div>
    )
  }

  if (error || !agent) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <h2 style={{ marginBottom: '0.5rem' }}>Agent not found</h2>
        <p style={{ color: 'var(--color-text-muted)' }}>{error || 'Unknown error'}</p>
        <Link to="/" className="btn btn-primary" style={{ marginTop: '1rem', display: 'inline-block' }}>
          Back to Agents
        </Link>
      </div>
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <Link to="/" className="btn btn-outline" style={{ marginBottom: '0.5rem', display: 'inline-block' }}>
            ← Back to Agents
          </Link>
          <h1 style={{ fontSize: '2rem', fontWeight: 700 }}>{agent.name}</h1>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
            <span className="badge badge-primary">{agent.category}</span>
            <span className="badge badge-secondary">v{agent.version}</span>
            {agent.tags.map(tag => (
              <span key={tag} className="badge badge-secondary" style={{ backgroundColor: 'var(--color-background)', color: 'var(--color-text)' }}>
                {tag}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '1.5rem' }}>
        <div>
          <div className="card">
            <div className="card-header">
              <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>Description</h2>
            </div>
            <div className="card-body">
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{agent.description}</div>
            </div>
          </div>

          <div className="card" style={{ marginTop: '1.5rem' }}>
            <div className="card-header">
              <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>Agent Content</h2>
            </div>
            <div className="card-body">
              <pre style={{ 
                backgroundColor: 'var(--color-background)', 
                padding: '1rem', 
                borderRadius: 'var(--radius-md)', 
                overflow: 'auto',
                fontSize: '0.8125rem',
                lineHeight: 1.6,
                maxHeight: '400px',
                fontFamily: 'var(--font-mono)'
              }}>
                {agent.content}
              </pre>
            </div>
          </div>
        </div>

        <div>
          <div className="card" style={{ position: 'sticky', top: '80px' }}>
            <div className="card-header">
              <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>Install Agent</h2>
            </div>
            <div className="card-body">
              <p style={{ color: 'var(--color-text-muted)', marginBottom: '1rem', fontSize: '0.875rem' }}>
                Choose a target to install this agent:
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {agent.targets.map(target => (
                  <button
                    key={target}
                    onClick={() => handleInstall(target)}
                    disabled={installing}
                    className="btn btn-primary"
                    style={{ justifyContent: 'flex-start' }}
                  >
                    {installing ? (
                      <>
                        <div className="spinner" style={{ width: '1rem', height: '1rem' }} />
                        Installing to {target}...
                      </>
                    ) : (
                      `Install to ${target}`
                    )}
                  </button>
                ))}
              </div>

              {installResult && (
                <div className={`alert ${installResult.success ? 'alert-success' : 'alert-error'}`} style={{ marginTop: '1rem' }} role="alert">
                  {installResult.message}
                </div>
              )}

              <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--color-border)' }}>
                <h3 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '0.5rem' }}>
                  Supported Targets
                </h3>
                <ul style={{ fontSize: '0.875rem', color: 'var(--color-text)', lineHeight: 2 }}>
                  <li>Claude Code</li>
                  <li>Cursor</li>
                  <li>Aider</li>
                  <li>Qwen Code</li>
                  <li>ZCode</li>
                </ul>
              </div>

              <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--color-border)' }}>
                <h3 style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '0.5rem' }}>
                  Installation Instructions
                </h3>
                <pre style={{ 
                  backgroundColor: 'var(--color-background)', 
                  padding: '1rem', 
                  borderRadius: 'var(--radius-md)', 
                  overflow: 'auto',
                  fontSize: '0.8125rem',
                  lineHeight: 1.6,
                  fontFamily: 'var(--font-mono)'
                }}>
                  {`# Install to {target}
prism-engine install --agent {agent.id} --target {target}

# Or via the web UI
# Click the install button above for automatic installation

# For manual installation, copy the agent content to:
# - Claude Code: ~/.claude/agents/{agent.id}.md
# - Cursor: .cursor/rules/{agent.id}.mdc
# - Aider: .aider/agents/{agent.id}.md
# - Qwen Code: ~/.qwen/agents/{agent.id}.md
# - ZCode: ~/.zcode/agents/{agent.id}.md
                  `}
                </pre>
              </div>
            </div>
          </div>

          <div className="card" style={{ marginTop: '1rem', position: 'sticky', top: '80px' }}>
            <div className="card-header">
              <h2 style={{ fontSize: '1.125rem', fontWeight: 600 }}>Metadata</h2>
            </div>
            <div className="card-body">
              <dl style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '0.5rem 1rem', fontSize: '0.875rem' }}>
                <dt style={{ color: 'var(--color-text-muted)' }}>Created</dt>
                <dd>{new Date(agent.created_at).toLocaleDateString()}</dd>
                <dt style={{ color: 'var(--color-text-muted)' }}>Updated</dt>
                <dd>{new Date(agent.updated_at).toLocaleDateString()}</dd>
                <dt style={{ color: 'var(--color-text-muted)' }}>ID</dt>
                <dd style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8125rem' }}>{agent.id}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}