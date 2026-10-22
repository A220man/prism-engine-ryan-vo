import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export function LoginPage() {
  const { login, demoLogin } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState('')

  const handleLogin = async () => {
    setError('')
    try {
      await login()
    } catch (err) {
      setError('Login failed. Please try again.')
    }
  }

  const handleDemoLogin = async () => {
    setError('')
    try {
      await demoLogin()
      navigate('/')
    } catch (err) {
      setError('Demo login failed. Is demo mode enabled?')
    }
  }

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto', padding: '2rem' }}>
      <div className="card">
        <div className="card-header" style={{ textAlign: 'center' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Welcome to Prism Engine</h1>
          <p style={{ color: 'var(--color-text-muted)', marginTop: '0.5rem' }}>
            AI Agent Management Platform
          </p>
        </div>
        <div className="card-body">
          <div style={{ marginBottom: '1.5rem', padding: '1rem', backgroundColor: 'var(--color-background)', borderRadius: 'var(--radius-md)', fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
            <strong>Demo Mode:</strong> Click "Demo Login" to explore without Keycloak setup.
            Requires backend DEMO_MODE=true.
          </div>

          <div style={{ marginTop: '1.5rem', padding: '1rem', backgroundColor: 'var(--color-primary)', borderRadius: 'var(--radius-md)', color: 'white' }}>
            <h3 style={{ marginBottom: '0.5rem', fontSize: '0.875rem' }}>About Prism Engine</h3>
            <p style={{ fontSize: '0.8125rem', lineHeight: 1.6 }}>
              Prism Engine is an AI agent management platform that provides a unified interface for discovering,
              installing, and managing specialized AI agents across multiple development tools including
              Claude Code, Cursor, Aider, Qwen Code, and ZCode.
            </p>
            <p style={{ fontSize: '0.8125rem', lineHeight: 1.6, marginTop: '0.5rem' }}>
              Features: Agent registry with search and filtering, multi-target installation with automatic
              format conversion, Qwen/ZCode template sanitization, parallel installation with diagnostics,
              OIDC authentication with Keycloak and SAML broker support.
            </p>
          </div>
          
          {error && (
            <div className="alert alert-error" style={{ marginBottom: '1rem' }} role="alert">
              {error}
            </div>
          )}

          <button onClick={handleLogin} className="btn btn-primary" style={{ width: '100%', marginBottom: '0.75rem' }}>
            Login with Keycloak
          </button>
          
          <button onClick={handleDemoLogin} className="btn btn-secondary" style={{ width: '100%' }}>
            Demo Login
          </button>
        </div>
      </div>
    </div>
  )
}