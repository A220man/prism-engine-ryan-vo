import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

export function Layout() {
  const { user, logout } = useAuth()
  const location = useLocation()

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{
        backgroundColor: 'var(--color-surface)',
        borderBottom: '1px solid var(--color-border)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '64px' }}>
          <Link to="/" style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-primary)' }}>
            Prism Engine
          </Link>
          <nav style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <Link to="/" style={{ color: location.pathname === '/' ? 'var(--color-primary)' : 'var(--color-text)', fontWeight: 500 }}>
              Agents
            </Link>
            {user && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <span style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                  {user.email}
                </span>
                <span className="badge badge-primary" style={{ textTransform: 'capitalize' }}>
                  {user.roles[0] || 'viewer'}
                </span>
                <button onClick={logout} className="btn btn-outline" style={{ padding: '0.375rem 0.875rem' }}>
                  Logout
                </button>
              </div>
            )}
          </nav>
        </div>
      </header>
      <main style={{ flex: 1, padding: '2rem 0' }}>
        <div className="container">
          <Outlet />
        </div>
      </main>
      <footer style={{ backgroundColor: 'var(--color-surface)', borderTop: '1px solid var(--color-border)', padding: '1.5rem 0', marginTop: 'auto' }}>
        <div className="container" style={{ textAlign: 'center', color: 'var(--color-text-muted)', fontSize: '0.875rem' }}>
          Prism Engine &copy; 2026 Ryan Vo &mdash; MIT License
        </div>
      </footer>
    </div>
  )
}