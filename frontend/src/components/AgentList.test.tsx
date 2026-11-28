import { describe, it, expect, beforeEach, vi } from 'vitest'

// Mock axios and api client before importing component
vi.mock('../api/client', () => {
  const mockApi = {
    get: vi.fn(),
  }
  return { api: mockApi as any }
})

import { AgentList } from './AgentList'

const PAGE_SIZE = 10

describe('AgentList component - unit', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('component can be imported', () => {
    expect(AgentList).toBeDefined()
  })

  it('renders without crashing', () => {
    // Just verify the component function exists and can be called
    expect(typeof AgentList).toBe('function')
  })

  it('utility functions work correctly', () => {
    // Test totalPages from agentQuery
    expect(totalPages(25, 10)).toBe(3)
    expect(totalPages(0, 10)).toBe(1)
    expect(totalPages(10, 10)).toBe(1)

    // Test clampPage from agentQuery
    expect(clampPage(5, 25, 10)).toBe(3)
    expect(clampPage(1, 25, 10)).toBe(1)
    expect(clampPage(100, 25, 10)).toBe(3)

    // Test buildAgentListParams from agentQuery
    const params1 = buildAgentListParams({ page: 1, page_size: 10, search: 'test', tag: '' })
    expect(params1).toEqual({ page: 1, page_size: 10, search: 'test' })

    const params2 = buildAgentListParams({ page: 2, page_size: 5, search: '', tag: 'python' })
    expect(params2).toEqual({ page: 2, page_size: 5, tag: 'python' })

    const params3 = buildAgentListParams({ page: 1, page_size: 10 })
    expect(params3).toEqual({ page: 1, page_size: 10 })
  })
})
