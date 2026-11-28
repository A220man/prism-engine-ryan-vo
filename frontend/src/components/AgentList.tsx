import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { buildAgentListParams, clampPage, totalPages } from '../api/agentQuery'

interface Agent {
  id: string
  name: string
  slug: string
  description: string | null
  version: string
  author: string | null
  tags: string[] | null
  created_at: string
  updated_at: string
}

interface AgentListResponse {
  items: Agent[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

interface AgentListProps {
  pageSize?: number
  initialPage?: number
}

export function AgentList({ pageSize = 10, initialPage = 1 }: AgentListProps) {
  const [agents, setAgents] = useState<Agent[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [tagInput, setTagInput] = useState('')
  const [tag, setTag] = useState('')
  const [page, setPage] = useState(initialPage)

  // Debounce free-text search into the `search` state that drives fetching.
  useEffect(() => {
    const id = setTimeout(() => {
      setSearch(searchInput)
      setPage(1)
    }, 250)
    return () => clearTimeout(id)
  }, [searchInput])

  const fetchAgents = useCallback(async (requestedPage: number) => {
    setLoading(true)
    setError(null)
    try {
      const params = buildAgentListParams({
        page: requestedPage,
        page_size: pageSize,
        search,
        tag,
      })
      const response = await api.get<AgentListResponse>('/api/v1/agents', { params })
      const data = response.data
      setAgents(data.items)
      setTotal(data.total)
      // Keep the visible page within range when filters shrink the result set.
      const clamped = clampPage(requestedPage, data.total, pageSize)
      if (clamped !== requestedPage) setPage(clamped)
    } catch (err) {
      setError('Failed to load agents')
      console.error(err)
      setAgents([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [search, tag, pageSize])

  useEffect(() => {
    fetchAgents(page)
  }, [fetchAgents, page])

  const lastPage = totalPages(total, pageSize)

  const applyTag = () => {
    setTag(tagInput.trim())
    setPage(1)
  }

  const clearFilters = () => {
    setSearchInput('')
    setSearch('')
    setTagInput('')
    setTag('')
    setPage(1)
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '300px' }}>
        <div className="spinner" role="status" aria-label="Loading agents..." />
      </div>
    )
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>Agents</h1>
          <p style={{ color: 'var(--color-text-muted)' }}>
            Discover and install AI agents for your development tools
            {total > 0 && `· ${total} total`}
          </p>
        </div>
      </div>

      {error && (
        <div className="alert alert-error" style={{ marginBottom: '1.5rem' }} role="alert">
          {error}
        </div>
      )}

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-body" style={{ padding: '1rem' }}>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'flex-end' }}>
            <div style={{ flex: 1, minWidth: '250px' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>Search agents</label>
              <input
                type="text"
                style={{
                  width: '100%', padding: '0.5rem', border: '1px solid var(--color-border)',
                  borderRadius: '4px', fontSize: '0.875rem',
                }}
                placeholder="Search by name, description..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                aria-label="Search agents"
              />
            </div>
            <div style={{ minWidth: '200px' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem' }}>Tag</label>
              <input
                type="text"
                style={{
                  width: '100%', padding: '0.5rem', border: '1px solid var(--color-border)',
                  borderRadius: '4px', fontSize: '0.875rem',
                }}
                placeholder="Filter by tag"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') applyTag() }}
                aria-label="Filter by tag"
              />
            </div>
            <button
              style={{
                padding: '0.5rem 1rem', fontSize: '0.875rem',
                backgroundColor: 'var(--color-primary)', color: 'white',
                border: 'none', borderRadius: '4px', cursor: 'pointer',
              }}
              onClick={applyTag}
            >
              Apply
            </button>
            {(search || tag) && (
              <button
                style={{
                  padding: '0.5rem 1rem', fontSize: '0.875rem',
                  backgroundColor: 'transparent', color: 'var(--color-text)',
                  border: '1px solid var(--color-border)', borderRadius: '4px', cursor: 'pointer',
                }}
                onClick={clearFilters}
              >
                Clear
              </button>
            )}
          </div>
        </div>
      </div>

      {agents.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
          <h2 style={{ marginBottom: '0.5rem' }}>No agents found</h2>
          <p style={{ color: 'var(--color-text-muted)' }}>
            {search || tag ? 'Try adjusting your filters' : 'No agents available yet'}
          </p>
        </div>
      ) : (
        <div className="card" style={{ padding: 0 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--color-border)' }}>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600, color: 'var(--color-text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Agent</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600, color: 'var(--color-text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Tags</th>
                <th style={{ padding: '1rem', textAlign: 'left', fontWeight: 600, color: 'var(--color-text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Version</th>
                <th style={{ padding: '1rem', textAlign: 'right', fontWeight: 600, color: 'var(--color-text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {agents.map(agent => {
                const description = agent.description ?? ''
                return (
                  <tr key={agent.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                    <td style={{ padding: '1rem' }}>
                      <Link to={`/agents/${agent.id}`} style={{ textDecoration: 'none' }}>
                        <div style={{ fontWeight: 600, color: 'var(--color-text)' }}>{agent.name}</div>
                        <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginTop: '0.25rem' }}>
                          {description.substring(0, 100)}{description.length > 100 ? '...' : ''}
                        </div>
                      </Link>
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.375rem' }}>
                        {((agent.tags as string[]) || []).map(t => (
                          <span key={t} className="badge badge-secondary" style={{ fontSize: '0.7rem', backgroundColor: 'var(--color-background)', color: 'var(--color-text)' }}>
                            {t}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td style={{ padding: '1rem', fontFamily: 'var(--font-mono)', fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                      v{agent.version}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'right' }}>
                      <Link to={`/agents/${agent.id}`} className="btn btn-outline" style={{ padding: '0.375rem 0.75rem', fontSize: '0.8125rem' }}>
                        View
                      </Link>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
          <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}>
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              style={{
                padding: '0.5rem 1rem', fontSize: '0.875rem',
                backgroundColor: 'transparent', color: 'var(--color-text)',
                border: '1px solid var(--color-border)', borderRadius: '4px', cursor: 'pointer',
              }}
              aria-label="Previous page"
            >
              Previous
            </button>
            {lastPage > 1 && (
              <span style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>
                Page {page} of {lastPage}
              </span>
            )}
            <button
              onClick={() => setPage((p) => Math.min(lastPage, p + 1))}
              disabled={page >= lastPage}
              style={{
                padding: '0.5rem 1rem', fontSize: '0.875rem',
                backgroundColor: 'transparent', color: 'var(--color-text)',
                border: '1px solid var(--color-border)', borderRadius: '4px', cursor: 'pointer',
              }}
              aria-label="Next page"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
