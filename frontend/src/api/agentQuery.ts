// Pure helpers for the agent-list view. Kept free of React/network so the
// backend contract (page, page_size, search, tag) can be unit tested directly.

export interface AgentListParams {
  page: number
  page_size: number
  search?: string
  tag?: string
}

export interface AgentListRequest {
  search: string
  tag: string
  page: number
  pageSize: number
}

/**
 * Map UI state to the query string expected by GET /api/v1/agents.
 * Empty search/tag are omitted so the backend treats them as "no filter"
 * instead of matching an empty string.
 */
export function buildAgentListParams(req: AgentListRequest): AgentListParams {
  const params: AgentListParams = {
    page: Math.max(1, Math.floor(req.page) || 1),
    page_size: Math.max(1, Math.floor(req.pageSize) || 1),
  }
  const search = req.search.trim()
  if (search) params.search = search
  const tag = req.tag.trim()
  if (tag) params.tag = tag
  return params
}

/** Total page count for a given total and page size. Never below 1. */
export function totalPages(total: number, pageSize: number): number {
  if (pageSize <= 0) return 1
  return Math.max(1, Math.ceil(total / pageSize))
}

/** Clamp a requested page into [1, lastPage] for the given total. */
export function clampPage(page: number, total: number, pageSize: number): number {
  const last = totalPages(total, pageSize)
  if (!Number.isFinite(page)) return 1
  return Math.min(Math.max(1, Math.floor(page)), last)
}
