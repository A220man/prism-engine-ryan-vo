export interface TokenData {
  sub?: string
  email?: string
  roles: string[]
  exp?: number
}

export interface User {
  id: string
  email: string
  roles: string[]
}